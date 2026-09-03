import akshare as ak
import pandas as pd


def run_strategy(
    min_industry_gain=10.0,
    max_industry_gain=20.0,
    min_rise_days=5,
    min_stock_gain=3.0,
    max_stock_gain=20.0
):
    """
    强势5连阳选股策略 V1

    条件：
    1. 行业20日涨幅在指定区间
    2. 个股连续上涨天数 >= 指定天数
    3. 个股连续涨幅在指定区间
    4. 排除 ST / *ST
    """

    # =========================
    # 1. 获取行业20日排行
    # =========================
    industry = ak.stock_fund_flow_industry(symbol="20日排行")

    # 将行业阶段涨跌幅转换成数字
    industry["行业20日涨幅"] = (
        industry["阶段涨跌幅"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )

    industry["行业20日涨幅"] = pd.to_numeric(
        industry["行业20日涨幅"],
        errors="coerce"
    )

    # =========================
    # 2. 筛选符合涨幅要求的行业
    # =========================
    industry = industry[
        (industry["行业20日涨幅"] >= min_industry_gain) &
        (industry["行业20日涨幅"] <= max_industry_gain)
    ]

    industry = industry[
        ["行业", "行业20日涨幅"]
    ].copy()

    # =========================
    # 3. 获取连续上涨股票
    # =========================
    stocks = ak.stock_rank_lxsz_ths()

    stocks["连涨天数"] = pd.to_numeric(
        stocks["连涨天数"],
        errors="coerce"
    )

    stocks["连续涨跌幅"] = pd.to_numeric(
        stocks["连续涨跌幅"],
        errors="coerce"
    )

    # =========================
    # 4. 筛选连续上涨股票
    # =========================
    stocks = stocks[
        (stocks["连涨天数"] >= min_rise_days) &
        (stocks["连续涨跌幅"] >= min_stock_gain) &
        (stocks["连续涨跌幅"] <= max_stock_gain)
    ]

    # =========================
    # 5. 排除 ST / *ST
    # =========================
    stocks = stocks[
        ~stocks["股票简称"]
        .astype(str)
        .str.contains("ST", case=False, na=False)
    ]

    # =========================
    # 6. 行业数据与个股数据合并
    # =========================
    result = stocks.merge(
        industry,
        left_on="所属行业",
        right_on="行业",
        how="inner"
    )

    # =========================
    # 7. 保留需要显示的字段
    # =========================
    result = result[
        [
            "股票代码",
            "股票简称",
            "所属行业",
            "行业20日涨幅",
            "连涨天数",
            "连续涨跌幅"
        ]
    ].copy()

    # =========================
    # 8. 排序
    # =========================
    result = result.sort_values(
        by=[
            "行业20日涨幅",
            "连涨天数",
            "连续涨跌幅"
        ],
        ascending=[
            False,
            False,
            False
        ]
    )

    # 重置序号
    result = result.reset_index(drop=True)

    return result
