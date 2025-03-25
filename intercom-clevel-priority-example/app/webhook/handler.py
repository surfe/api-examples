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
    return {}

@router.post("/intercom")
async def handle_webhook(
    request: Request,
    x_hub_signature: Optional[str] = Header(None)
):
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

        admin_id = data.get("item", {}).get("source", {}).get("author", {}).get("id")
        if data.get("item", {}).get("source", {}).get("author", {}).get("type") != "admin":
            admin_id = None
        if not admin_id:
            raise HTTPException(
                status_code=400,
                detail="Missing required admin_id"
            )

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
            await intercom.add_conversation_tag(conversation_id, admin_id)
            print(f"Added priority tag to conversation {conversation_id}")
        
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