import asyncio
from collections.abc import Coroutine
from typing import Any


async def delay(coro, seconds: int) -> None:
    await asyncio.sleep(seconds)
    return await coro


def delay_task(task_name: Any, coro: Coroutine, seconds: int) -> asyncio.Task:
    return asyncio.create_task(
        coro=delay(coro, seconds),
        name=str(task_name),
    )


def get_task(task_name: Any) -> asyncio.Task | None:
    for task in asyncio.all_tasks():
        if task.get_name() == str(task_name):
            return task
    return None


def cancel_task(task_name: Any) -> bool | None:
    task = get_task(task_name)
    return task.cancel() if task is not None else None
