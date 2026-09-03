import streamlit as st
import pandas as pd

from 策略.强势股 import run_strategy

st.set_page_config(
    page_title="A股趋势筛选",
    page_icon="📈",
    layout="wide"
)

st.title("A股趋势筛选器")

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

if st.button("开始筛选", type="primary"):

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
