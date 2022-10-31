from math import isnan
import logging
import re
from io import BytesIO
from urllib.parse import urljoin
from datetime import datetime

from requests import get as fetch
from bs4 import BeautifulSoup
from pandas import read_excel

from typing import Final, List, TypedDict, Optional
from pandas import DataFrame, Series

notification_url: Final = r'https://jxzx.bit.edu.cn/tzgg/9791433d77d044b6bed2e07c50b02319.htm'


class PlanInfo(TypedDict):
    url: str
    note: str
    filename: str


def get_plan_info(**requests_args) -> PlanInfo:
    req = fetch(notification_url, **requests_args)
    req.raise_for_status()
    req.encoding = 'utf-8'

    soup = BeautifulSoup(req.text, features='lxml')
    plan_element = soup.select(
        '.pageArticle > .Annex > ul > li > a:not([download])'
    )[1]
    url = urljoin(notification_url, plan_element.get('href'))  # type: ignore

    filename = plan_element.get_text()
    assert '学生' in filename and '考试安排' in filename

    note = re.search(r'(?<=（).+(?=）)', filename).group(0)  # type: ignore

    logging.info(f"Got the URL of “{note}”: {url} .")

    return PlanInfo(
        url=url,
        filename=filename,
        note=note
    )


def get_watched_plans(url: str, watches: List[str], **requests_args) -> DataFrame:
    """
    Returns:
        The data with Index(['学号', '姓名', '课程号', '课程名', '考试序号', '考试时间', '其他说明', '通知单类型']).
    """

    res = fetch(url, **requests_args)
    res.raise_for_status()
    data = read_excel(BytesIO(res.content))
    # 若直接`read_excel(url)`，无法设置代理

    return data[data['学号'].isin(watches)]


def filter_out_personal_info(plans: DataFrame) -> DataFrame:
    """
    See `get_watched_plans`.
    """

    columns: Final = ['课程号', '课程名', '考试时间', '其他说明', '通知单类型']
    assert columns[-1] == '通知单类型'

    safe_plans = plans[columns]
    unique_plans = safe_plans.drop_duplicates()

    merged_plans = unique_plans.groupby(
        columns[:-1], dropna=False
    ).aggregate({
        '通知单类型': '／'.join
    }).reset_index()

    return merged_plans.sort_values(by='考试时间', axis='index')


def one_plan_to_markdown(plan: Series) -> str:
    raw_time: str = plan['考试时间']
    is_completed = datetime.fromisoformat(
        raw_time.split()[0]).date() < datetime.now().date()

    title: str = f"{plan['课程名']}"
    if is_completed:
        title = f"✓ {title}"
    else:
        title = f"**{title}**"

    if plan['通知单类型'] != '正常':
        title += f"（{plan['通知单类型']}）"

    if is_completed:
        return f"- {title}"
    else:
        time: str = raw_time.replace('(', '（').replace(')', '）')

        raw_remark = plan['其他说明']
        remark: list[str] = []
        if type(raw_remark) == str:
            remark = [f"> {line}" for line in raw_remark.split('\n')]
        elif type(raw_remark) == float and isnan(raw_remark):
            pass
        else:
            logging.error(f"备注无法识别：{raw_remark}。")

        return '\n\n'.join(filter(lambda x: bool(x), [
            f"- {title}",
            f"  {time}",
            '\n>\n'.join(remark)
            # remark 本应是 list item 的内容，然而钉钉手机端不支持（会导致后续加粗失效），只好去除缩进了。
        ]))


def all_plans_to_markdown(plans: DataFrame) -> str:
    if plans.empty:
        return ''

    messages = plans.apply(one_plan_to_markdown, axis='columns')
    return '\n\n'.join(messages)  # type: ignore


def fetch_notification_markdown(watches: List[str], **requests_args) -> str:
    info = get_plan_info(**requests_args)
    plans = get_watched_plans(info['url'], watches, **requests_args)
    plans = filter_out_personal_info(plans)

    return '\n\n'.join([
        f'（测试）我们班相关的“学生考试安排”如下。（{info["note"]}）',
        all_plans_to_markdown(plans),
        f"详情见[教学中心通知]({notification_url})。"
    ])
