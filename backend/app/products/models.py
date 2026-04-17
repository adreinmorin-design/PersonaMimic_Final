import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database.database import Base


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    niche = Column(String)
    status = Column(String)  # 'building', 'validated', 'packaged', 'published'
    path = Column(String)  # filesystem path to zip
    url = Column(String)  # Published URL
    adversary_score = Column(Integer)  # Quality score 0-100
    whop_product_id = Column(String)  # Whop internal product ID
    whop_plan_id = Column(String)  # Whop internal plan ID
    description = Column(String)
    price = Column(Integer, default=0)  # Price in cents or USD whole units
    category = Column(String)  # e.g. 'Software', 'Information', 'Service'
    sales_count = Column(Integer, default=0)
    total_revenue = Column(Integer, default=0)  # Total USD revenue
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
