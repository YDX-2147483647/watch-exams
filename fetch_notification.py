from math import isnan
import logging
import re
from io import BytesIO
from urllib.parse import urljoin

from requests import get as fetch
from bs4 import BeautifulSoup
from pandas import read_excel

from typing import Final, List, TypedDict, Optional
from pandas import DataFrame, Series

notification_url: Final = r'https://jxzx.bit.edu.cn/tzgg/0d9f2ceab73245098241554162b99978.htm'


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
    )[0]
    url = urljoin(notification_url, plan_element.get('href'))

    filename = plan_element.get_text()
    assert '学生考试安排' in filename

    note = re.search(r'(?<=（).+(?=）)', filename).group(0)

    logging.info(f"Got the URL of “{note}”: {url} .")

    return PlanInfo(
        url=url,
        filename=filename,
        note=note
    )


def get_watched_plans(url: str, watches: List[str], **requests_args) -> DataFrame:
    """
    Returns:
        The data with Index(['学号', '姓名', '课程号', '课程名', '考试序号', '考试时间', '考试须知查询', '通知单类型']).
    """

    res = fetch(url, **requests_args)
    res.raise_for_status()
    data = read_excel(BytesIO(res.content))
    # 若直接`read_excel(url)`，无法设置代理

    return data[data['姓名'].isin(watches)]


def filter_out_personal_info(plans: DataFrame) -> DataFrame:
    """
    See `get_watched_plans`.
    """

    columns: Final = ['课程号', '课程名', '考试时间', '考试须知查询', '通知单类型']
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
    title: str = plan['课程名']
    if plan['通知单类型'] != '正常':
        title += f"（{plan['通知单类型']}）"

    time: str = plan['考试时间'].replace('(', '（').replace(')', '）')

    raw_remark = plan['考试须知查询']
    remark: Optional[str] = None
    if type(raw_remark) == str:
        remark = raw_remark
    elif type(raw_remark) == float and isnan(raw_remark):
        pass
    else:
        logging.error(f"备注无法识别：{raw_remark}。")

    return '- ' + '\n\n  '.join(row for row in [title, time, remark] if row)


def all_plans_to_markdown(plans: DataFrame) -> str:
    messages = plans.apply(one_plan_to_markdown, axis='columns')
    return '\n\n'.join(messages)


def fetch_notification_markdown(watches: List[str], **requests_args) -> str:
    info = get_plan_info(**requests_args)
    plans = get_watched_plans(info['url'], watches, **requests_args)
    plans = filter_out_personal_info(plans)

    return '\n\n'.join([
        f'（测试）我们班相关的“学生考试安排”如下。（{info["note"]}）',
        all_plans_to_markdown(plans),
        f"详情见[教学中心通知]({notification_url})。"
    ])
