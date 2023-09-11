from __future__ import annotations

import logging
import re
from difflib import ndiff
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class Saver:
    message: str | None
    _output_dir: Path

    def __init__(self, output_dir: Path) -> None:
        """
        Param:
        - output_dir: the directory to save outputs. Auto mkdir if not exists.
        """

        output_dir.mkdir(exist_ok=True)
        self._output_dir = output_dir

        self.message = None

    @property
    def output_dir(self) -> Path:
        return self._output_dir

    @property
    def output_file(self) -> Path:
        return self._output_dir / "message.txt"

    @property
    def old_output_file(self) -> Path:
        return self.output_file.with_stem("message-old")

    def changed(self) -> bool:
        assert (
            self.message is not None
        ), "No message to compare. Please set `saver.message`."

        old_message = self._read_old_message() or "\n"

        # ignore first row
        return (
            old_message[old_message.index("\n") :]
            != self.message[self.message.index("\n") :]
        )

    def _read_old_message(self) -> str | None:
        if self.output_file.exists():
            return self.output_file.read_text(encoding="utf-8")
        else:
            return None

    def diff(self) -> str:
        """比较新旧消息，表示为钉钉的 Markdown"""

        assert (
            self.message is not None
        ), "No message to compare. Please set `saver.message`."

        old_message = self._read_old_message()

        if old_message is None:
            return self.message

        difference = ndiff(
            old_message.splitlines(keepends=True),
            self.message.splitlines(keepends=True),
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
            line = line[2:t]  # noqa: PLW2901 redefined-loop-name

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

    def save(self) -> None:
        """备份并更新 message.txt"""

        if self.message is None:
            logging.warning("Nothing to save. Ignored.")
            return

        # Backup the old
        self.old_output_file.unlink(missing_ok=True)
        try:
            self.output_file.rename(self.old_output_file)
        except FileNotFoundError:
            pass

        # Save the new
        self.output_file.write_text(self.message, encoding="utf-8")
        logging.info(f"The message was saved to {self.output_file}.")
