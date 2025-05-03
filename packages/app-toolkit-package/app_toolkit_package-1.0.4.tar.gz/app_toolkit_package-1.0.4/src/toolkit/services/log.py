# from src.config import db_config as c
# from ..models.log import BaseLog
# from ..repo.db import crud


# async def db_logger(client_info, secret_id, event, event_time) -> None:
#     async with c.async_session.begin() as session:
#         await crud.create(
#             session,
#             Log(
#                 client_info=client_info,
#                 secret_id=secret_id,
#                 event=event,
#                 event_time=event_time,
#             ),
#         )
