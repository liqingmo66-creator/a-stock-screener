import akshare as ak
import pandas as pd


def run_reversal(
    min_revenue_growth=10.0,
    min_profit_growth=30.0,
    min_acceleration=20.0
):
    """
    业绩反转策略 V1

    核心逻辑：
    1. 营业收入同比增长 >= 指定值
    2. 净利润同比增长 >= 指定值
    3. 净利润增速相较上一期明显改善
    4. 排除 ST / *ST

    参数：
    min_revenue_growth  最低营收同比增速
    min_profit_growth   最低净利润同比增速
    min_acceleration    净利润增速至少改善多少个百分点
    """

    # =========================
    # 1. 获取A股实时行情
    # =========================
    spot = ak.stock_zh_a_spot_em()

    spot = spot.rename(
        columns={
            "代码": "股票代码",
            "名称": "股票简称"
        }
    )

    # 排除 ST
    spot = spot[
        ~spot["股票简称"]
        .astype(str)
        .str.contains("ST", case=False, na=False)
    ].copy()

    # =========================
    # 2. 获取最新业绩快报/业绩报表
    # =========================
    finance = ak.stock_yjbb_em()

    # 不同时间接口字段可能略有区别
    # 这里统一处理常用字段名称
    rename_map = {
        "股票代码": "股票代码",
        "股票简称": "股票简称",
        "营业收入-营业收入": "营业收入",
        "营业收入-同比增长": "营收同比",
        "净利润-净利润": "净利润",
        "净利润-同比增长": "净利润同比"
    }

    finance = finance.rename(
        columns={
            k: v for k, v in rename_map.items()
            if k in finance.columns
        }
    )

    # =========================
    # 3. 找营收同比字段
    # =========================
    revenue_col = None

    for col in finance.columns:
        if "营业收入" in str(col) and "同比" in str(col):
            revenue_col = col
            break

    # =========================
    # 4. 找净利润同比字段
    # =========================
    profit_col = None

    for col in finance.columns:
        if "净利润" in str(col) and "同比" in str(col):
            profit_col = col
            break

    if revenue_col is None or profit_col is None:
        raise ValueError(
            "当前财务数据接口字段发生变化，未找到营收同比或净利润同比字段"
        )

    # 转数字
    finance["营收同比"] = pd.to_numeric(
        finance[revenue_col],
        errors="coerce"
    )

    finance["净利润同比"] = pd.to_numeric(
        finance[profit_col],
        errors="coerce"
    )

    # =========================
    # 5. 基础业绩筛选
    # =========================
    finance = finance[
        (finance["营收同比"] >= min_revenue_growth) &
        (finance["净利润同比"] >= min_profit_growth)
    ].copy()

    # =========================
    # 6. 获取上一期业绩数据
    # =========================
    # V1阶段：
    # 如果接口当前只有最新一期数据，
    # 则先用净利润同比本身作为反转强度基础评分。
    #
    # 后续V2再增加：
    # 本期净利润增速 > 上期净利润增速

    finance["业绩改善强度"] = (
        finance["净利润同比"] -
        min_profit_growth
    )

    finance = finance[
        finance["业绩改善强度"] >= min_acceleration
    ].copy()

    # =========================
    # 7. 合并股票简称
    # =========================
    result = finance.merge(
        spot[
            [
                "股票代码",
                "股票简称"
            ]
        ],
        on="股票代码",
        how="inner",
        suffixes=("", "_实时")
    )

    if "股票简称_实时" in result.columns:
        result["股票简称"] = result["股票简称_实时"]

    # =========================
    # 8. 排序
    # =========================
    result = result.sort_values(
        by=[
            "净利润同比",
            "营收同比"
        ],
        ascending=[
            False,
            False
        ]
    )

    # =========================
    # 9. 输出字段
    # =========================
    keep_columns = [
        "股票代码",
        "股票简称",
        "营收同比",
        "净利润同比",
        "业绩改善强度"
    ]

    keep_columns = [
        col for col in keep_columns
        if col in result.columns
    ]

    result = result[
        keep_columns
    ].copy()

    result = result.reset_index(drop=True)

    return result
