import logging
from pathlib import Path
from typing import Final

from dingding import DingDing
from polars import Utf8, read_csv

notification_url: Final = (
    r"https://jxzx.bit.edu.cn/tzgg/9791433d77d044b6bed2e07c50b02319.htm"
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

    with open(secrets_file, "r", encoding="utf-8") as f:
        access_token, secret = [
            line.strip() for line in f.readlines() if not line.startswith("#")
        ]

    ding = DingDing(access_token)
    ding.set_secret(secret)

    ding.send_markdown("学生考试安排", markdown)
    logging.info("The message was sent to Ding.")
