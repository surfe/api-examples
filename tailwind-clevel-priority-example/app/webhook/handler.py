from fastapi import APIRouter, Request, HTTPException, Header # type: ignore
from typing import Optional
from app.config import WEBHOOK_SECRET
from app.services import intercom, surfe

router = APIRouter()

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

        print(f"Topic: {topic}")
        if topic != "conversation.user.created":
            return {"status": "ignored", "reason": "irrelevant topic"}
        
        #TODO: test the structure of the data object with a live webhook test
        data = payload.get("data", {})
        conversation_id = data.get("item", {}).get("id")
        contact_email = data.get("item", {}).get("user", {}).get("email")
        
        if not all([conversation_id, contact_email]):
            raise HTTPException(
                status_code=400,
                detail="Missing required conversation data"
            )
            
        # Call Surfe API to enrich the contact
        contact_enrichment = await surfe.enrich_contact(contact_email)
        # Check if they're C-level, would be in an array called seniorities, as 'C-Level'
        is_c_level = any(seniority.lower() == 'c-level' for seniority in contact_enrichment.get("seniorities", []))
        # Update the conversation priority if needed
        if is_c_level:
            await intercom.update_conversation_priority(conversation_id, "priority")
        
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
    

