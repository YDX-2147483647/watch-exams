from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from dingding import DingDing
from polars import Utf8, read_csv

if TYPE_CHECKING:
    from pathlib import Path

notification_url: Final = (
    r"https://jxzx.bit.edu.cn/tzgg/acf3d085e79344f8aa957058692d11f7.htm"
)


def load_watches(filepath: Path) -> list[str]:
    watches = read_csv(
        filepath,
        encoding="utf-8",
        comment_char="#",
        dtypes={"姓名": Utf8, "学号": Utf8},
    )

    return list(watches["学号"])


def ding(markdown: str, secrets_file: Path) -> None:
    """向钉钉发送 Markdown"""

    with open(secrets_file, encoding="utf-8") as f:
        access_token, secret = (
            line.strip() for line in f.readlines() if not line.startswith("#")
        )

    ding = DingDing(access_token)
    ding.set_secret(secret)

    ding.send_markdown("学生考试安排", markdown)
    logging.info("The message was sent to Ding.")
