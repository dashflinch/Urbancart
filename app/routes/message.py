from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.message import Message
from app.schemas.message import (MessageCreate,MessageResponse)
from app.utils.dependencies import get_current_user
from sqlalchemy import or_



router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)




@router.post(
    "",
    response_model=MessageResponse
)
def send_message(
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    receiver = db.query(User).filter(
        User.id == data.receiver_id
    ).first()

    if not receiver:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    new_message = Message(
        sender_id=current_user.id,
        receiver_id=data.receiver_id,
        message=data.message
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message





@router.get("/conversations")
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    conversations = (
        db.query(Message)
        .filter(
            or_(
                Message.sender_id == current_user.id,
                Message.receiver_id == current_user.id,
            )
        )
        .order_by(Message.created_at.desc())
        .all()
    )

    result = []
    users_seen = set()

    for msg in conversations:

        other_user_id = (
            msg.receiver_id
            if msg.sender_id == current_user.id
            else msg.sender_id
        )

        if other_user_id in users_seen:
            continue

        users_seen.add(other_user_id)

        other_user = db.query(User).filter(
            User.id == other_user_id
        ).first()

        result.append({
            "id": other_user.id,
            "name": other_user.full_name,
            "last_message": msg.message,
        })
    return result




@router.get(
    "/{user_id}",
    response_model=list[MessageResponse]
)
def get_messages(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    messages = db.query(Message).filter(
        (
            (Message.sender_id == current_user.id) &
            (Message.receiver_id == user_id)
        ) |
        (
            (Message.sender_id == user_id) &
            (Message.receiver_id == current_user.id)
        )
    ).order_by(
        Message.created_at.asc()
    ).all()
    return messages
