import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from qbittorrentapi import Client, Tracker  # 你妈的类型能不能好好写?

from .. import config
from ..utils.base import write_lines
from ..utils.functions import load_all_tracker, show_test_result
from ..utils.output import create_progress, fail, print

__all__ = ["ClientTestOptions", "client_test"]


def get_torrent(client: Client, torrent: str):
    torrents = client.torrents.info.all()
    for t in torrents:
        if torrent == t.name or torrent == t.hash:
            return t
    return None


@dataclass
class ClientTestOptions:
    url: str
    torrent: str
    user: Optional[str] = None
    pwd: Optional[str] = None


async def client_test(
    tracker_urls: list[str],
    client_options: ClientTestOptions,
    output_path: Path,
    *,
    fast_mode: bool = True,
    polling_interval: float = 3.0,
    yes_all: bool = False,
):
    all_trackers, provider_map = await load_all_tracker(tracker_urls)

    # 连接qbittorrent客户端
    print(f"Connecting to qBittorrent web api (url: {client_options.url}, user: {client_options.user})...")
    client = Client(host=client_options.url, username=client_options.user, password=client_options.pwd)

    # 寻找测试种子
    test_torrent = get_torrent(client, client_options.torrent)
    if test_torrent is None:
        print(f"Torrent “{client_options.torrent}” not found in “{client_options.url}”.")
        return
    print(f"Found test torrent: “{test_torrent.name}”({test_torrent.hash})")

    # 清除原有的所有 tracker
    old_trackers = [t.url for t in test_torrent.trackers]

    # 从这里开始要考虑恢复原有tracker了
    try:
        client.torrents_remove_trackers(
            test_torrent.info.hash,
            urls=[t.url for t in test_torrent.trackers],
        )
        print(f"Removed all trackers from “{test_torrent.name}”.")

        # 添加新的测试tracker
        client.torrents_add_trackers(
            test_torrent.hash,
            urls=all_trackers,
        )
        print(f"Added {len(all_trackers)} trackers to “{test_torrent.name}”.")

        # 等待tracker生效
        contracted_trackers = []
        available_trackers = []

        progress = create_progress()
        progress.start()
        bar = progress.add_task("Waiting for all trackers to be contacted", total=len(all_trackers))

        def check_has_data(t: Tracker):
            return t.num_downloaded != -1 or t.num_leeches != -1 or t.num_peers != -1 or t.num_seeds != -1

        async def wait_trackers():
            while True:
                await asyncio.sleep(polling_interval)
                torrent = get_torrent(client, client_options.torrent)
                if not torrent:
                    fail(f"Torrent “{client_options.torrent}” not found.")
                    continue
                for t in torrent.trackers:
                    if t.url not in all_trackers:
                        continue
                    elif t.url in contracted_trackers:
                        continue
                    elif t.status == 2:
                        contracted_trackers.append(t.url)
                        available_trackers.append(t.url)
                    elif t.status == 3 and check_has_data(t):
                        contracted_trackers.append(t.url)
                        available_trackers.append(t.url)
                    elif t.status == 3 and t.msg != "" and fast_mode:
                        if t.url not in contracted_trackers:
                            fail(f"Tracker “{t.url}” is not contactable(updating but failed): “{t.msg}”")
                        contracted_trackers.append(t.url)
                    elif t.status == 4:
                        if t.url not in contracted_trackers:
                            fail(f"Tracker “{t.url}” is not contactable(not working): “{t.msg}”")
                        contracted_trackers.append(t.url)

                progress.update(bar, completed=len(contracted_trackers))
                if len(contracted_trackers) == len(all_trackers):
                    print("All trackers are contacted.")
                    break

        await asyncio.wait_for(wait_trackers(), timeout=config.timeout)
        show_test_result(all_trackers, available_trackers, provider_map)
        if not yes_all:
            print("press enter to continue...")
    except asyncio.TimeoutError:
        show_test_result(all_trackers, available_trackers, provider_map)
        if not yes_all:
            print("press enter to continue...")
    except Exception as e:
        progress.stop()
        raise e
    finally:
        # 恢复原有tracker
        test_torrent = get_torrent(client, client_options.torrent)
        if not test_torrent:
            fail(f"Torrent “{client_options.torrent}” not found.")
            return
        client.torrents_remove_trackers(
            test_torrent.hash,
            urls=[t.url for t in test_torrent.trackers],
        )
        print(f"Removed all testing trackers from “{test_torrent.name}”.")
        client.torrents_add_trackers(
            test_torrent.hash,
            urls=old_trackers,
        )
        print(f"Restored all original trackers to “{test_torrent.name}”.")
    # 保存结果
    print(f"Saving output file to “{output_path}”...")
    write_lines(output_path, available_trackers)
    print("Output files saved.")
