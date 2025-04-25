from datetime import datetime
from typing import (
    Any, Dict, Generic, List, Optional, Type, TypeVar, Union
)

import pendulum
from fastapi import HTTPException
from pydantic import BaseModel, UUID4
from sqlalchemy import or_, desc, select, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from config.logger import log
from db.table import Base
from utils.exceptions.exc_400 import http_400_exc_bad_request
from utils.exceptions.exc_409 import http_409_exc_conflict
from utils.exceptions.exc_500 import http_500_exc_internal_server_error

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseCRUDRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class for CRUD operations on database models.

    Provides common database operations with error handling and type safety.

    Type Parameters:
        ModelType: The SQLAlchemy model type
        CreateSchemaType: Pydantic model for creation operations
        UpdateSchemaType: Pydantic model for update operations
    """

    def __init__(self, model: Type[ModelType], *args, **kwargs):
        """
        Initialize the repository with a specific model.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    async def get_one(self, db: Session, *, silent=False, **filters) -> Optional[ModelType]:
        """
        Retrieve a single record by matching a specific field value.

        example usage: user = get_one(db=db, id=<uuid>)
        """
        try:
            query = db.query(self.model)
            for k, v in filters.items():
                query = query.filter(getattr(self.model, k) == v)

            result = query.first()
            if not result and not silent: raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found"
            )
            return result
        except SQLAlchemyError:
            log.error(f"Database error fetching {self.model.__name__} with id={id}", exc_info=True)
            raise await http_500_exc_internal_server_error()
        except Exception:
            log.exception(f"Error in get_by_field for {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def get_by_id(self, db: Session, *, id: UUID4, silent=False) -> ModelType:
        """
        Retrieve a single record by its ID.
        """
        return await self.get_one(db=db, id=id, silent=silent)

    async def get_many_by_ids(self, db: Session, *, ids: list, silent=False) -> Optional[List[ModelType]]:
        """
        Retrieve multiple records by their IDs.

        Args:
            db: Database session
            ids: List of primary key values
            silent: if false, raise an exception when a record is not found

        Returns:
            List[ModelType]: List of found records

        Raises:
            HTTPException: 400 if any ID is not found
        """
        if not ids: return []
        try:
            found_objects = db.query(self.model).filter(self.model.id.in_(ids)).all()
            missing_ids = set(ids) - {obj.id for obj in found_objects}
            if missing_ids and not silent: raise await http_400_exc_bad_request(
                f"Records not found for ids: {missing_ids}"
            )
            return found_objects
        except HTTPException:
            raise
        except:
            log.exception(f"Error in get_many_by_ids for {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def get_all(
            self, *,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            time_range_min: datetime = None,
            time_range_max: datetime = None,
            is_deleted: bool = None
    ) -> List[ModelType]:
        """
        Retrieve all records with pagination and ordering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by. Prefix with a hyphen ('-') to sort descending
            time_range_min: Get records after this time
            time_range_max: Get records before this time
            is_deleted: Get records that have been marked as deleted or not

        Returns:
            List[ModelType]: List of records
        """
        query = db.query(self.model)
        try:
            if is_deleted is not None: query = query.filter(self.model.deleted_at.isnot(None) == is_deleted)
            if time_range_min: query = query.filter(self.model.created_at >= time_range_min)
            if time_range_max: query = query.filter(self.model.created_at <= time_range_max)

            query = await self._get_ordering(query=query, order_by=order_by)
            results = query.offset(skip).limit(limit).all()
            return results
        except HTTPException:
            raise
        except SQLAlchemyError:
            log.error(f"Database error in get_all for {self.model.__name__}", exc_info=True)
            return []
        except:
            log.exception(f"Unexpected error in get_all {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def get_by_filters(
            self, *,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            **filters: Any
    ) -> List[ModelType]:
        """
        Retrieve records matching exact filter conditions.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by. Prefix with a hyphen ('-') to sort descending

            **filters: Field-value pairs to filter by

        Returns:
            List[ModelType]: List of matching records
        """
        query = db.query(self.model)
        try:
            for field, value in filters.items():
                if value is not None: query = query.filter(getattr(self.model, field) == value)

            query = await self._get_ordering(query=query, order_by=order_by)
            results = query.offset(skip).limit(limit).all()
            return results

        except HTTPException:
            raise
        except AttributeError:
            log.error(f"Invalid filter field")
            raise await http_400_exc_bad_request(f'Invalid filter field provided for {self.model.__name__}')
        except:
            log.exception(f"Error in get_by_filters for {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def get_by_pattern(
            self, *,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            **patterns: Any
    ) -> List[ModelType]:
        """
        Retrieve records matching pattern-based (ILIKE) filter conditions.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by. Prefix with a hyphen ('-') to sort descending
            **patterns: Field-pattern pairs to filter by

        Returns:
            List[ModelType]: List of matching records
        """
        query = db.query(self.model)
        try:
            for field, pattern in patterns.items():
                if not pattern: continue

                field_attr = getattr(self.model, field)
                if isinstance(pattern, list):

                    valid_patterns = [p.strip() for p in pattern if p]
                    if not valid_patterns: continue

                    query = query.filter(or_(*[field_attr.ilike(f"%{p}%") for p in valid_patterns]))

                else:
                    query = query.filter(field_attr.ilike(f"%{pattern}%"))

            query = await self._get_ordering(query=query, order_by=order_by)
            result = query.offset(skip).limit(limit).all()
            return result

        except HTTPException:
            raise
        except AttributeError as e:
            log.error(f"Invalid pattern matching field", exc_info=True)
            raise await http_400_exc_bad_request(f'Invalid field for pattern matching: {str(e)}')
        except:
            log.exception(f"Error in get_by_pattern for {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def get_or_create(
            self, *,
            db: Session,
            data: CreateSchemaType,
            unique_field: str,
    ) -> ModelType:
        """
        Get an existing record by a unique field or create a new one.

        Args:
            db: Database session
            data: Creation data
            unique_field: Field to check for existing record

        Returns:
            ModelType: Existing or newly created record
        """
        try:
            if existing_obj := await self.get_one(db=db, **{unique_field: getattr(data, unique_field)}):
                return existing_obj

            return await self.create(db=db, data=data)
        except:
            log.exception(f"Error in get_or_create for {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def create(self, *, db: Session, data: CreateSchemaType, created_by_id: Optional[UUID4] = None) -> ModelType:
        """
        Create a new record.

        Args:
            db: Database session
            data: Creation data
            created_by_id: Id of the user creating the record

        Returns:
            ModelType: Created record

        Raises:
            HTTPException: 409 on unique constraint violation
        """
        if not data: raise await http_400_exc_bad_request("No data provided for creation")
        try:
            model_data = data.model_dump(exclude_none=True, exclude_defaults=False)
            db_obj = self.model(**model_data)
            if created_by_id and hasattr(db_obj, 'created_by_id'):
                db_obj.created_by_id = created_by_id

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)

            return db_obj
        except IntegrityError as e:
            db.rollback()
            log.error(f"Integrity error creating {self.model.__name__}", exc_info=True)
            raise await http_409_exc_conflict(self._format_integrity_error(e))
        except:
            db.rollback()
            log.exception(f"Error creating {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def update(
            self, *,
            db: Session,
            db_obj: ModelType,
            data: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record.

        Args:
            db: Database session
            db_obj: Existing record to update
            data: Update data (Pydantic model or dict)

        Returns:
            ModelType: Updated record
        """
        try:
            update_data = data.model_dump(exclude_none=True) if isinstance(data, BaseModel) else data
            for field, value in update_data.items():
                setattr(db_obj, field, value)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)

            return db_obj
        except:
            db.rollback()
            log.exception(f"Error updating {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def delete(
            self, *,
            db: Session,
            id: Optional[UUID4] = None,
            db_obj: Optional[ModelType] = None,
            soft: bool = False
    ) -> None:
        """
        Delete a record by ID or pass in the object to be deleted.

        Args:
            db: Database session
            id: Record ID to delete
            db_obj: Object to delete
            soft: mark as deleted if true

        Raises:
            HTTPException: 404 if not found, 409 if deletion violates constraints
        """
        # Check existence
        if not id and not db_obj: raise ValueError(
            "Provide either id or the db object to delete"
        )
        if not db_obj: db_obj = await self.get_by_id(db=db, id=id, silent=False)
        try:
            if soft:
                db_obj.deleted_at = pendulum.now()
                if hasattr(db_obj, "is_active"):
                    db_obj.is_active = False

                # Mark the object as changed
                db.add(db_obj)
                db.commit()
            else:
                # Perform hard deletion
                db.delete(db_obj)
                db.commit()
        except IntegrityError:
            db.rollback()
            log.error(f"Integrity error deleting {self.model.__name__}", exc_info=True)
        except:
            log.exception(f"Error deleting {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def bulk_hard_delete(self, db: Session, *, ids: List[UUID4]) -> None:
        """
        Delete multiple records by ID.

        Args:
            db: Database session
            ids: List of record IDs to delete

        Raises:
            HTTPException: 404 if not found, 409 if deletion violates constraints
        """
        if not ids: return
        try:
            result = db.execute(delete(self.model).where(self.model.id.in_(ids)))
            db.commit()

            # Check if all rows were deleted
            if result.rowcount != len(ids): log.warning(
                f"Requested to delete {len(ids)} records, but only {result.rowcount} were deleted"
            )

        except HTTPException:
            db.rollback()
            log.exception("failed to delete")
            raise
        except IntegrityError:
            db.rollback()
            log.error(f"Integrity error during bulk delete of {self.model.__name__}", exc_info=True)
            raise await http_409_exc_conflict(
                f"Cannot delete some {self.model.__name__} records due to constraints"
            )
        except Exception:
            db.rollback()
            log.exception(f"Error during bulk delete of {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def _validate_unique_fields(self, db: Session, *, model_data: dict, unique_fields: List, id: UUID4 = None):
        for field in unique_fields:
            if field in model_data and model_data[field]:
                query = select(self.model).where(getattr(self.model, field) == model_data[field])

                if id:
                    if not isinstance(id, UUID4): raise await http_400_exc_bad_request(
                        "Invalid UUID format for ID"
                    )
                    query = query.where(self.model.id != id)

                result = db.execute(query)
                if result.scalars().first(): raise await http_400_exc_bad_request(
                    f"'{field}' for {model_data[field]} already exists"
                )

    async def _get_ordering(self, query, order_by: List[str]):
        if not order_by: return query.order_by(desc(self.model.created_at))

        _ordering_fields = []
        try:
            for field in order_by:
                desc_order = False
                if field.startswith('-'):
                    field = field[1:]
                    desc_order = True

                order_column = getattr(self.model, field)
                ordering = desc(order_column) if desc_order else order_column
                _ordering_fields.append(ordering)

            return query.order_by(*_ordering_fields)
        except AttributeError:
            raise await http_409_exc_conflict(f'Invalid key given to order_by: {order_by}')

    @staticmethod
    def _format_integrity_error(e: IntegrityError) -> str:
        """Prettifies SQLAlchemy IntegrityError messages."""
        error_message = str(e.orig)

        if isinstance(e.orig, Exception):
            if "ForeignKeyViolationError" in error_message:
                start = error_message.find("Key (")
                if start != -1:
                    detail = error_message[start:].replace("DETAIL: ", "").strip()
                    return f"Foreign key constraint violated: {detail}"
                return "Foreign key constraint violated."
            elif "UniqueViolationError" in error_message:
                return "Unique constraint violated. A similar record already exists."

        return str(e.orig)
