import asyncio
from pathlib import Path
from typing import List, Optional

import typer

from ..functions.set_tracker import BtClientOptions, set_tracker
from ..utils.base import read_lines

cmd = typer.Typer(
    name="set-trackers",
    help="Set trackers for qbittorrent client",
)


@cmd.callback()
def cmd_set_trackers(
    url: str = typer.Argument(..., help="Url of the qbittorrent web ui"),
    username: Optional[str] = typer.Option(
        None,
        "--username",
        "-u",
        envvar="QBITTORRENT_USERNAME",
        help="Username for the qbittorrent client",
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        envvar="QBITTORRENT_PASSWORD",
        help="Password for the qbittorrent client",
    ),
    trackers_urls: List[str] = typer.Option(
        [],
        "--trackers-urls",
        "-t",
        help="List of trackers urls",
    ),
    tackers_file: Optional[Path] = typer.Option(
        None,
        "--tackers-file",
        "-f",
        help="Path to the file containing trackers",
    ),
    append: bool = typer.Option(
        False,
        "--append",
        "-a",
        help="Append trackers to existing trackers",
    ),
):
    urls = trackers_urls
    if tackers_file:
        urls += read_lines(tackers_file.read_text())
    asyncio.run(
        set_tracker(
            urls,
            BtClientOptions(url=url, user=username, pwd=password),
            append,
        )
    )
