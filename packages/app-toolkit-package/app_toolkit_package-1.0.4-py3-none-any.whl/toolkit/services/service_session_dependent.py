"""Standard session dependent pass-through service."""

from ..repo.db import crud
from ..types_app import _AS, TypeModel, TypePK


async def get_all(
    session: _AS,
    model: TypeModel,
    **filter_data,
) -> list[TypeModel]:
    return await crud.get_all(session, model, **filter_data)


async def get(
    session: _AS,
    model: TypeModel,
    **filter_data,
) -> TypeModel:
    return await crud.get_one(session, model, **filter_data)


async def exists(
    session: _AS,
    model: TypeModel,
    raise_not_found: bool = False,
    **filter_data,
) -> bool:
    return await crud.exists(session, model, raise_not_found, **filter_data)


async def create(
    session: _AS,
    entity: TypeModel | object,
    **create_data,
) -> TypeModel:
    assert session.in_transaction()
    if create_data:
        entity = entity(**create_data)  # type: ignore [operator]
    return await crud.create(session, entity)  # type: ignore [arg-type]


async def update(
    session: _AS,
    model: TypeModel,
    id: TypePK,
    **update_data,
) -> TypeModel:
    assert session.in_transaction()
    return await crud.update(session, model, id, **update_data)


async def delete(
    session: _AS,
    model: TypeModel,
    id: TypePK,
) -> TypeModel:
    assert session.in_transaction()
    # below crud.delete has a problem with models with relations
    # return await crud.delete(session, model, id)
    obj = await crud.get_one(session, model, id=id)
    session.add(obj)
    await session.delete(obj)
    return obj
