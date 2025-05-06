from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base

from services.db import SessionLocal

Base = declarative_base()


class CRUDMixin:
    @classmethod
    def create(cls, **fields):
        try:
            with SessionLocal() as db:
                new_entity = cls(**fields)
                db.add(new_entity)
                db.commit()
                db.refresh(new_entity)

                return new_entity

        except SQLAlchemyError as e:
            raise ValueError(f"Failed to create {cls.__str__}: {str(e)}")

    @classmethod
    def find(cls, limit=25, offset=0, **filters):
        try:
            with SessionLocal() as db:
                query = db.query(cls)
                entities = query

                if filters:
                    conditions = [getattr(cls, field_name) == value for field_name, value in filters.items()]
                    entities = entities.filter(*conditions)

                entities = entities.limit(limit).offset(offset).all()

                total_count = query.count()

                return entities, total_count

        except SQLAlchemyError as e:
            raise ValueError(f"Failed to find {cls.__str__}: {str(e)}")

    @classmethod
    def find_one(cls, **filters):
        try:
            with SessionLocal() as db:
                conditions = [getattr(cls, field_name) == value for field_name, value in filters.items()]

                entity = db.query(cls).filter(*conditions).first()

                return entity

        except SQLAlchemyError as e:
            raise ValueError(f"Failed to find {cls.__str__}: {str(e)}")

    @classmethod
    def update(cls, id, **fields):
        try:
            with SessionLocal() as db:
                entity = db.query(cls).filter(getattr(cls, "id") == id).first()

                for field_name, value in fields.items():
                    setattr(entity, field_name, value)

                db.commit()
                db.refresh(entity)

                return entity

        except SQLAlchemyError as e:
            raise ValueError(f"Failed to find {cls.__str__}: {str(e)}")

    @classmethod
    def delete(cls, id):
        try:
            with SessionLocal() as db:
                entity = db.query(cls).filter(getattr(cls, "id") == id).first()

                db.delete(entity)
                db.commit()

                return entity

        except SQLAlchemyError as e:
            raise ValueError(f"Failed to delete {cls.__str__}: {str(e)}")
