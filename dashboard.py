import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# 0. 페이지 설정
st.set_page_config(page_title="고급 주문 데이터 분석 대시보드", layout="wide")

# 1. 데이터 로드 및 전처리
@st.cache_data
def load_data():
    file_path = r"D:\fcicb6\project1 - preprocessed_data.csv"
    if not os.path.exists(file_path):
        return None
    df = pd.read_csv(file_path)
    # 금액 변환
    price_cols = ['실결제 금액', '결제금액', '판매단가', '공급단가']
    for col in price_cols:
        if col in df.columns and df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
    df['주문일'] = pd.to_datetime(df['주문일'])
    # 그룹 분리
    df['그룹'] = df['셀러명'].apply(lambda x: '킹댕즈' if x == '킹댕즈' else '일반 셀러')
    return df

df = load_data()

if df is not None:
    # 2. 사이드바: 그룹 필터 및 정보
    st.sidebar.header("🔍 분석 설정")
    group_choice = st.sidebar.multiselect(
        "분석할 셀러 그룹을 선택하세요", 
        options=['킹댕즈', '일반 셀러'], 
        default=['킹댕즈', '일반 셀러']
    )
    
    # 필터링 데이터 적용
    if not group_choice:
        st.error("최소 한 개의 그룹을 선택해주세요.")
        st.stop()
    
    f_df = df[df['그룹'].isin(group_choice)]

    # 3. 메인 타이틀 및 핵심 지표 (Metrics)
    st.title("🍊 프리미엄 과일 커머스 데이터 분석")
    st.caption("작업지시서 기반 통합 대시보드 (Plotly Interactive)")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("총 매출액", f"₩{f_df['실결제 금액'].sum():,.0f}")
    with m2:
        st.metric("총 주문건수", f"{len(f_df):,}건")
    with m3:
        st.metric("평균 객단가(AOV)", f"₩{(f_df['실결제 금액'].sum()/len(f_df)):,.0f}")
    with m4:
        repeat_rate = (f_df['재구매 횟수'] > 0).mean() * 100
        st.metric("재구매 고객 비중", f"{repeat_rate:.1f}%")

    # 4. 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📉 매출 & 채널 분석", "📊 셀러 & 로열티 분석", "🗺️ 지역별 심층 인사이트", "📋 Raw Data"])

    # --- 탭 1: 매출 & 채널 분석 ---
    with tab1:
        st.header("시계열 및 채널 기여도 분석")
        
        # [그래프 1] 일자별 매출 추이 (Line)
        trend_df = f_df.groupby([f_df['주문일'].dt.date, '그룹'])['실결제 금액'].sum().reset_index()
        fig1 = px.line(trend_df, x='주문일', y='실결제 금액', color='그룹', markers=True, 
                       title="일자별 매출 추이", labels={'주문일': '날짜', '실결제 금액': '매출액'})
        st.plotly_chart(fig1, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            # [그래프 2] 주문 경로별 매출 비중 (Pie)
            ch_rev = f_df.groupby('주문경로')['실결제 금액'].sum().reset_index()
            fig2 = px.pie(ch_rev, values='실결제 금액', names='주문경로', hole=0.4, title="주문 경로별 매출 비중")
            st.plotly_chart(fig2)
        with c2:
            # [그래프 3] 채널별 평균 객단가 (Bar)
            ch_aov = f_df.groupby('주문경로')['실결제 금액'].mean().sort_values(ascending=False).reset_index()
            fig3 = px.bar(ch_aov, x='주문경로', y='실결제 금액', color='주문경로', title="채널별 평균 객단가")
            st.plotly_chart(fig3)

        # [표 1] 채널별 성과 지표 요약
        st.subheader("📝 채널별 성과 지표 요약")
        ch_summary = f_df.groupby('주문경로').agg({
            '실결제 금액': 'sum',
            '주문번호': 'count',
            'UID': 'nunique'
        }).rename(columns={'실결제 금액':'총 매출액', '주문번호':'주문건수', 'UID':'고객수'}).reset_index()
        st.table(ch_summary.sort_values(by='총 매출액', ascending=False))

    # --- 탭 2: 셀러 & 로열티 분석 ---
    with tab2:
        st.header("셀러별 성과 및 고객 충성도")

        c3, c4 = st.columns(2)
        with c3:
            # [그래프 4] 품종별 판매량 Top 10 (Bar)
            prod_rank = f_df['품종'].value_counts().head(10).reset_index()
            fig4 = px.bar(prod_rank, x='품종', y='count', color='품종', title="가장 많이 팔린 품종 Top 10")
            st.plotly_chart(fig4)
        with c4:
            # [그래프 5] 셀러별 매출 성과 (Horizontal Bar)
            sel_perf = f_df.groupby('셀러명')['실결제 금액'].sum().nlargest(15).reset_index()
            fig5 = px.bar(sel_perf, x='실결제 금액', y='셀러명', orientation='h', color='실결제 금액', 
                          title="매출 상위 셀러 현황 (Top 15)")
            st.plotly_chart(fig5)

        st.subheader("🏅 셀러 랭킹 분석")
        c5, c6 = st.columns(2)
        with c5:
            # [표 2] 매출 상위 10개 셀러
            st.write("**[표 2] 매출 상위 10개 셀러**")
            top10_sel = f_df.groupby('셀러명')['실결제 금액'].sum().nlargest(10).reset_index()
            top10_sel.columns = ['셀러명', '총 매출액']
            st.dataframe(top10_sel, use_container_width=True)
        with c6:
            # [표 3] 재구매율 상위 10개 셀러 (최소 30건 주문 이상 대상)
            st.write("**[표 3] 고객 충성도(재구매율) 상위 셀러**")
            s_total = f_df.groupby('셀러명').size()
            s_repeat = f_df[f_df['재구매 횟수'] > 0].groupby('셀러명').size()
            s_ratio = (s_repeat / s_total * 100).fillna(0).loc[s_total[s_total >= 30].index].nlargest(10).reset_index()
            s_ratio.columns = ['셀러명', '재구매율 (%)']
            st.dataframe(s_ratio, use_container_width=True)

    # --- 탭 3: 지역별 심층 인사이트 ---
    with tab3:
        st.header("지역별 수요 및 경로 연계 분석")
        
        # [그래프 6] 지역별 매출 합계 (Bar)
        reg_sales = f_df.groupby('광역지역(정식)')['실결제 금액'].sum().sort_values(ascending=False).reset_index()
        fig6 = px.bar(reg_sales, x='광역지역(정식)', y='실결제 금액', color='실결제 금액', title="광역지역별 총 매출 비중")
        st.plotly_chart(fig6, use_container_width=True)

        st.subheader("🔍 지역별 상세 조합 분석")
        if os.path.exists(r"D:\fcicb6\regional_insights.json"):
            with open(r"D:\fcicb6\regional_insights.json", "r", encoding="utf-8") as f:
                reg_json = json.load(f)
            
            sel_reg = st.selectbox("심층 분석할 지역 선택", options=list(reg_json.keys()))
            if sel_reg:
                detail = reg_json[sel_reg]
                # [표 4] 지역별 베스트 조합표
                st.write(f"**[표 4] {sel_reg} 지역 베스트 [경로 x 셀러] 조합**")
                st.table(detail['상위조합'])
        else:
            st.warning("지역 연계 분석 데이터(JSON)가 없습니다. 분석 스크립트를 먼저 실행해주세요.")

    # --- 탭 4: Raw Data ---
    with tab4:
        st.header("전체 데이터 샘플 및 미리보기")
        # [표 5] 최근 주문 데이터 샘플
        st.write("**[표 5] 최근 주문 데이터 샘플 (최근 50건)**")
        raw_preview = f_df.sort_values(by='주문일', ascending=False).head(50)
        st.dataframe(raw_preview, use_container_width=True)

else:
    st.error("데이터 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
