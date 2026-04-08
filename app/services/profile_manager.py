from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserUpdate


def get_user_by_id(user_id: int, db: Session) -> User:
    """Fetch a user by primary key."""
    return db.query(User).filter(User.id == user_id).first()


def update_profile(user: User, update_data: UserUpdate, db: Session) -> User:
    """Apply partial profile update to the authenticated user and persist."""
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
