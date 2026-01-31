import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 한글 폰트 설정 (Windows 기준 Malgun Gothic 사용)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def perform_eda(file_path):
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return

    # 데이터 로드
    df = pd.read_csv(file_path)
    
    # 1. 데이터 전처리
    # 금액 컬럼 숫자형 변환 (콤마 제거)
    price_cols = ['실결제 금액', '결제금액', '판매단가', '공급단가', '주문취소 금액']
    for col in price_cols:
        if col in df.columns and df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
        elif col in df.columns:
            df[col] = df[col].astype(float)

    # 날짜 처리
    df['주문일'] = pd.to_datetime(df['주문일'])
    df['주문일자'] = df['주문일'].dt.date
    
    # 마진 계산 (간이)
    df['마진'] = df['실결제 금액'] - (df['공급단가'] * df['주문-취소 수량'])

    print("--- 1. 셀러별 매출 추이 (Top 5) ---")
    top_sellers = df.groupby('셀러명')['실결제 금액'].sum().nlargest(5).index
    seller_trend = df[df['셀러명'].isin(top_sellers)].groupby(['주문일자', '셀러명'])['실결제 금액'].sum().unstack().fillna(0)
    print(seller_trend.tail())
    
    plt.figure(figsize=(12, 6))
    seller_trend.plot(kind='line', marker='o', ax=plt.gca())
    plt.title('상위 5개 셀러별 일일 매출 추이')
    plt.ylabel('실결제 금액')
    plt.grid(True)
    plt.legend(title='셀러명', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('seller_sales_trend.png')
    plt.close()

    print("\n--- 2. 셀러별 주력 상품 (품종 기준) ---")
    # 셀러별로 품종별 판매수량 합계
    seller_product_strength = df.groupby(['셀러명', '품종'])['주문-취소 수량'].sum().unstack().fillna(0)
    # 상위 10개 셀러만 확인
    top_10_sellers = df.groupby('셀러명')['실결제 금액'].sum().nlargest(10).index
    print(seller_product_strength.loc[top_10_sellers])
    
    plt.figure(figsize=(12, 8))
    seller_product_strength.loc[top_10_sellers].plot(kind='bar', stacked=True, ax=plt.gca())
    plt.title('상위 10개 셀러별 품종별 판매 비량')
    plt.ylabel('판매 수량')
    plt.legend(title='품종', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('seller_product_strength.png')
    plt.close()

    print("\n--- 3. 재구매 고객 분석 ---")
    # 재구매 횟수가 1 이상인 고객
    repeat_customers = df[df['재구매 횟수'] > 0]
    print(f"재구매 고객 수: {repeat_customers['UID'].nunique()}명")
    print("\n재구매 고객의 선호 품종 Top 5:")
    print(repeat_customers['품종'].value_counts().head(5))
    
    print("\n재구매 고객의 주요 유입 경로:")
    print(repeat_customers['주문경로'].value_counts())

    print("\n--- 4. 유입 채널별 매출액과 기여도 ---")
    channel_analysis = df.groupby('주문경로').agg({
        '실결제 금액': 'sum',
        'UID': 'nunique',
        '주문번호': 'count'
    }).rename(columns={'UID': '고객수', '주문번호': '주문건수'})
    channel_analysis['건당결제액'] = channel_analysis['실결제 금액'] / channel_analysis['주문건수']
    print(channel_analysis.sort_values(by='실결제 금액', ascending=False))
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=channel_analysis.index, y=channel_analysis['실결제 금액'])
    plt.title('주문경로별 총 매출액')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('channel_revenue.png')
    plt.close()

    print("\n--- 5. [추가] 지역별 매출 비중 ---")
    region_sales = df.groupby('광역지역(정식)')['실결제 금액'].sum().sort_values(ascending=False)
    print(region_sales.head(10))

    # 최종 리포트 저장용
    summary = {
        "total_revenue": df['실결제 금액'].sum(),
        "total_orders": len(df),
        "top_seller": top_sellers[0],
        "top_channel": channel_analysis['실결제 금액'].idxmax()
    }
    print(f"\n[요약] 전체 매출: {summary['total_revenue']:,.0f}원")
    print(f"[요약] 최고 매출 셀러: {summary['top_seller']}")
    print(f"[요약] 최고 효율 채널: {summary['top_channel']}")

if __name__ == "__main__":
    perform_eda(r"D:\fcicb6\project1 - preprocessed_data.csv")
