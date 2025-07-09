import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, DateTime, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from enum import Enum

from db.session import Base


Base = declarative_base(cls=AsyncAttrs)


class UnitType(str, Enum):
    PCS = "бр"
    KG = "кг"
    G = "г"
    LITER = "л"
    ML = "мл"

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nsi_id = Column(String, nullable=False)
    name = Column(String, nullable=False)

    products = relationship("Product", back_populates="category_rel")


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    glovo_id = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    grosery_store = Column(String, nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)

    snapshots = relationship("PriceSnapshot", back_populates="product", cascade="all, delete")
    category_rel = relationship("Category", back_populates="products")


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    price_regular = Column(Float, nullable=False)
    price_promo = Column(Float, nullable=True)
    price_displayed = Column(Float, nullable=False)

    unit_type = Column(String, nullable=True)
    unit_quantity = Column(Float, nullable=True)
    unit_price_normalized = Column(Float, nullable=True)

    product = relationship("Product", back_populates="snapshots")