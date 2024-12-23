from sqlalchemy.orm import relationship

from database import Base

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey


class Cat(Base):
    __tablename__ = "cats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    years_of_experience = Column(Integer, nullable=False, default=1)
    breed = Column(String, nullable=False)
    salary = Column(Float, nullable=False, default=1.0)


class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    notes = Column(String)

    complete = Column(Boolean, default=False)

    mission = relationship("Mission", back_populates="targets")


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    cat_id = Column(Integer, ForeignKey("cats.id"), nullable=True)
    complete = Column(Boolean, default=False)

    targets = relationship("Target", back_populates="mission")
