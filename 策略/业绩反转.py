import akshare as ak
import pandas as pd
import time


def get_finance_with_retry(date, retries=3):
    """
    获取业绩报表。
    如果东方财富临时断开连接，自动重试。
    """

    last_error = None

    for i in range(retries):
        try:
            df = ak.stock_yjbb_em(date=date)

            if df is not None and not df.empty:
                return df

        except Exception as e:
            last_error = e

            if i < retries - 1:
                time.sleep(3)

    raise RuntimeError(
        f"财务数据接口连续 {retries} 次连接失败：{last_error}"
    )


def run_reversal(
    min_revenue_growth=10.0,
    min_profit_growth=30.0,
    min_acceleration=20.0,
    report_date="20260630"
):
    """
    业绩反转策略 V1

    默认使用 2026 半年报数据。

    条件：
    1. 营业总收入同比 >= min_revenue_growth
    2. 净利润同比 >= min_profit_growth
    3. 净利润同比超过最低门槛至少 min_acceleration 个百分点
    4. 排除 ST / *ST
    """

    # =========================
    # 1. 获取业绩报表
    # =========================
    finance = get_finance_with_retry(
        date=report_date,
        retries=3
    )

    # =========================
    # 2. 检查必要字段
    # =========================
    required_columns = [
        "股票代码",
        "股票简称",
        "营业总收入-同比增长",
        "净利润-同比增长"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in finance.columns
    ]

    if missing_columns:
        raise ValueError(
            f"财务数据缺少字段：{missing_columns}"
        )

    # =========================
    # 3. 统一字段名称
    # =========================
    finance = finance.rename(
        columns={
            "营业总收入-同比增长": "营收同比",
            "净利润-同比增长": "净利润同比",
            "净资产收益率": "ROE",
            "销售毛利率": "毛利率",
            "所处行业": "所属行业"
        }
    )

    # =========================
    # 4. 转换数字
    # =========================
    finance["营收同比"] = pd.to_numeric(
        finance["营收同比"],
        errors="coerce"
    )

    finance["净利润同比"] = pd.to_numeric(
        finance["净利润同比"],
        errors="coerce"
    )

    if "ROE" in finance.columns:
        finance["ROE"] = pd.to_numeric(
            finance["ROE"],
            errors="coerce"
        )

    if "毛利率" in finance.columns:
        finance["毛利率"] = pd.to_numeric(
            finance["毛利率"],
            errors="coerce"
        )

    # =========================
    # 5. 排除 ST
    # =========================
    finance = finance[
        ~finance["股票简称"]
        .astype(str)
        .str.contains("ST", case=False, na=False)
    ].copy()

    # =========================
    # 6. 基础业绩筛选
    # =========================
    finance = finance[
        (finance["营收同比"] >= min_revenue_growth) &
        (finance["净利润同比"] >= min_profit_growth)
    ].copy()

    # =========================
    # 7. 业绩改善强度
    # =========================
    finance["业绩改善强度"] = (
        finance["净利润同比"] -
        min_profit_growth
    )

    finance = finance[
        finance["业绩改善强度"] >= min_acceleration
    ].copy()

    # =========================
    # 8. 排序
    # =========================
    finance = finance.sort_values(
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
        "所属行业",
        "营收同比",
        "净利润同比",
        "业绩改善强度",
        "ROE",
        "毛利率"
    ]

    keep_columns = [
        col for col in keep_columns
        if col in finance.columns
    ]

    result = finance[
        keep_columns
    ].copy()

    result = result.reset_index(drop=True)

    return result
