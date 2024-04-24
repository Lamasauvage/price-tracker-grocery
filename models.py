from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String, nullable=True)
    prices = relationship("Price", order_by="Price.id", back_populates="product", cascade="delete, delete-orphan")


class Price(Base):
    __tablename__ = 'prices'
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    price = Column(Float)
    date = Column(Date, default=datetime.date.today)
    store = Column(String)
    product = relationship("Product", back_populates="prices")


Product.prices = relationship("Price", order_by=Price.id, back_populates="product")


class GroceryShopping(Base):
    __tablename__ = 'grocery_shopping'
    id = Column(Integer, primary_key=True, index=True)
    total_price = Column(Float)
    date = Column(Date, default=datetime.date.today)
    store = Column(String)