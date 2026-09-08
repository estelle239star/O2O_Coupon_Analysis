import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from pathlib import Path


# =========================================================
# 1. 页面配置
# =========================================================
st.set_page_config(
    page_title="O2O优惠券精准营销分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# 2. 项目路径
# =========================================================
BASE_DIR = Path(__file__).resolve().parent

TABLE_DIR = BASE_DIR / "output" / "tables"
FIGURE_DIR = BASE_DIR / "output" / "figures"


# =========================================================
# 3. Matplotlib 中文字体
# =========================================================

# Streamlit Cloud / Linux 中 fonts-noto-cjk 常见字体位置
FONT_CANDIDATES = [
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
    Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
]

CN_FONT = None

# 先尝试固定路径
for font_path in FONT_CANDIDATES:
    if font_path.exists():
        CN_FONT = font_manager.FontProperties(
            fname=str(font_path)
        )
        break

# 如果固定路径没找到，再扫描系统字体
if CN_FONT is None:

    system_fonts = font_manager.findSystemFonts(
        fontpaths=None,
        fontext="ttf"
    )

    for font_path in system_fonts:

        font_lower = font_path.lower()

        if (
            "notosanscjk" in font_lower
            or "notoserifcjk" in font_lower
            or "sourcehansans" in font_lower
            or "sourcehanserif" in font_lower
        ):
            CN_FONT = font_manager.FontProperties(
                fname=font_path
            )
            break

# Windows 本地兜底
if CN_FONT is None:
    CN_FONT = font_manager.FontProperties(
        family="Microsoft YaHei"
    )

plt.rcParams["axes.unicode_minus"] = False


def set_cn_font(
    ax,
    title=None,
    xlabel=None,
    ylabel=None
):
    """
    给 Matplotlib 图中的所有文字强制设置中文字体
    """

    if title is not None:
        ax.set_title(
            title,
            fontproperties=CN_FONT,
            fontsize=13
        )

    if xlabel is not None:
        ax.set_xlabel(
            xlabel,
            fontproperties=CN_FONT
        )

    if ylabel is not None:
        ax.set_ylabel(
            ylabel,
            fontproperties=CN_FONT
        )

    for label in ax.get_xticklabels():
        label.set_fontproperties(CN_FONT)

    for label in ax.get_yticklabels():
        label.set_fontproperties(CN_FONT)


# =========================================================
# 4. 页面样式
# =========================================================
st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }

    [data-testid="stMetric"] {
        background-color: #f7f9fc;
        border: 1px solid #e6e9ef;
        padding: 16px;
        border-radius: 12px;
    }

    [data-testid="stSidebar"] {
        min-width: 250px;
    }

    h1 {
        font-weight: 700;
    }

    h2 {
        margin-top: 0.8rem;
    }

    h3 {
        margin-top: 0.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 5. 数据读取
# =========================================================
@st.cache_data
def load_data():

    valid_model = pd.read_csv(
        TABLE_DIR / "dashboard_data.csv"
    )

    model_comparison = pd.read_csv(
        TABLE_DIR / "model_comparison.csv"
    )

    topk_results = pd.read_csv(
        TABLE_DIR / "topk_marketing_results.csv"
    )

    feature_importance = pd.read_csv(
        TABLE_DIR / "lgb_feature_importance.csv"
    )

    strategy_summary = pd.read_csv(
        TABLE_DIR / "business_strategy_summary.csv"
    )

    return (
        valid_model,
        model_comparison,
        topk_results,
        feature_importance,
        strategy_summary
    )


try:

    (
        valid_model,
        model_comparison,
        topk_results,
        feature_importance,
        strategy_summary
    ) = load_data()

except Exception as e:

    st.error(
        "数据读取失败，请检查 output/tables 文件。"
    )

    st.exception(e)

    st.stop()


# =========================================================
# 6. 基础指标
# =========================================================
sample_count = len(valid_model)

redeem_count = int(
    valid_model["label"].sum()
)

baseline_rate = (
    valid_model["label"].mean()
)

top10_rate = (
    topk_results.iloc[0]["实际核销率"]
    if len(topk_results) > 0
    else 0
)


# =========================================================
# 7. 特征中文映射
# =========================================================
FEATURE_NAME_MAP = {

    "merchant_mature_coupon_count":
        "商户历史优惠券数量",

    "receive_day":
        "领券日期",

    "merchant_mature_redeem_rate":
        "商户历史核销率",

    "merchant_mature_redeem_count":
        "商户历史核销次数",

    "distance_value":
        "用户与商户距离",

    "coupon_mature_receive_count":
        "优惠券历史领取量",

    "discount_rate_value":
        "实际折扣力度",

    "discount_threshold":
        "满减门槛",

    "receive_month":
        "领券月份",

    "user_mature_coupon_count":
        "用户历史领券次数",

    "coupon_mature_redeem_rate":
        "优惠券历史核销率",

    "coupon_mature_redeem_count":
        "优惠券历史核销次数",

    "receive_weekday":
        "领券星期",

    "user_mature_redeem_rate":
        "用户历史核销率",

    "distance_missing":
        "距离缺失标记",

    "user_mature_redeem_count":
        "用户历史核销次数",

    "is_manjian":
        "是否满减",

    "is_weekend":
        "是否周末",

    "discount_reduction":
        "优惠减免金额"
}


# =========================================================
# 8. 侧边栏
# =========================================================
st.sidebar.title(
    "📊 O2O精准营销"
)

st.sidebar.caption(
    "数据分析项目 Dashboard"
)

page = st.sidebar.radio(
    "页面导航",
    [
        "🏠 项目总览",
        "🎟️ 优惠券分析",
        "👥 用户行为分析",
        "🤖 模型效果",
        "🎯 精准营销",
        "💡 营销策略"
    ]
)

st.sidebar.divider()

st.sidebar.markdown(
    """
    **项目主题**

    O2O用户消费行为分析与  
    优惠券精准营销策略优化

    **核心流程**

    数据清洗 → EDA → 特征工程 →  
    机器学习 → 高潜样本识别 →  
    精准营销策略
    """
)


# =========================================================
# 9. 项目总览
# =========================================================
if page == "🏠 项目总览":

    st.title(
        "O2O优惠券精准营销分析"
    )

    st.markdown(
        """
        基于O2O优惠券消费数据，从**用户行为、优惠券属性、
        消费场景和历史行为**等维度进行分析，
        并结合机器学习模型识别高核销倾向样本，
        最终形成可执行的精准营销策略。
        """
    )

    st.divider()

    st.header(
        "📌 核心成果"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "验证集样本",
        f"{sample_count:,}"
    )

    col2.metric(
        "实际核销样本",
        f"{redeem_count:,}"
    )

    col3.metric(
        "整体核销率",
        f"{baseline_rate:.2%}"
    )

    col4.metric(
        "Top 10%核销率",
        f"{top10_rate:.2%}"
    )

    st.caption(
        "Top 10%高潜样本核销率明显高于整体水平，"
        "说明模型具有较好的高潜样本识别能力。"
    )

    st.divider()

    st.header(
        "🔍 项目方法"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.subheader(
            "① 数据分析"
        )

        st.markdown(
            """
            - 数据清洗与标签构建
            - 用户消费行为分析
            - 优惠券属性分析
            - 消费距离分析
            """
        )

    with col2:

        st.subheader(
            "② 机器学习"
        )

        st.markdown(
            """
            - 无泄漏历史特征构建
            - Logistic Regression
            - Random Forest
            - LightGBM
            """
        )

    with col3:

        st.subheader(
            "③ 精准营销"
        )

        st.markdown(
            """
            - 高潜样本排序
            - Top-K营销分析
            - Lift与捕获率
            - 差异化用户运营
            """
        )

    st.divider()

    st.header(
        "💡 核心业务发现"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.success(
            f"""
            **高潜用户**

            整体核销率：**{baseline_rate:.2%}**

            Top 10%高潜样本核销率：
            **{top10_rate:.2%}**

            模型排序能够显著提高目标用户筛选效率。
            """
        )

        st.info(
            """
            **用户历史行为**

            历史核销次数越多的用户，
            后续核销率整体越高，
            因此用户历史行为是重要的营销分层依据。
            """
        )

    with col2:

        st.warning(
            """
            **优惠券设计**

            更大的折扣力度并不一定对应更高的核销率。

            优惠力度与使用门槛需要综合设计。
            """
        )

        st.info(
            """
            **消费距离**

            距离较近的消费场景整体具有更高的核销表现，
            可用于场景化精准触达。
            """
        )


# =========================================================
# 10. 优惠券分析
# =========================================================
elif page == "🎟️ 优惠券分析":

    st.title(
        "🎟️ 优惠券策略分析"
    )

    st.markdown(
        """
        从**满减门槛、折扣力度和消费距离**
        三个角度分析优惠券核销表现。
        """
    )

    st.divider()

    # -----------------------------------------------------
    # 10.1 满减门槛
    # -----------------------------------------------------
    st.header(
        "1. 满减门槛与核销表现"
    )

    threshold_analysis = (
        valid_model[
            valid_model["is_manjian"] == 1
        ]
        .groupby("discount_threshold")
        .agg(
            样本数=("label", "size"),
            核销数=("label", "sum"),
            核销率=("label", "mean")
        )
        .reset_index()
        .sort_values(
            "discount_threshold"
        )
    )

    threshold_analysis = (
        threshold_analysis[
            threshold_analysis["样本数"] >= 100
        ]
    )

    col1, col2 = st.columns(
        [1.5, 1]
    )

    with col1:

        fig, ax = plt.subplots(
            figsize=(7.5, 4.2)
        )

        ax.bar(
            threshold_analysis[
                "discount_threshold"
            ].astype(str),

            threshold_analysis[
                "核销率"
            ] * 100
        )

        set_cn_font(
            ax,
            title="不同满减门槛的优惠券核销率",
            xlabel="满减门槛",
            ylabel="核销率（%）"
        )

        plt.tight_layout()

        st.pyplot(
            fig,
            use_container_width=True
        )

        plt.close(fig)

    with col2:

        threshold_display = (
            threshold_analysis.copy()
        )

        threshold_display["核销率"] = (
            threshold_display["核销率"]
            * 100
        ).round(2)

        threshold_display = (
            threshold_display.rename(
                columns={
                    "discount_threshold":
                        "满减门槛"
                }
            )
        )

        st.dataframe(
            threshold_display,
            use_container_width=True,
            hide_index=True
        )

    st.info(
        """
        **结论：**
        较低或适中的满减门槛整体具有更好的核销表现，
        过高门槛可能降低优惠券实际使用概率。
        """
    )

    st.divider()

    # -----------------------------------------------------
    # 10.2 折扣力度
    # -----------------------------------------------------
    st.header(
        "2. 优惠力度与核销表现"
    )

    discount_analysis = (
        valid_model.copy()
    )

    discount_analysis[
        "discount_group"
    ] = pd.cut(
        discount_analysis[
            "discount_rate_value"
        ],
        bins=[
            0,
            0.6,
            0.7,
            0.8,
            0.9,
            1.0
        ],
        labels=[
            "≤6折",
            "6-7折",
            "7-8折",
            "8-9折",
            "9-10折"
        ],
        include_lowest=True
    )

    discount_summary = (
        discount_analysis
        .groupby(
            "discount_group",
            observed=True
        )
        .agg(
            样本数=("label", "size"),
            核销数=("label", "sum"),
            核销率=("label", "mean")
        )
        .reset_index()
    )

    col1, col2 = st.columns(
        [1.5, 1]
    )

    with col1:

        fig, ax = plt.subplots(
            figsize=(7.5, 4.2)
        )

        ax.bar(
            discount_summary[
                "discount_group"
            ].astype(str),

            discount_summary[
                "核销率"
            ] * 100
        )

        set_cn_font(
            ax,
            title="不同折扣区间的优惠券核销率",
            xlabel="折扣区间",
            ylabel="核销率（%）"
        )

        plt.tight_layout()

        st.pyplot(
            fig,
            use_container_width=True
        )

        plt.close(fig)

    with col2:

        discount_display = (
            discount_summary.copy()
        )

        discount_display["核销率"] = (
            discount_display["核销率"]
            * 100
        ).round(2)

        discount_display = (
            discount_display.rename(
                columns={
                    "discount_group":
                        "折扣区间"
                }
            )
        )

        st.dataframe(
            discount_display,
            use_container_width=True,
            hide_index=True
        )

    st.info(
        """
        **结论：**
        折扣力度与核销率并不存在简单的单调关系，
        因此优惠券设计不能单纯依靠增加折扣力度。
        """
    )

    st.divider()

    # -----------------------------------------------------
    # 10.3 消费距离
    # -----------------------------------------------------
    st.header(
        "3. 消费距离与核销表现"
    )

    distance_summary = (
        valid_model[
            valid_model[
                "distance_missing"
            ] == 0
        ]
        .groupby(
            "distance_value"
        )
        .agg(
            样本数=("label", "size"),
            核销数=("label", "sum"),
            核销率=("label", "mean")
        )
        .reset_index()
        .sort_values(
            "distance_value"
        )
    )

    col1, col2 = st.columns(
        [1.6, 1]
    )

    with col1:

        fig, ax = plt.subplots(
            figsize=(7.5, 4.2)
        )

        ax.plot(
            distance_summary[
                "distance_value"
            ],

            distance_summary[
                "核销率"
            ] * 100,

            marker="o"
        )

        set_cn_font(
            ax,
            title="消费距离与优惠券核销率",
            xlabel="消费距离",
            ylabel="核销率（%）"
        )

        plt.tight_layout()

        st.pyplot(
            fig,
            use_container_width=True
        )

        plt.close(fig)

    with col2:

        distance_display = (
            distance_summary.copy()
        )

        distance_display["核销率"] = (
            distance_display["核销率"]
            * 100
        ).round(2)

        distance_display = (
            distance_display.rename(
                columns={
                    "distance_value":
                        "消费距离"
                }
            )
        )

        st.dataframe(
            distance_display,
            use_container_width=True,
            hide_index=True
        )

    st.info(
        """
        **结论：**
        距离较近的消费场景整体具有更高的优惠券核销率，
        因此消费距离可作为场景化营销的重要参考。
        """
    )


# =========================================================
# 11. 用户行为分析
# =========================================================
elif page == "👥 用户行为分析":

    st.title(
        "👥 用户行为分析"
    )

    st.markdown(
        """
        使用预测时点之前已经成熟的历史行为，
        对用户营销价值进行分层分析。
        """
    )

    st.divider()

    # -----------------------------------------------------
    # 11.1 历史活跃度
    # -----------------------------------------------------
    st.header(
        "1. 用户历史活跃度"
    )

    user_analysis = (
        valid_model.copy()
    )

    user_analysis[
        "user_activity_group"
    ] = pd.cut(
        user_analysis[
            "user_mature_coupon_count"
        ],
        bins=[
            -1,
            0,
            3,
            float("inf")
        ],
        labels=[
            "无历史记录",
            "低/中活跃用户",
            "高活跃用户"
        ]
    )

    activity_summary = (
        user_analysis
        .groupby(
            "user_activity_group",
            observed=True
        )
        .agg(
            样本数=("label", "size"),
            核销数=("label", "sum"),
            核销率=("label", "mean")
        )
        .reset_index()
    )

    col1, col2 = st.columns(
        [1.4, 1]
    )

    with col1:

        fig, ax = plt.subplots(
            figsize=(7, 4)
        )

        ax.bar(
            activity_summary[
                "user_activity_group"
            ].astype(str),

            activity_summary[
                "核销率"
            ] * 100
        )

        set_cn_font(
            ax,
            title="不同历史活跃度用户核销率",
            xlabel="用户类型",
            ylabel="核销率（%）"
        )

        plt.tight_layout()

        st.pyplot(
            fig,
            use_container_width=True
        )

        plt.close(fig)

    with col2:

        activity_display = (
            activity_summary.copy()
        )

        activity_display["核销率"] = (
            activity_display["核销率"]
            * 100
        ).round(2)

        activity_display = (
            activity_display.rename(
                columns={
                    "user_activity_group":
                        "用户类型"
                }
            )
        )

        st.dataframe(
            activity_display,
            use_container_width=True,
            hide_index=True
        )

    st.info(
        """
        高活跃用户整体具有更高的优惠券核销率，
        历史领券活跃度可以作为用户筛选的重要参考。
        """
    )

    st.divider()

    # -----------------------------------------------------
    # 11.2 历史核销
    # -----------------------------------------------------
    st.header(
        "2. 用户历史核销表现"
    )

    redeem_analysis = (
        valid_model.copy()
    )

    redeem_analysis[
        "user_redeem_group"
    ] = pd.cut(
        redeem_analysis[
            "user_mature_redeem_count"
        ],
        bins=[
            -1,
            0,
            2,
            float("inf")
        ],
        labels=[
            "无历史核销",
            "历史核销1-2次",
            "历史核销3次及以上"
        ]
    )

    redeem_summary = (
        redeem_analysis
        .groupby(
            "user_redeem_group",
            observed=True
        )
        .agg(
            样本数=("label", "size"),
            核销数=("label", "sum"),
            核销率=("label", "mean")
        )
        .reset_index()
    )

    col1, col2 = st.columns(
        [1.4, 1]
    )

    with col1:

        fig, ax = plt.subplots(
            figsize=(7, 4)
        )

        ax.bar(
            redeem_summary[
                "user_redeem_group"
            ].astype(str),

            redeem_summary[
                "核销率"
            ] * 100
        )

        set_cn_font(
            ax,
            title="不同历史核销用户的当前核销率",
            xlabel="用户类型",
            ylabel="当前核销率（%）"
        )

        plt.tight_layout()

        st.pyplot(
            fig,
            use_container_width=True
        )

        plt.close(fig)

    with col2:

        redeem_display = (
            redeem_summary.copy()
        )

        redeem_display["核销率"] = (
            redeem_display["核销率"]
            * 100
        ).round(2)

        redeem_display = (
            redeem_display.rename(
                columns={
                    "user_redeem_group":
                        "用户类型"
                }
            )
        )

        st.dataframe(
            redeem_display,
            use_container_width=True,
            hide_index=True
        )

    st.success(
        """
        **关键发现：**

        具有多次历史核销记录的用户表现出明显更高的再次核销倾向，
        是精准营销中的重点用户群体。
        """
    )


# =========================================================
# 12. 模型效果
# =========================================================
elif page == "🤖 模型效果":

    st.title(
        "🤖 机器学习模型效果"
    )

    st.markdown(
        """
        比较 Logistic Regression、Random Forest 和 LightGBM
        在时间验证集上的预测表现。
        """
    )

    st.divider()

    st.header(
        "1. 模型指标对比"
    )

    st.dataframe(
        model_comparison,
        use_container_width=True,
        hide_index=True
    )

    auc_candidates = [
        col
        for col in model_comparison.columns
        if "auc" in col.lower()
    ]

    if len(auc_candidates) > 0:

        auc_col = (
            auc_candidates[0]
        )

        model_col = (
            model_comparison.columns[0]
        )

        chart_data = (
            model_comparison[
                [
                    model_col,
                    auc_col
                ]
            ].copy()
        )

        fig, ax = plt.subplots(
            figsize=(8, 4)
        )

        ax.bar(
            chart_data[model_col],
            chart_data[auc_col]
        )

        set_cn_font(
            ax,
            title="ROC-AUC 对比",
            xlabel="模型",
            ylabel="ROC-AUC"
        )

        plt.tight_layout()

        st.pyplot(
            fig,
            use_container_width=True
        )

        plt.close(fig)

    st.info(
        """
        **模型结果说明**

        - Random Forest 的 ROC-AUC 最高，整体概率排序能力较强；
        - LightGBM 在 Accuracy 和 Precision 上表现较好；
        - 后续高潜样本识别、Top-K营销分析和特征重要性分析均基于 LightGBM 完成。

        因此，本项目不将 LightGBM 定义为所有指标下的“最优模型”，
        而是将其作为后续业务分析与精准营销策略的主要模型。
        """
    )

    st.divider()

    # -----------------------------------------------------
    # 12.2 LightGBM 特征重要性
    # -----------------------------------------------------
    st.header(
        "2. LightGBM 特征重要性"
    )

    feature_data = (
        feature_importance.copy()
    )

    feature_col = (
        feature_data.columns[0]
    )

    importance_col = (
        feature_data.columns[1]
    )

    feature_data[
        "feature_cn"
    ] = (
        feature_data[
            feature_col
        ]
        .map(
            FEATURE_NAME_MAP
        )
        .fillna(
            feature_data[
                feature_col
            ]
        )
    )

    feature_data = (
        feature_data
        .sort_values(
            importance_col,
            ascending=False
        )
        .head(10)
        .sort_values(
            importance_col,
            ascending=True
        )
    )

    fig, ax = plt.subplots(
        figsize=(8, 5.5)
    )

    ax.barh(
        feature_data[
            "feature_cn"
        ],
        feature_data[
            importance_col
        ]
    )

    set_cn_font(
        ax,
        title="LightGBM Top 10 特征重要性",
        xlabel="重要性",
        ylabel="特征"
    )

    plt.tight_layout()

    st.pyplot(
        fig,
        use_container_width=True
    )

    plt.close(fig)

    st.caption(
        "特征重要性反映模型建树过程中对不同变量的使用程度，"
        "不代表因果关系。"
    )


# =========================================================
# 13. 精准营销
# =========================================================
elif page == "🎯 精准营销":

    st.title(
        "🎯 高潜样本与精准营销"
    )

    st.markdown(
        """
        基于 LightGBM 输出的核销概率对验证集样本进行排序，
        比较不同 Top-K 营销范围下的核销率、
        Lift 和核销用户捕获率。
        """
    )

    st.divider()

    st.header(
        "1. Top-K 营销效果"
    )

    cols = st.columns(
        len(topk_results)
    )

    for i, (_, row) in enumerate(
        topk_results.iterrows()
    ):

        with cols[i]:

            st.metric(
                str(
                    row["Top比例"]
                ),
                f'{row["实际核销率"]:.2%}',
                f'Lift {row["Lift"]:.2f}'
            )

            st.caption(
                f'捕获率：'
                f'{row["核销用户捕获率"]:.2%}'
            )

    st.divider()

    st.header(
        "2. 营销范围对比"
    )

    col1, col2 = st.columns(
        [1.5, 1]
    )

    with col1:

        plot_data = pd.DataFrame(
            {
                "触达范围": (
                    ["整体样本"]
                    +
                    topk_results[
                        "Top比例"
                    ].tolist()
                ),

                "核销率": (
                    [baseline_rate]
                    +
                    topk_results[
                        "实际核销率"
                    ].tolist()
                )
            }
        )

        fig, ax = plt.subplots(
            figsize=(7.5, 4.2)
        )

        bars = ax.bar(
            plot_data[
                "触达范围"
            ],

            plot_data[
                "核销率"
            ] * 100
        )

        set_cn_font(
            ax,
            title="不同营销触达范围的实际核销率",
            xlabel="触达范围",
            ylabel="实际核销率（%）"
        )

        for bar, value in zip(
            bars,
            plot_data[
                "核销率"
            ]
        ):

            ax.text(
                bar.get_x()
                + bar.get_width() / 2,

                bar.get_height(),

                f"{value:.2%}",

                ha="center",
                va="bottom",

                fontproperties=CN_FONT
            )

        plt.tight_layout()

        st.pyplot(
            fig,
            use_container_width=True
        )

        plt.close(fig)

    with col2:

        topk_display = (
            topk_results.copy()
        )

        topk_display[
            "实际核销率"
        ] = (
            topk_display[
                "实际核销率"
            ]
            * 100
        ).round(2)

        topk_display[
            "核销用户捕获率"
        ] = (
            topk_display[
                "核销用户捕获率"
            ]
            * 100
        ).round(2)

        topk_display[
            "Lift"
        ] = (
            topk_display[
                "Lift"
            ].round(2)
        )

        st.dataframe(
            topk_display,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.header(
        "3. 营销决策建议"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.success(
            """
            ### 💰 预算有限

            **优先 Top 10%**

            - 核销率约 25.29%
            - Lift约 2.52
            - 聚焦最高潜用户
            """
        )

    with col2:

        st.info(
            """
            ### ⚖️ 效率 + 覆盖

            **优先 Top 20%**

            - 核销率约 20.67%
            - 捕获约 41.25% 核销样本
            - 推荐作为主要触达范围
            """
        )

    with col3:

        st.warning(
            """
            ### 📢 扩大覆盖

            **Top 30%**

            - 捕获约 55.39% 核销样本
            - Lift约 1.85
            - 覆盖更广但效率下降
            """
        )


# =========================================================
# 14. 营销策略
# =========================================================
elif page == "💡 营销策略":

    st.title(
        "💡 综合精准营销策略"
    )

    st.markdown(
        """
        综合模型预测、用户历史行为、
        优惠券属性和消费场景，
        将分析结果转化为可执行的营销策略。
        """
    )

    st.divider()

    st.header(
        "📋 营销策略汇总"
    )

    st.dataframe(
        strategy_summary,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.header(
        "🎯 最终策略框架"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.success(
            """
            ### ① 用户筛选

            - 预算有限：优先 Top 10%
            - 兼顾效率与覆盖：优先 Top 20%
            - 历史多次核销用户重点维护
            """
        )

        st.info(
            """
            ### ② 优惠券设计

            - 结合折扣力度和满减门槛
            - 不单纯追求更大折扣
            - 根据用户行为设计差异化优惠
            """
        )

    with col2:

        st.warning(
            """
            ### ③ 场景化营销

            - 优先距离较近的高潜用户
            - 结合模型概率和距离排序
            - 降低低效率广泛触达
            """
        )

        st.success(
            """
            ### ④ 用户差异化运营

            **高价值用户：**
            重点维护和优先触达

            **普通活跃用户：**
            使用适度优惠促进转化

            **无历史行为用户：**
            使用低成本优惠试探性触达
            """
        )

    st.divider()

    st.header(
        "📌 项目最终结论"
    )

    st.markdown(
        f"""
        验证集整体核销率为
        **{baseline_rate:.2%}**，

        LightGBM筛选出的 Top 10% 高潜样本核销率达到
        **{top10_rate:.2%}**。

        项目结果表明，结合
        **模型预测概率 + 用户历史行为 + 优惠券属性 + 消费距离**
        可以形成更精细的用户筛选和营销资源配置策略。

        相比无差别营销，该方法能够更有效地识别高核销倾向样本，
        为优惠券精准营销和差异化运营提供数据支持。
        """
    )