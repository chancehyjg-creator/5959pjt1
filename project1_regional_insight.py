import pandas as pd
import os
import json

def get_regional_insights(file_path):
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return

    # 데이터 로드
    df = pd.read_csv(file_path)
    
    # 데이터 전처리: 실결제 금액 숫자형 변환
    if df['실결제 금액'].dtype == 'object':
        df['실결제 금액'] = df['실결제 금액'].str.replace(',', '').astype(float)
    else:
        df['실결제 금액'] = df['실결제 금액'].astype(float)

    # 1. 지역별 총 매출 상위 5개 지역 뽑기
    top_regions = df.groupby('광역지역(정식)')['실결제 금액'].sum().nlargest(5).index.tolist()
    
    regional_analysis = {}

    for region in top_regions:
        region_df = df[df['광역지역(정식)'] == region]
        
        # 해당 지역의 매출 총액
        total_sales = region_df['실결제 금액'].sum()
        
        # 해당 지역의 주요 주문 경로 Top 3
        top_channels = region_df.groupby('주문경로')['실결제 금액'].sum().nlargest(3).to_dict()
        
        # 해당 지역의 주요 셀러 Top 3
        top_sellers = region_df.groupby('셀러명')['실결제 금액'].sum().nlargest(3).to_dict()
        
        # 경로 x 셀러 조합 분석 (이 지역에서 어떤 경로로 어떤 셀러의 물건을 사는지)
        path_seller_top = region_df.groupby(['주문경로', '셀러명'])['실결제 금액'].sum().nlargest(3).reset_index()
        path_seller_list = []
        for _, row in path_seller_top.iterrows():
            path_seller_list.append({
                "경로": row['주문경로'],
                "셀러": row['셀러명'],
                "매출": row['실결제 금액']
            })

        regional_analysis[region] = {
            "총매출": total_sales,
            "주요경로": top_channels,
            "주요셀러": top_sellers,
            "상위조합": path_seller_list
        }

    # 결과 저장
    with open(r"D:\fcicb6\regional_insights.json", "w", encoding="utf-8") as f:
        json.dump(regional_analysis, f, ensure_ascii=False, indent=4)
        
    # 콘솔 출력용 요약
    print(f"--- 지역별 연계 분석 요약 ---")
    for region, data in regional_analysis.items():
        print(f"\n[{region}]")
        print(f"  - 총 매출: {data['총매출']:,.0f}원")
        print(f"  - 핵심 경로: {list(data['주요경로'].keys())[0]} ({data['주요경로'][list(data['주요경로'].keys())[0]]:,.0f}원)")
        print(f"  - 핵심 셀러: {list(data['주요셀러'].keys())[0]} ({data['주요셀러'][list(data['주요셀러'].keys())[0]]:,.0f}원)")
        print(f"  - 베스트 조합: {data['상위조합'][0]['경로']}를 통해 {data['상위조합'][0]['셀러']} 제품 구매")

if __name__ == "__main__":
    get_regional_insights(r"D:\fcicb6\project1 - preprocessed_data.csv")
