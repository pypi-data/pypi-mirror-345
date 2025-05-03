"""Standard DB pass-through service managing sessions."""

from ..types_app import _AS, TypeModel, TypePK
from . import service_session_dependent, service_session_independent


class DBService:
    def __init__(self, model: TypeModel) -> None:
        self.model = model

    @staticmethod
    def get_service(method: str, session: _AS | None, *args, **kwargs):
        if session is None:
            return getattr(service_session_independent, method)(*args, **kwargs)
        return getattr(service_session_dependent, method)(session, *args, **kwargs)

    async def get_all(
        self,
        *,
        session: _AS | None = None,
        **filter_data,
    ) -> list[TypeModel]:
        return await self.get_service("get_all", session, self.model, **filter_data)

    async def get(
        self,
        *,
        session: _AS | None = None,
        **filter_data,
    ) -> TypeModel:
        return await self.get_service("get", session, self.model, **filter_data)

    async def exists(
        self,
        *,
        session: _AS | None = None,
        raise_not_found: bool = False,
        **filter_data,
    ) -> TypeModel:
        return await self.get_service(
            "exists", session, self.model, raise_not_found, **filter_data
        )

    async def create(
        self,
        *,
        session: _AS | None = None,
        obj: object | None = None,
        **create_data,
    ) -> TypeModel:
        if bool(obj) == bool(create_data):
            raise ValueError(
                f"CREATE {self.model}: `obj` and `create_data` cannot present or miss both at the time!!!"
            )
        return await self.get_service(
            "create", session, obj or self.model, **create_data
        )

    async def update(
        self,
        *,
        session: _AS | None = None,
        id: TypePK,
        **update_data,
    ) -> TypeModel:
        return await self.get_service("update", session, self.model, id, **update_data)

    async def delete(
        self,
        *,
        session: _AS | None = None,
        id: TypePK,
    ) -> TypeModel:
        return await self.get_service("delete", session, self.model, id)


# If you don't use an alembic -> uncomment below
# async def create_db_and_tables() -> None:
#     await crud.create_db_and_tables()
