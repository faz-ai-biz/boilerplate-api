from sqlalchemy import Column, Integer, String

from src.db.models import Base


class ExampleModel(Base):
    __tablename__ = "example"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
