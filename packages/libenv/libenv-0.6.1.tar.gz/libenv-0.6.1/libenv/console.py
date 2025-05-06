from typing import List
import asyncio

from rich.console import Console

console = Console(soft_wrap=True)

async def run_command(command: List[str]) -> int:
    console.print(f"running: {command}")

    process = await asyncio.create_subprocess_exec(*command)
    #stdout, stderr = await process.communicate()
    ret = await process.wait()
    return ret
