from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth import verify_token, oauth2_scheme


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    email = verify_token(token)

    user = db.query(User).filter(User.email == email).first()

    return user