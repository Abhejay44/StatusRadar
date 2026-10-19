from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.service import Service


def create_service(
    db: Session,
    name: str,
    url: str,
    is_active: bool = True,
) -> Service:
    service = Service(
        name=name,
        url=url,
        is_active=is_active,
    )

    db.add(service)

    try:
        db.commit()
        db.refresh(service)
    except SQLAlchemyError:
        db.rollback()
        raise

    return service


def list_services(db: Session) -> list[Service]:
    statement = select(Service).order_by(Service.id)
    return list(db.scalars(statement).all())
