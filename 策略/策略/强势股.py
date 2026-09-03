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
    强势股策略 V1

    条件：
    1. 行业20日涨幅在指定区间
    2. 个股连续上涨天数 >= 指定天数
    3. 个股连续涨幅在指定区间
    4. 排除 ST / *ST
    """

    # =========================
    # 1. 获取行业20日数据
    # =========================
    industry = ak.stock_fund_flow_industry(symbol="20日排行")

    industry["行业20日涨幅"] = (
        industry["阶段涨跌幅"]
        .astype(str)
        .str.replace("%", "", regex=False)
    )

    industry["行业20日涨幅"] = pd.to_numeric(
        industry["行业20日涨幅"],
        errors="coerce"
    )

    # 筛选强势行业
    industry = industry[
        (industry["行业20日涨幅"] >= min_industry_gain) &
        (industry["行业20日涨幅"] <= max_industry_gain)
    ]

    industry = industry[
        ["行业", "行业20日涨幅"]
    ].copy()

    # =========================
    # 2. 获取连续上涨股票
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
    # 3. 个股条件
    # =========================
    stocks = stocks[
        (stocks["连涨天数"] >= min_rise_days) &
        (stocks["连续涨跌幅"] >= min_stock_gain) &
        (stocks["连续涨跌幅"] <= max_stock_gain)
    ]

    # 排除 ST
    stocks = stocks[
        ~stocks["股票简称"]
        .astype(str)
        .str.contains("ST", case=False, na=False)
    ]

    # =========================
    # 4. 行业 + 个股合并
    # =========================
    result = stocks.merge(
        industry,
        left_on="所属行业",
        right_on="行业",
        how="inner"
    )

    # =========================
    # 5. 输出字段
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
    # 6. 排序
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

    result = result.reset_index(drop=True)

    return result
