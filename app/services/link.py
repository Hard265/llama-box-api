from uuid import UUID
from sqlalchemy.orm import Session, joinedload

from app.models.link import Link


def get_user_link(db: Session, user_id: UUID, id: UUID):
    link = (
        db.query(Link)
        .options(joinedload(Link.user), joinedload(Link.folder), joinedload(Link.file))
        .filter(Link.user_id == user_id, Link.id == id)
        .first()
    )
    return link


def get_user_links(db: Session, user_id: UUID):
    links = (
        db.query(Link)
        .options(joinedload(Link.user), joinedload(Link.folder), joinedload(Link.file))
        .filter(Link.user_id == user_id, Link.id == id)
        .all()
    )
    return links


def get_link(db: Session, token: str):
    link = db.query(Link).filter(Link.token == token).first()
    return link
