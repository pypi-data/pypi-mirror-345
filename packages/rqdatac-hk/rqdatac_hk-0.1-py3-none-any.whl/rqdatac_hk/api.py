import pandas as pd
import math
from rqdatac.validators import (
    ensure_date_or_today_int,
    ensure_list_of_string,
    ensure_date_int,
    check_quarter,
    quarter_string_to_date,
    check_items_in_container,
)
from rqdatac.client import get_client
from rqdatac.decorators import export_as_api
from rqdatac.hk_decorators import support_hk_order_book_id
from rqdatac.services.financial import HK_FIELDS_LIST_EX


@export_as_api(namespace="hk")
@support_hk_order_book_id
def get_detailed_financial_items(
    order_book_ids,
    fields,
    start_quarter,
    end_quarter,
    date=None,
    statements="latest",
    market="hk",
):
    """获取港股财务细项
    :param order_book_ids: 股票合约代码列表
    :param fields: 指定返回财报字段
    :param start_quarter: 财报季度 - 起始，如 2020q1
    :param end_quarter: 财报季度 - 截止
    :param date: 财报发布日期，默认为当前日期, 如 '2020-01-01' | '20200101'
    :param statements: 可选 latest/all, 默认为 latest
            latest: 仅返回在date时点所能观察到的最新数据；
            all：返回在date时点所能观察到的所有版本，从第一次发布直到观察时点的所有修改。
    :return: DataFrame
    """
    order_book_ids = ensure_list_of_string(order_book_ids, "order_book_ids")
    check_quarter(start_quarter, "start_quarter")
    start_quarter_int = ensure_date_int(quarter_string_to_date(start_quarter))
    check_quarter(end_quarter, "end_quarter")
    end_quarter_int = ensure_date_int(quarter_string_to_date(end_quarter))
    if start_quarter > end_quarter:
        raise ValueError(
            "invalid quarter range: [{!r}, {!r}]".format(start_quarter, end_quarter)
        )
    if fields is not None:
        fields = ensure_list_of_string(fields, "fields")
        check_items_in_container(fields, HK_FIELDS_LIST_EX, "fields")
    if statements not in ["all", "latest"]:
        raise ValueError("invalid statements , got {!r}".format(statements))
    date = ensure_date_or_today_int(date)
    result = get_client().execute(
        "hk.get_detailed_financial_items",
        order_book_ids,
        fields,
        start_quarter_int,
        end_quarter_int,
        date,
        statements,
    )
    if not result:
        return None
    df = pd.DataFrame.from_records(result)
    df["end_date"] = df["end_date"].apply(
        lambda d: "{}q{}".format(d.year, math.ceil(d.month / 3))
    )
    df.sort_values(["order_book_id", "end_date", "info_date"], inplace=True)
    df.rename(columns={"end_date": "quarter"}, inplace=True)
    df.set_index(["order_book_id", "quarter"], inplace=True)
    return df
