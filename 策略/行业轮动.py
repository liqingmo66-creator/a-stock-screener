import akshare as ak
import pandas as pd


def run_rotation(
    min_industry_gain=5.0,
    max_industry_gain=20.0,
    min_rise_days=3,
    min_stock_gain=0.0,
    max_stock_gain=30.0,
    top_industries=5,
    stocks_per_industry=2
):
    """
    行业轮动策略 V1

    逻辑：
    1. 找最近20日涨幅较强的行业
    2. 选出排名靠前的行业
    3. 在这些行业中寻找近期连续上涨的强势个股
    4. 每个行业保留指定数量的强势股票
    5. 排除 ST / *ST
    """

    # =========================
    # 1. 获取行业20日排行
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

    # =========================
    # 2. 筛选强势行业
    # =========================
    industry = industry[
        (industry["行业20日涨幅"] >= min_industry_gain) &
        (industry["行业20日涨幅"] <= max_industry_gain)
    ].copy()

    # 按行业20日涨幅从高到低排列
    industry = industry.sort_values(
        "行业20日涨幅",
        ascending=False
    )

    # 只取最强的前 N 个行业
    industry = industry.head(top_industries)

    industry = industry[
        ["行业", "行业20日涨幅"]
    ].copy()

    # 如果没有符合条件的行业，直接返回空表
    if industry.empty:
        return pd.DataFrame(
            columns=[
                "股票代码",
                "股票简称",
                "所属行业",
                "行业20日涨幅",
                "连涨天数",
                "连续涨跌幅"
            ]
        )

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
    # 4. 筛选近期强势股票
    # =========================
    stocks = stocks[
        (stocks["连涨天数"] >= min_rise_days) &
        (stocks["连续涨跌幅"] >= min_stock_gain) &
        (stocks["连续涨跌幅"] <= max_stock_gain)
    ].copy()

    # 排除 ST / *ST
    stocks = stocks[
        ~stocks["股票简称"]
        .astype(str)
        .str.contains("ST", case=False, na=False)
    ]

    # =========================
    # 5. 个股与强势行业合并
    # =========================
    result = stocks.merge(
        industry,
        left_on="所属行业",
        right_on="行业",
        how="inner"
    )

    if result.empty:
        return pd.DataFrame(
            columns=[
                "股票代码",
                "股票简称",
                "所属行业",
                "行业20日涨幅",
                "连涨天数",
                "连续涨跌幅"
            ]
        )

    # =========================
    # 6. 行业内股票排序
    # =========================
    result = result.sort_values(
        by=[
            "行业20日涨幅",
            "连续涨跌幅",
            "连涨天数"
        ],
        ascending=[
            False,
            False,
            False
        ]
    )

    # =========================
    # 7. 每个行业只保留前 N 只
    # =========================
    result = (
        result
        .groupby("所属行业", group_keys=False)
        .head(stocks_per_industry)
    )

    # =========================
    # 8. 最终显示字段
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

    # 最终排序
    result = result.sort_values(
        by=[
            "行业20日涨幅",
            "连续涨跌幅"
        ],
        ascending=[
            False,
            False
        ]
    )

    result = result.reset_index(drop=True)

    return result
