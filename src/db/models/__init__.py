from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import declarative_base

# Create the declarative base
Base: DeclarativeMeta = declarative_base()

from .example_model import ExampleModel  # noqa: F401

# Import all models here to ensure they are registered with SQLAlchemy
from .user import User  # noqa: F401
