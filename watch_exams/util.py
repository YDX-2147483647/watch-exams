import logging
import re
from difflib import ndiff
from pathlib import Path

from dingding import DingDing
from pandas import read_csv


def load_watches(filepath: Path) -> list[str]:
    watches = read_csv(
        filepath,
        encoding="utf-8",
        comment="#",
        dtype=str,
    )

    return list(watches["学号"])


def has_changed(message: str, old_message: str | None) -> bool:
    if old_message is None:
        old_message = "\n"

    return old_message[old_message.index("\n") :] != message[message.index("\n") :]


def compare(message: str, old_message: str | None) -> str:
    """比较新旧消息，表示为钉钉的 Markdown"""

    if old_message is None:
        return message

    difference = ndiff(
        old_message.splitlines(keepends=True),
        message.splitlines(keepends=True),
    )

    confusing = False
    result = []
    for line in difference:
        if "\n" in line:
            t = line.rindex("\n")
            tail = line[t:]
        else:
            t = None
            tail = ""

        code = line[:2]
        line = line[2:t]

        match code:
            case "  ":
                result.append(line + tail)
            case "+ ":
                if re.match(r"^([->\s]*)$", line):
                    result.append(line + tail)
                else:
                    head_line = re.sub(
                        r"^([-#>\s]*)", r'\1<font color="#00FF00">', line
                    )
                    result.append(f"{head_line}</font>{tail}")
            case "- ":
                confusing = True
                result.append(f'\n<font color="#FF0000">\\-  {line}</font>{tail}\n')
            case "? ":
                confusing = True
                result.append(f'\n<font color="#0072A3">?  {line}</font>{tail}\n')
            case _:
                result.append(f"{code}{line}{tail}")

    if confusing:
        result.append(
            '\n\n（<font color="#00FF00">绿色</font>代表新增，'
            '“<font color="#FF0000">\\-</font>”开头表示删除，'
            '“<font color="#0072A3">?</font>”开头指示更改）\n'
        )

    return "".join(result)


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
