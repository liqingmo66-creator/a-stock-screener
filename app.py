import streamlit as st
import akshare as ak
import pandas as pd

st.set_page_config(
    page_title="A股趋势筛选",
    page_icon="📈",
    layout="wide"
)

st.title("A股趋势筛选器")

st.write("""
当前筛选逻辑：

- 行业近20日涨幅：10%～20%
- 个股连续上涨：≥5天
- 个股连续涨幅：3%～20%
- 排除ST
""")

if st.button("开始筛选", type="primary"):

    with st.spinner("正在获取最新行情，请稍候..."):

        try:
            # 1. 获取行业20日排行
            industry = ak.stock_fund_flow_industry(symbol="20日排行")

            industry["行业20日涨幅"] = (
                industry["阶段涨跌幅"]
                .astype(str)
                .str.replace("%", "", regex=False)
                .astype(float)
            )

            industry = industry[
                (industry["行业20日涨幅"] >= 10) &
                (industry["行业20日涨幅"] <= 20)
            ][["行业", "行业20日涨幅"]]

            # 2. 获取连续上涨股票
            stocks = ak.stock_rank_lxsz_ths()

            stocks["连涨天数"] = pd.to_numeric(
                stocks["连涨天数"],
                errors="coerce"
            )

            stocks["连续涨跌幅"] = pd.to_numeric(
                stocks["连续涨跌幅"],
                errors="coerce"
            )

            stocks = stocks[
                (stocks["连涨天数"] >= 5) &
                (stocks["连续涨跌幅"] >= 3) &
                (stocks["连续涨跌幅"] <= 20) &
                (~stocks["股票简称"].str.contains(
                    "ST",
                    case=False,
                    na=False
                ))
            ]

            # 3. 行业和个股匹配
            result = stocks.merge(
                industry,
                left_on="所属行业",
                right_on="行业",
                how="inner"
            )

            result = result[
                [
                    "股票代码",
                    "股票简称",
                    "所属行业",
                    "行业20日涨幅",
                    "连涨天数",
                    "连续涨跌幅"
                ]
            ]

            # 4. 排序
            result = result.sort_values(
                ["行业20日涨幅", "连续涨跌幅"],
                ascending=False
            )

            st.success(f"筛选完成，共找到 {len(result)} 只股票")

            st.dataframe(
                result,
                use_container_width=True,
                hide_index=True
            )

        except Exception as e:
            st.error("数据获取或筛选失败")
            st.exception(e)
