import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.database import Base


class TaskQueue(Base):
    __tablename__ = "task_queue"
    id = Column(Integer, primary_key=True, index=True)
    brain_name = Column(String, index=True)
    task_type = Column(String, index=True)
    payload = Column(Text)  # JSON blob
    status = Column(String, default="pending", index=True)  # pending, running, completed, failed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ReviewPool(Base):
    __tablename__ = "review_pool"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    reviewer_brain = Column(String, index=True)
    status = Column(String, index=True)  # 'approved', 'rejected', 'correction_needed'
    critique = Column(Text)
    iteration = Column(Integer, default=1)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class TaskBoard(Base):
    __tablename__ = "task_board"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    task_description = Column(String)
    assigned_brain = Column(String, index=True)  # Dre, Fenko, Codesmith
    status = Column(String, default="todo", index=True)  # todo, in_progress, review, done
    priority = Column(Integer, default=1)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)


class UsageQuota(Base):
    __tablename__ = "usage_quotas"
    id = Column(Integer, primary_key=True, index=True)
    brain_name = Column(String, index=True)
    day = Column(String, index=True)  # YYYY-MM-DD
    tokens_consumed = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    last_updated = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
