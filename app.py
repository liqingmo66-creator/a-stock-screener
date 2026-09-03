import streamlit as st
import pandas as pd

from 策略.强势股 import run_strategy
from 策略.行业轮动 import run_rotation
from 策略.业绩反转 import run_reversal

st.set_page_config(
    page_title="A股趋势筛选",
    page_icon="📈",
    layout="wide"
)

st.title("A股趋势筛选器")


# =========================
# 策略选择
# =========================
strategy_name = st.selectbox(
    "选择选股策略",
    [
        "强势5连阳",
        "行业轮动",
        "业绩反转"
    ]
)


# =========================================================
# 策略1：强势5连阳
# =========================================================
if strategy_name == "强势5连阳":

    st.subheader("强势5连阳策略")

    min_industry_gain = st.number_input(
        "行业20日最低涨幅 %",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=1.0
    )

    max_industry_gain = st.number_input(
        "行业20日最高涨幅 %",
        min_value=0.0,
        max_value=100.0,
        value=20.0,
        step=1.0
    )

    min_rise_days = st.number_input(
        "最低连涨天数",
        min_value=1,
        max_value=30,
        value=5,
        step=1
    )

    min_stock_gain = st.number_input(
        "最低连续涨幅 %",
        min_value=0.0,
        max_value=100.0,
        value=3.0,
        step=1.0
    )

    max_stock_gain = st.number_input(
        "最高连续涨幅 %",
        min_value=0.0,
        max_value=100.0,
        value=20.0,
        step=1.0
    )

    st.info(
        f"""
当前筛选条件：

- 行业20日涨幅：{min_industry_gain}% ～ {max_industry_gain}%
- 个股连续上涨：≥ {min_rise_days} 天
- 个股连续涨幅：{min_stock_gain}% ～ {max_stock_gain}%
- 排除 ST / *ST
"""
    )

    if st.button("开始筛选", type="primary", key="momentum_button"):

        if min_industry_gain > max_industry_gain:
            st.error("行业最低涨幅不能高于最高涨幅")

        elif min_stock_gain > max_stock_gain:
            st.error("个股最低涨幅不能高于最高涨幅")

        else:

            with st.spinner("正在获取最新行情并筛选，请稍候..."):

                try:

                    result = run_strategy(
                        min_industry_gain=min_industry_gain,
                        max_industry_gain=max_industry_gain,
                        min_rise_days=min_rise_days,
                        min_stock_gain=min_stock_gain,
                        max_stock_gain=max_stock_gain
                    )

                    if result.empty:

                        st.warning("当前没有符合条件的股票")

                    else:

                        st.success(
                            f"筛选完成，共找到 {len(result)} 只股票"
                        )

                        st.dataframe(
                            result,
                            use_container_width=True,
                            hide_index=True
                        )

                        csv = result.to_csv(
                            index=False
                        ).encode("utf-8-sig")

                        st.download_button(
                            "下载筛选结果",
                            data=csv,
                            file_name="强势股筛选结果.csv",
                            mime="text/csv"
                        )

                except Exception as e:

                    st.error(f"筛选失败：{e}")


