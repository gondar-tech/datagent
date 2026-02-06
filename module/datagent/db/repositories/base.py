from typing import Generic, TypeVar, List, Optional, Type
from sqlalchemy.orm import Session
from ..models.base import Base

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model_cls: Type[T]):
        self.session = session
        self.model_cls = model_cls

    def get(self, id: str) -> Optional[T]:
        return self.session.query(self.model_cls).filter(self.model_cls.id == id).first()

    def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        return self.session.query(self.model_cls).offset(skip).limit(limit).all()

    def create(self, obj: T) -> T:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj
