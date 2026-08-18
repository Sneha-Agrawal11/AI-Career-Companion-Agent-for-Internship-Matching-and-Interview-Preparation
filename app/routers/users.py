from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

from app.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile")
def get_profile(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role,
    }


@router.put("/profile")
def update_profile(
    full_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    current_user.full_name = full_name

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully",
        "user": current_user
    }

@router.delete("/delete")
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    db.delete(current_user)
    db.commit()

    return {
        "message": "User account deleted successfully"
    }