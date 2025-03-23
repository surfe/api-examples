from fastapi import APIRouter, Request, HTTPException, Header # type: ignore
from typing import Optional
from app.config import WEBHOOK_SECRET
from app.services.surfe import SurfeService
from app.services.intercom import IntercomService

router = APIRouter()
intercom = IntercomService() 
surfe = SurfeService()

@router.head("/intercom")
async def handle_webhook_validation():
    print("Webhook validation request received")
    return {}

@router.post("/intercom")
async def handle_webhook(
    request: Request,
    x_hub_signature: Optional[str] = Header(None)
):
    print("Webhook request received")
    body = await request.body()
    
    if not x_hub_signature or not intercom.verify_webhook_signature(
        WEBHOOK_SECRET,
        x_hub_signature,
        body
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature"
        )
    
    try:
        payload = await request.json()
        
        topic = payload.get("topic")

        if topic != "conversation.user.created":
            return {"status": "ignored", "reason": "irrelevant topic"}
        
        data = payload.get("data", {})

        conversation_id = data.get("item", {}).get("id")

        contact_id = data.get("item", {}).get("contacts", {}).get("contacts", [{}])[0].get("id")

        contact_details_intercom = intercom.get_contact_details(contact_id)
        
        contact_email = contact_details_intercom.get("email", {})
        
        if not all([conversation_id, contact_email]):
            raise HTTPException(
                status_code=400,
                detail="Missing required conversation data"
            )
            
        contact_details_surfe = await surfe.get_contact_details_by_email(contact_email)
        is_c_level = any(seniority.lower() == 'c-level' for seniority in contact_details_surfe.get("person", {}).get("seniorities", [])) or any(department.lower() == 'c suite' for department in contact_details_surfe.get("person", {}).get("departments", []))
        if is_c_level:
            # TODO: replace this logic since it's not feasible
            # await intercom.update_conversation_priority(conversation_id, "priority")
            print(f"Conversation Priority Updated: {conversation_id}")
        
        return {
            "status": "success",
            "conversation_id": conversation_id,
            "contact_email": contact_email,
            "is_c_level": is_c_level,
            "priority_updated": is_c_level
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    


    # Contact Enrichment: {'person': {'id': '08bf0123-1558-438c-85cc-001841028037', 'firstName': 'Omar', 'lastName': 'Ismail', 'name': 'Omar Ismail', 'jobTitle': 'Co-Founder & CEO', 'companyName': 'Temple', 'companyWebsite': 'http://www.temple.fans', 'linkedinUrl': 'http://www.linkedin.com/in/omarismailb', 'country': 'United Kingdom', 'seniorities': ['Founder'], 'departments': ['C Suite'], 'subdepartments': ['Executive']}}
    # Contact Enrichment: {'person': {'id': '51c1a43c-5a07-4c37-9988-5196da882527', 'firstName': 'Sam', 'lastName': 'Millar', 'name': 'Sam Millar', 'jobTitle': 'Cofounder & CTO', 'companyName': 'Temple', 'companyWebsite': 'http://www.temple.fans', 'linkedinUrl': 'http://www.linkedin.com/in/millr', 'country': 'United Kingdom', 'seniorities': ['Founder'], 'departments': ['C Suite'], 'subdepartments': ['Founder']}}
    #Contact Enrichment: {'person': {'id': '7ccbce81-4888-4a61-af49-57223b92f151', 'firstName': 'Lloyd', 'lastName': 'Rayner', 'name': 'Lloyd Rayner', 'jobTitle': 'Chief Revenue Officer (CRO)', 'companyName': 'Surfe', 'companyWebsite': 'http://www.surfe.com', 'linkedinUrl': 'http://www.linkedin.com/in/lloyd-rayner', 'country': 'United Kingdom', 'seniorities': ['C_suite'], 'departments': ['C Suite'], 'subdepartments': ['Sales Executive']}}