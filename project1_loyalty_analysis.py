import pandas as pd
import os
import json

def analyze_loyalty(file_path):
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return

    # 데이터 로드
    df = pd.read_csv(file_path)
    
    # 1. 재구매 고객 정의 (재구매 횟수 > 0)
    repeat_df = df[df['재구매 횟수'] > 0]
    
    # --- 유입경로별 재구매 분석 ---
    # 재구매 주문 건수
    channel_repeat_orders = repeat_df['주문경로'].value_counts()
    # 유입경로별 전체 주문 건수 대비 재구매 주문 비중
    channel_total_orders = df['주문경로'].value_counts()
    channel_repeat_ratio = (channel_repeat_orders / channel_total_orders * 100).fillna(0)
    
    # --- 셀러별 재구매 분석 ---
    # 재구매 주문 건수
    seller_repeat_orders = repeat_df['셀러명'].value_counts()
    # 셀러별 전체 주문 건수 대비 재구매 주문 비중
    seller_total_orders = df['셀러명'].value_counts()
    seller_repeat_ratio = (seller_repeat_orders / seller_total_orders * 100).fillna(0)
    
    # --- 재구매 횟수가 유독 높은 헤비 유저 분석 ---
    heavy_users = df.groupby('UID')['재구매 횟수'].max().nlargest(10)
    
    loyalty_summary = {
        "channel_loyalty": {
            "top_repeat_orders": channel_repeat_orders.head(5).to_dict(),
            "top_repeat_ratio": channel_repeat_ratio.nlargest(5).to_dict()
        },
        "seller_loyalty": {
            "top_repeat_orders": seller_repeat_orders.head(5).to_dict(),
            "top_repeat_ratio": seller_repeat_ratio[seller_total_orders > 50].nlargest(5).to_dict() # 최소 주문 50건 이상 셀러 대상
        },
        "repeat_customer_habits": {
            "top_products": repeat_df['품종'].value_counts().head(5).to_dict(),
            "avg_repeat_count": float(repeat_df['재구매 횟수'].mean())
        }
    }

    # 결과 저장
    with open(r"D:\fcicb6\loyalty_insights.json", "w", encoding="utf-8") as f:
        json.dump(loyalty_summary, f, ensure_ascii=False, indent=4)
        
    print("--- 재구매(로열티) 분석 요약 ---")
    print(f"\n[유입경로별 재구매 비중 Top 3]")
    for path, ratio in channel_repeat_ratio.nlargest(3).items():
        print(f"  - {path}: {ratio:.1f}%")

    print(f"\n[셀러별 재구매 비중 Top 3 (주문 50건 이상 대상)]")
    for seller, ratio in seller_repeat_ratio[seller_total_orders > 50].nlargest(3).items():
        print(f"  - {seller}: {ratio:.1f}%")

if __name__ == "__main__":
    analyze_loyalty(r"D:\fcicb6\project1 - preprocessed_data.csv")