# =========================================================
# 策略2：行业轮动
# =========================================================
elif strategy_name == "行业轮动":

    st.subheader("行业轮动策略")

    rotation_min_industry_gain = st.number_input(
        "行业20日最低涨幅 %",
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=1.0,
        key="rotation_min_industry_gain"
    )

    rotation_max_industry_gain = st.number_input(
        "行业20日最高涨幅 %",
        min_value=0.0,
        max_value=100.0,
        value=20.0,
        step=1.0,
        key="rotation_max_industry_gain"
    )

    top_industries = st.number_input(
        "选择最强行业数量",
        min_value=1,
        max_value=30,
        value=5,
        step=1
    )

    rotation_min_rise_days = st.number_input(
        "个股最低连涨天数",
        min_value=1,
        max_value=30,
        value=3,
        step=1
    )

    rotation_min_stock_gain = st.number_input(
        "个股最低连续涨幅 %",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=1.0
    )

    rotation_max_stock_gain = st.number_input(
        "个股最高连续涨幅 %",
        min_value=0.0,
        max_value=100.0,
        value=30.0,
        step=1.0
    )

    stocks_per_industry = st.number_input(
        "每个行业最多保留股票数量",
        min_value=1,
        max_value=20,
        value=2,
        step=1
    )

    st.info(
        f"""
当前筛选条件：

- 行业20日涨幅：{rotation_min_industry_gain}% ～ {rotation_max_industry_gain}%
- 选择最强行业：前 {top_industries} 个
- 个股连续上涨：≥ {rotation_min_rise_days} 天
- 个股连续涨幅：{rotation_min_stock_gain}% ～ {rotation_max_stock_gain}%
- 每个行业最多保留：{stocks_per_industry} 只
- 排除 ST / *ST
"""
    )

    if st.button("开始筛选", type="primary", key="rotation_button"):

        if rotation_min_industry_gain > rotation_max_industry_gain:
            st.error("行业最低涨幅不能高于最高涨幅")

        elif rotation_min_stock_gain > rotation_max_stock_gain:
            st.error("个股最低涨幅不能高于最高涨幅")

        else:

            with st.spinner("正在获取最新行业与个股数据，请稍候..."):

                try:

                    result = run_rotation(
                        min_industry_gain=rotation_min_industry_gain,
                        max_industry_gain=rotation_max_industry_gain,
                        min_rise_days=rotation_min_rise_days,
                        min_stock_gain=rotation_min_stock_gain,
                        max_stock_gain=rotation_max_stock_gain,
                        top_industries=top_industries,
                        stocks_per_industry=stocks_per_industry
                    )

                    if result.empty:

                        st.warning("当前没有符合条件的股票")

                    else:

                        st.success(
                            f"筛选完成，共找到 {len(result)} 只股票"
                        )

                        st.dataframe(
                            result,
                            use_container_width=True,
                            hide_index=True
                        )

                        csv = result.to_csv(
                            index=False
                        ).encode("utf-8-sig")

                        st.download_button(
                            "下载筛选结果",
                            data=csv,
                            file_name="行业轮动筛选结果.csv",
                            mime="text/csv"
                        )

                except Exception as e:

                    st.error(f"筛选失败：{e}")


# =========================================================
# 策略3：业绩反转
# =========================================================
elif strategy_name == "业绩反转":

    st.subheader("业绩反转策略")

    min_revenue_growth = st.number_input(
        "最低营收同比增速 %",
        min_value=-100.0,
        max_value=500.0,
        value=10.0,
        step=5.0
    )

    min_profit_growth = st.number_input(
        "最低净利润同比增速 %",
        min_value=-100.0,
        max_value=1000.0,
        value=30.0,
        step=5.0
    )

    min_acceleration = st.number_input(
        "最低业绩改善强度（百分点）",
        min_value=0.0,
        max_value=500.0,
        value=20.0,
        step=5.0
    )

    st.info(
        f"""
当前筛选条件：

- 营收同比：≥ {min_revenue_growth}%
- 净利润同比：≥ {min_profit_growth}%
- 业绩改善强度：≥ {min_acceleration} 个百分点
- 排除 ST / *ST
"""
    )

    if st.button("开始筛选", type="primary", key="reversal_button"):

        with st.spinner("正在获取最新财务数据并筛选，请稍候..."):

            try:

                result = run_reversal(
                    min_revenue_growth=min_revenue_growth,
                    min_profit_growth=min_profit_growth,
                    min_acceleration=min_acceleration
                )

                if result.empty:

                    st.warning("当前没有符合条件的股票")

                else:

                    st.success(
                        f"筛选完成，共找到 {len(result)} 只股票"
                    )

                    st.dataframe(
                        result,
                        use_container_width=True,
                        hide_index=True
                    )

                    csv = result.to_csv(
                        index=False
                    ).encode("utf-8-sig")

                    st.download_button(
                        "下载筛选结果",
                        data=csv,
                        file_name="业绩反转筛选结果.csv",
                        mime="text/csv"
                    )

            except Exception as e:

                st.error(f"筛选失败：{e}")
