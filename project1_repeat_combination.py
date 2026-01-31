import pandas as pd
import os
import json

def analyze_repeat_combinations(file_path):
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return

    # 데이터 로드
    df = pd.read_csv(file_path)
    
    # 1. 재구매 데이터만 필터링 (재구매 횟수 > 0)
    repeat_df = df[df['재구매 횟수'] > 0].copy()
    
    # 2. 재구매가 가장 많은 채널 확인
    top_repeat_channel = repeat_df['주문경로'].value_counts().idxmax()
    top_repeat_channel_count = repeat_df['주문경로'].value_counts().max()
    
    # 3. [주문경로 x 셀러명] 조합 분석
    path_seller_combo = repeat_df.groupby(['주문경로', '셀러명']).size().reset_index(name='재구매건수')
    top_path_seller = path_seller_combo.sort_values(by='재구매건수', ascending=False).head(10)
    
    # 4. [주문경로 x 광역지역] 조합 분석
    path_region_combo = repeat_df.groupby(['주문경로', '광역지역(정식)']).size().reset_index(name='재구매건수')
    top_path_region = path_region_combo.sort_values(by='재구매건수', ascending=False).head(10)

    # 5. [주문경로 x 품종] 조합 분석
    path_product_combo = repeat_df.groupby(['주문경로', '품종']).size().reset_index(name='재구매건수')
    top_path_product = path_product_combo.sort_values(by='재구매건수', ascending=False).head(10)

    result = {
        "best_channel": {
            "name": top_repeat_channel,
            "count": int(top_repeat_channel_count)
        },
        "top_path_seller_combinations": top_path_seller.to_dict(orient='records'),
        "top_path_region_combinations": top_path_region.to_dict(orient='records'),
        "top_path_product_combinations": top_path_product.to_dict(orient='records')
    }

    with open(r"D:\fcicb6\repeat_combinations.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
        
    print(f"--- 재구매 최강 조합 분석 ---")
    print(f"재구매가 가장 많은 채널: {top_repeat_channel} ({top_repeat_channel_count}건)")
    print("\n[상위 5개 경로 x 셀러 조합]")
    for i, row in top_path_seller.head(5).iterrows():
        print(f"  {i+1}. {row['주문경로']} + {row['셀러명']} : {row['재구매건수']}건")

if __name__ == "__main__":
    analyze_repeat_combinations(r"D:\fcicb6\project1 - preprocessed_data.csv")
