from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from io import BytesIO
from typing import TYPE_CHECKING
from urllib.parse import urljoin

import polars as pl
from bs4 import BeautifulSoup
from polars import Utf8, read_excel
from requests import get as fetch

from .util import notification_url

if TYPE_CHECKING:
    from typing import Final

    from polars import DataFrame


@dataclass
class _PlanInfo:
    url: str
    note: str
    filename: str


def _get_plan_info(**requests_args) -> _PlanInfo:
    logging.info(f"Fetching the notification: {notification_url}.")

    res = fetch(notification_url, **requests_args)
    res.raise_for_status()
    res.encoding = "utf-8"

    soup = BeautifulSoup(res.text, features="lxml")
    plan_element = soup.select(".pageArticle > .Annex > ul > li > a:not([download])")[1]
    url: str = urljoin(notification_url, plan_element.get("href"))  # type: ignore

    filename = plan_element.get_text()
    assert "学生" in filename and "考试安排" in filename

    note = re.search(r"(?<=（).+(?=）)", filename).group(0)  # type: ignore

    logging.info(f"Got the URL of “{note}”: {url} .")

    return _PlanInfo(url=url, filename=filename, note=note)


def _get_watched_plans(url: str, watches: list[str], **requests_args) -> DataFrame:
    """
    Returns:
        The data with the following indices.
            "学号", "姓名", "课程号", "课程名", "考试序号", "考试时间", "其他说明", "通知单类型"
    """

    res = fetch(url, **requests_args)
    res.raise_for_status()

    logging.info("Successfully downloaded the xlsx.")

    return read_excel(
        BytesIO(res.content),
        sheet_id=1,
        sheet_name=None,
        read_csv_options=dict(dtypes={"学号": Utf8}),
    ).filter(pl.col("学号").is_in(watches))


def _filter_out_personal_info(plans: DataFrame) -> DataFrame:
    """
    See `get_watched_plans`.
    """

    columns: Final = ["课程号", "课程名", "考试时间", "其他说明", "通知单类型"]
    assert columns[-1] == "通知单类型"

    return (
        plans.select(pl.col(columns))
        .unique()
        .groupby(columns[:-1])
        .agg(pl.col("通知单类型"))
        .sort("考试时间")
    )


def fetch_plans(watches: list[str], **requests_args) -> tuple[DataFrame, str]:
    """
    Return: plans, note
    """

    info = _get_plan_info(**requests_args)
    plans = _get_watched_plans(info.url, watches, **requests_args)
    plans = _filter_out_personal_info(plans)

    return plans, info.note
