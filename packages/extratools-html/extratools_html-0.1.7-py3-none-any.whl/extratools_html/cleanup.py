from asyncio import create_subprocess_exec, subprocess
from asyncio.subprocess import Process


async def cleanup_page(page_html: str) -> str:
    # https://github.com/danburzo/percollate
    process: Process = await create_subprocess_exec(
        "percollate",
        *[
            "html",
            "--output",
            "-",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    stdout, _ = await process.communicate(page_html.encode())

    return stdout.decode()
