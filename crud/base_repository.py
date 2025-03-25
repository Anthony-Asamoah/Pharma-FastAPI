from typing import (
    Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Literal
)

import pendulum
from fastapi import HTTPException
from pydantic import BaseModel, UUID4
from sqlalchemy import or_, desc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, NoResultFound
from sqlalchemy.orm import Session
from starlette import status
from starlette.status import HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST

from config.logger import log
from db.table import Base
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

    async def get_by_id(
            self, db: Session, *,
            id: Any,
            silent: bool = False,
    ) -> Optional[ModelType]:
        """
        Retrieve a single record by its ID.

        Args:
            db: Database session
            id: Primary key value
            silent: If True, return None instead of raising 404 when not found

        Returns:
            Optional[ModelType]: Found record or None if silent=True

        Raises:
            HTTPException: 404 if record not found and silent=False
        """
        if id is None: return None
        try:
            result = db.query(self.model).filter(self.model.id == id).first()
            return result
        except NoResultFound:
            if silent: return None
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found"
            )
        except SQLAlchemyError:
            log.error(f"Database error fetching {self.model.__name__} with id={id}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"{self.model.__name__} not found"
            )
        except:
            log.exception(f"Unexpected error fetching {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def get_by_field(self, *, db: Session, field: str, value: Any, silent=True) -> Optional[ModelType]:
        """
        Retrieve a single record by matching a specific field value.

        Args:
            db: Database session
            field: Model field name
            value: Value to match

        Returns:
            Optional[ModelType]: Found record or None

        Raises:
            HTTPException: 400 if field is invalid
        """
        if value is None: return None
        try:
            result = db.query(self.model).filter(getattr(self.model, field) == value).first()
            if not result and not silent: raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"{self.model.__name__} not found"
            )
            return result
        except AttributeError:
            log.error(f"Invalid field {field} for model {self.model.__name__}", exc_info=True)
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail=f'Invalid field: {field}'
            )
        except:
            log.exception(f"Error in get_by_field for {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def get_many_by_ids(self, *, db: Session, ids: List[Any]) -> List[ModelType]:
        """
        Retrieve multiple records by their IDs.

        Args:
            db: Database session
            ids: List of primary key values

        Returns:
            List[ModelType]: List of found records

        Raises:
            HTTPException: 400 if any ID is not found
        """
        if not ids: return []
        try:
            results = db.query(self.model).filter(self.model.id.in_(ids)).all()
            missing_ids = set(ids) - {obj.id for obj in results}
            if missing_ids: raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Records not found for {len(missing_ids)} objs with id: {missing_ids}"
            )
            return results
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
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc'
    ) -> List[ModelType]:
        """
        Retrieve all records with pagination and ordering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            order_direction: Sort direction ('asc' or 'desc')

        Returns:
            List[ModelType]: List of records
        """
        query = db.query(self.model)
        try:
            if order_by:
                try:
                    order_column = getattr(self.model, order_by)
                except AttributeError:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=f'Invalid key given to order_by: {order_by}'
                    )
                query = query.order_by(
                    order_column.desc() if order_direction == 'desc' else order_column.asc()
                )
            else:
                query = query.order_by(desc(self.model.created_at))

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
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **filters: Any
    ) -> List[ModelType]:
        """
        Retrieve records matching exact filter conditions.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            order_direction: Sort direction ('asc' or 'desc')
            **filters: Field-value pairs to filter by

        Returns:
            List[ModelType]: List of matching records
        """
        query = db.query(self.model)
        try:
            # Apply filters
            for field, value in filters.items():
                if value is not None: query = query.filter(getattr(self.model, field) == value)

            # Apply ordering
            if order_by:
                try:
                    order_column = getattr(self.model, order_by)
                except AttributeError:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=f'Invalid key given to order_by: {order_by}'
                    )
                query = query.order_by(
                    order_column.desc() if order_direction == 'desc' else order_column.asc()
                )

            results = query.offset(skip).limit(limit).all()
            return results

        except HTTPException:
            raise
        except AttributeError as e:
            log.error(f"Invalid filter field", )
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=f'Invalid filter field provided for {self.model.__name__}'
            )
        except:
            log.exception(f"Error in get_by_filters for {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def get_by_pattern(
            self, *,
            db: Session,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            order_direction: Literal['asc', 'desc'] = 'asc',
            **patterns: Any
    ) -> List[ModelType]:
        """
        Retrieve records matching pattern-based (ILIKE) filter conditions.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field to order by
            order_direction: Sort direction ('asc' or 'desc')
            **patterns: Field-pattern pairs to filter by

        Returns:
            List[ModelType]: List of matching records
        """
        query = db.query(self.model)
        try:
            # Apply pattern matching filters
            for field, pattern in patterns.items():
                if not pattern: continue

                field_attr = getattr(self.model, field)
                if isinstance(pattern, list):
                    valid_patterns = [p for p in pattern if p]
                    if valid_patterns:
                        query = query.filter(or_(*[field_attr.ilike(f"%{p}%") for p in valid_patterns]))
                    else:  # todo test without else clause
                        continue
                else:
                    query = query.filter(field_attr.ilike(f"%{pattern}%"))

            # Apply ordering
            if order_by:
                try:
                    order_column = getattr(self.model, order_by)
                except AttributeError:
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=f'Invalid key given to order_by: {order_by}'
                    )
                query = query.order_by(
                    order_column.desc() if order_direction == 'desc' else order_column.asc()
                )

            results = query.offset(skip).limit(limit).all()
            return results

        except HTTPException:
            raise
        except AttributeError as e:
            log.error(f"Invalid pattern matching field", exc_info=True)
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail=f'Invalid field for pattern matching: {str(e)}'
            )
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
            # Try to get existing record
            if existing_obj := await self.get_by_field(db=db, field=unique_field, value=getattr(data, unique_field)):
                return existing_obj
            # Create new record if not found
            return await self.create(db=db, data=data)
        except:
            log.exception(f"Error in get_or_create for {self.model.__name__}")
            raise await http_500_exc_internal_server_error()

    async def create(self, *, db: Session, data: CreateSchemaType) -> ModelType:
        """
        Create a new record.

        Args:
            db: Database session
            data: Creation data

        Returns:
            ModelType: Created record

        Raises:
            HTTPException: 409 on unique constraint violation
        """
        if not data: raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="No data provided for creation"
        )

        try:
            model_data = data.model_dump(exclude_none=True, exclude_defaults=False)
            db_obj = self.model(**model_data)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)

            return db_obj
        except IntegrityError as e:
            db.rollback()
            log.error(f"Integrity error creating {self.model.__name__}", exc_info=True)
            raise HTTPException(status_code=HTTP_409_CONFLICT, detail=self._format_integrity_error(e))
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
            self, *, db: Session, id: Optional[UUID4] = None, db_obj: Optional[ModelType] = None, soft: bool=False
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

    @staticmethod
    def _format_integrity_error(e: IntegrityError) -> str:
        """Prettifies SQLAlchemy IntegrityError messages."""
        error_message = str(e.orig)

        if isinstance(e.orig, Exception):
            if "ForeignKeyViolationError" in error_message:
                start = error_message.get("Key (")
                if start != -1:
                    detail = error_message[start:].replace("DETAIL: ", "").strip()
                    return f"Foreign key constraint violated: {detail}"
                return "Foreign key constraint violated."
            elif "UniqueViolationError" in error_message:
                return "Unique constraint violated. A similar record already exists."

        return str(e.orig)
