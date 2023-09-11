from __future__ import annotations

import logging
from datetime import datetime
from math import isnan
from typing import TYPE_CHECKING

import polars as pl
from zoneinfo import ZoneInfo

from .util import notification_url

if TYPE_CHECKING:
    from polars import DataFrame


def _one_plan_to_markdown(plan: dict) -> str:
    raw_time: str = plan["考试时间"]
    is_completed = (
        datetime.fromisoformat(raw_time.split()[0]).date()
        < datetime.now(tz=ZoneInfo("Asia/Shanghai")).date()
    )

    title: str = f"{plan['课程名']}"
    if is_completed:
        title = f"✓ {title}"
    else:
        title = f"**{title}**"

    if plan["通知单类型"] != ["正常"]:
        title += f"（{'／'.join(plan['通知单类型'])}）"

    if is_completed:
        return f"- {title}"
    else:
        time: str = raw_time.replace("(", "（").replace(")", "）")

        raw_remark = plan["其他说明"]
        remark: list[str] = []
        if isinstance(raw_remark, str):
            remark = [f"> {line}" for line in raw_remark.split("\n")]
        elif isinstance(raw_remark, float) and isnan(raw_remark):
            pass
        elif raw_remark is None:
            pass
        else:
            logging.error(f"备注无法识别：{raw_remark}。")

        return "\n\n".join(
            filter(
                bool,
                [
                    f"- {title}",
                    f"  {time}",
                    "\n>\n".join(remark),
                    # remark 本应是 list item 的内容，
                    # 然而钉钉手机端不支持（会导致后续加粗失效），只好去除缩进了。
                ],
            )
        )


def _all_plans_to_markdown(plans: DataFrame) -> str:
    if plans.is_empty():
        return ""

    messages = plans.select(
        pl.struct(pl.all()).apply(_one_plan_to_markdown)
    ).to_series()
    return "\n\n".join(messages)


def to_markdown(plans: DataFrame, note: str) -> str:
    return "\n\n".join(
        [
            f"（测试）我们班相关的“学生考试安排”如下。（{note}）",
            _all_plans_to_markdown(plans),
            f"详情见[教学中心通知]({notification_url})。",
        ]
    )
