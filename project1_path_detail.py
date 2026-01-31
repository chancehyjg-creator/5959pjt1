import pandas as pd
import os

def analyze_specific_paths(file_path):
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return

    # 데이터 로드
    df = pd.read_csv(file_path)
    
    # '기타'와 '크롬' 경로 데이터만 필터링
    target_paths = ['기타', '크롬']
    filtered_df = df[df['주문경로'].isin(target_paths)]
    
    print(f"--- '기타' 및 '크롬' 경로 상세 분석 (총 {len(filtered_df)}건) ---")
    
    # 1. 경로별 회원구분(회원 vs 비회원) 분포
    path_member_dist = filtered_df.groupby(['주문경로', '회원구분']).size().unstack(fill_value=0)
    print("\n[1. 회원구분 분포]")
    print(path_member_dist)
    
    # 2. 비율로 확인
    path_member_ratio = path_member_dist.div(path_member_dist.sum(axis=1), axis=0) * 100
    print("\n[2. 회원구분 비율 (%)]")
    print(path_member_ratio.round(2))

    # 3. '목적' 컬럼 분석 (검색 유입 성격 파악)
    if '목적' in df.columns:
        print("\n[3. 구매 목적별 분포]")
        path_purpose_dist = filtered_df.groupby(['주문경로', '목적']).size().unstack(fill_value=0)
        print(path_purpose_dist)

    # 4. 재구매 횟수가 0인 경우 (신규 유입/검색 유입 가능성)
    print("\n[4. 신규 유입(재구매 횟수 0) vs 기존 고객]")
    filtered_df['고객유형'] = filtered_df['재구매 횟수'].apply(lambda x: '신규(검색유입 가능성)' if x == 0 else '기존(재방문)')
    new_inflow_dist = filtered_df.groupby(['주문경로', '고객유형']).size().unstack(fill_value=0)
    print(new_inflow_dist)

if __name__ == "__main__":
    analyze_specific_paths(r"D:\fcicb6\project1 - preprocessed_data.csv")
