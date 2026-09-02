"""Example CRUD router; mounted under the ingress prefix in app/main.py."""

from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Item
from ..schemas import ItemCreate, ItemRead

router = APIRouter(prefix="/items", tags=["items"])
SessionDep = Annotated[Session, Depends(get_db)]


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: SessionDep) -> Item:
    item = Item(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("", response_model=list[ItemRead])
def list_items(db: SessionDep) -> Sequence[Item]:
    return db.scalars(select(Item).order_by(Item.id)).all()


@router.get("/{item_id}", response_model=ItemRead)
def read_item(item_id: int, db: SessionDep) -> Item:
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "item not found")
    return item
