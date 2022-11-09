from sqlalchemy import Column, Integer


class SQLAlchemyRepository:
    """ Base class for SQLAlchemy repositories """
    id: int = Column(Integer, primary_key=True, index=True)
