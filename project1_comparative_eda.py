import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 한글 폰트 설정 (Windows 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def perform_comparative_eda(file_path):
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return

    # 데이터 로드
    df = pd.read_csv(file_path)
    
    # 1. 데이터 전처리
    price_cols = ['실결제 금액', '결제금액', '판매단가', '공급단가']
    for col in price_cols:
        if col in df.columns and df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
        elif col in df.columns:
            df[col] = df[col].astype(float)

    df['주문일'] = pd.to_datetime(df['주문일'])
    df['주문일자'] = df['주문일'].dt.date
    
    # 그룹 분리: 킹댕즈 vs 나머지
    df['그룹'] = df['셀러명'].apply(lambda x: '킹댕즈' if x == '킹댕즈' else '나머지 셀러')
    
    df_king = df[df['그룹'] == '킹댕즈']
    df_others = df[df['그룹'] == '나머지 셀러']

    print(f"--- 데이터 분리 완료 ---")
    print(f"킹댕즈 주문건수: {len(df_king)}건, 총 매출: {df_king['실결제 금액'].sum():,.0f}원")
    print(f"나머지 셀러 주문건수: {len(df_others)}건, 총 매출: {df_others['실결제 금액'].sum():,.0f}원")

    # 1. 시계열 추이 비교
    plt.figure(figsize=(12, 6))
    df.groupby(['주문일자', '그룹'])['실결제 금액'].sum().unstack().plot(kind='line', marker='o', ax=plt.gca())
    plt.title('킹댕즈 vs 나머지 셀러 매출 추이 비교')
    plt.ylabel('매출액')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('group_comparison_trend.png')
    plt.close()

    # 2. 나머지 셀러들만의 매출 Top 5 추이 (킹댕즈 제외하고 자세히 보기)
    plt.figure(figsize=(12, 6))
    top_others = df_others.groupby('셀러명')['실결제 금액'].sum().nlargest(5).index
    df_others[df_others['셀러명'].isin(top_others)].groupby(['주문일자', '셀러명'])['실결제 금액'].sum().unstack().plot(kind='line', marker='o', ax=plt.gca())
    plt.title('일반 셀러 Top 5 매출 추이 (킹댕즈 제외)')
    plt.ylabel('매출액')
    plt.grid(True)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('others_top5_trend.png')
    plt.close()

    # 3. 유입 채널 기여도 비교
    channel_comp = df.groupby(['주문경로', '그룹'])['실결제 금액'].sum().unstack().fillna(0)
    print("\n--- 채널별 매출 기여도 비교 ---")
    print(channel_comp)
    
    channel_comp.plot(kind='bar', figsize=(12, 6))
    plt.title('채널별 매출 기여도: 킹댕즈 vs 나머지')
    plt.ylabel('매출액')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('channel_contribution_by_group.png')
    plt.close()

    # 4. 재구매율 비교
    repeat_king = (df_king['재구매 횟수'] > 0).mean() * 100
    repeat_others = (df_others['재구매 횟수'] > 0).mean() * 100
    print(f"\n--- 재구매율 비교 ---")
    print(f"킹댕즈 재구매 비중: {repeat_king:.2f}%")
    print(f"나머지 셀러 재구매 비중: {repeat_others:.2f}%")

    # 5. 품종별 선호도 차이
    print("\n--- 그룹별 주력 품종 Top 3 ---")
    print("[킹댕즈]")
    print(df_king['품종'].value_counts().head(3))
    print("\n[나머지 셀러]")
    print(df_others['품종'].value_counts().head(3))

    # 데이터 요약 저장
    summary = {
        "king_sales": df_king['실결제 금액'].sum(),
        "others_sales": df_others['실결제 금액'].sum(),
        "king_repeat": repeat_king,
        "others_repeat": repeat_others,
        "king_top_channel": df_king.groupby('주문경로')['실결제 금액'].sum().idxmax(),
        "others_top_channel": df_others.groupby('주문경로')['실결제 금액'].sum().idxmax()
    }
    
    with open('comparative_summary.txt', 'w', encoding='utf-8') as f:
        for k, v in summary.items():
            f.write(f"{k}: {v}\n")

if __name__ == "__main__":
    perform_comparative_eda(r"D:\fcicb6\project1 - preprocessed_data.csv")
