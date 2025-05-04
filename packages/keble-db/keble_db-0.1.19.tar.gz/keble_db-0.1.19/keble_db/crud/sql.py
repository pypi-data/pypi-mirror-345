from typing import Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm.session import Session as SaSession
from sqlmodel import Session, select

from ..schemas import QueryBase, Uuid
from .sql_util import parse_query_for_first, parse_query_for_list

ModelType = TypeVar("ModelType", bound=BaseModel)

SqlIdType = str | None | Uuid | UUID


class SqlCRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], table_name: str):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD) in SQL

        **Parameters**
        * `model`: A SQLAlchemy model class
        """
        self.model = model
        self.model.__table__.name = table_name  # type: ignore
        self.model.__tablename__ = table_name  # type: ignore
        self.table_name = table_name

    def first(
        self, s: Session | SaSession, query: Optional[QueryBase] = None
    ) -> Optional[ModelType]:
        parsed = parse_query_for_first(self.model, query=query)
        if query is not None:
            sel = select(self.model).order_by(query.order_by)
        else:
            sel = select(self.model)
        statement = sel.limit(1)  # only the first one
        if parsed.where is not None:
            statement = statement.where(parsed.where)
        results = s.exec(statement)  # type: ignore
        return results.one_or_none()

    def get_multi(
        self, s: Session | SaSession, *, query: QueryBase | dict | None
    ) -> List[ModelType]:
        if isinstance(query, dict):
            query = QueryBase(**query)
        # assert query.offset is not None and query.limit is not None, '[Db] offset and limit is require for listing query'
        parsed = parse_query_for_list(self.model, query=query)
        statement = select(self.model)
        if query is not None and query.order_by is not None:
            statement = statement.order_by(query.order_by)
        if query is not None and query.limit is not None:
            statement = statement.limit(query.limit)
        if query is not None and query.offset is not None:
            assert isinstance(query.offset, int), (
                f"[Db] Expected int or None type offset in sql query, but got {query.offset}"
            )
            statement = statement.offset(query.offset)
        if parsed.where is not None:
            statement = statement.where(parsed.where)
        results = s.exec(statement)  # type: ignore
        return list(results.all())

    def count(self, s: Session | SaSession, query: Optional[QueryBase] = None) -> int:
        parsed = parse_query_for_list(self.model, query=query)
        statement = select(func.count(self.model.id))  # type: ignore # only the first one
        if parsed.where is not None:
            statement = statement.where(parsed.where)
        count = s.exec(statement).one()  # type: ignore
        return count

    def create(self, s: Session | SaSession, *, obj_in: ModelType):
        obj_in = self.pre_commit_create(s, obj_in=obj_in)
        s.commit()
        s.refresh(obj_in)
        return obj_in

    def pre_commit_create(self, s: Session | SaSession, *, obj_in: ModelType):
        s.add(obj_in)
        return obj_in

    def create_multi(self, s: Session | SaSession, *, obj_in_list: List[ModelType]):
        if len(obj_in_list) == 0:
            return []
        for obj_in in obj_in_list:
            s.add(obj_in)
        s.commit()
        for obj_in in obj_in_list:
            s.refresh(obj_in)
        return obj_in_list

    def update(
        self, s: Session | SaSession, *, _id: SqlIdType, obj_in: dict
    ) -> ModelType:
        obj = self.pre_commit_update(s, _id=_id, obj_in=obj_in)
        s.commit()
        s.refresh(obj)
        return obj

    def pre_commit_update(
        self,
        s: Session | SaSession,
        *,
        _id: SqlIdType,
        obj_in: dict,
    ) -> ModelType:
        if not isinstance(obj_in, dict):
            # try to convert to dict from pydantic object
            assert hasattr(obj_in, "model_dump") and callable(obj_in.model_dump), (
                f"[Db] Expected dict or pydantic object, but got type: {type(obj_in)}"
            )
            obj_in = obj_in.model_dump(exclude={"id", "created"})

        obj = self.first_by_id(s, _id=_id)
        if obj is None:
            raise ValueError("Failed to update due to object not found")
        for k, v in obj_in.items():
            # print("k, v ", k, v)
            # eval(f"obj.{k}=v")
            if hasattr(obj, k):
                setattr(obj, k, v)
            # setattr(obj, k, v)
        s.add(obj)
        return obj

    def delete(
        self,
        s: Session | SaSession,
        *,
        _id: SqlIdType,
    ):
        obj = self.first_by_id(s, _id=_id)
        if obj is None:
            return None
        s.delete(obj)
        s.commit()

    def delete_multi(
        self, s: Session | SaSession, *, obj_in_list: List[Union[str, ModelType]]
    ):
        if len(obj_in_list) == 0:
            return
        ids = [item for item in obj_in_list if isinstance(item, str)]
        objects = [item for item in obj_in_list if not isinstance(item, str)]

        if len(objects) > 0:
            for obj in objects:
                s.delete(obj)
            s.commit()
        for _id in ids:
            self.delete(s, _id=_id)

    def first_by_id(
        self, s: Session | SaSession, *, _id: SqlIdType
    ) -> Optional[ModelType]:
        if _id is None:
            raise ValueError("[Db] _id can not be None")
        return self.first(s, query=QueryBase(id=str(_id)))
