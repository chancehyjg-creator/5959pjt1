import pandas as pd
import json

def get_path_insight(file_path):
    df = pd.read_csv(file_path)
    target_paths = ['기타', '크롬']
    filtered_df = df[df['주문경로'].isin(target_paths)].copy()
    
    # Analyze by Member Type
    member_dist = filtered_df.groupby(['주문경로', '회원구분']).size().unstack(fill_value=0).to_dict()
    
    # Analyze by Purpose (Inflow nature)
    purpose_dist = filtered_df.groupby(['주문경로', '목적']).size().unstack(fill_value=0).to_dict()
    
    # Analyze by Repeat Purchase (New vs Existing)
    filtered_df['is_new'] = filtered_df['재구매 횟수'] == 0
    new_dist = filtered_df.groupby(['주문경로', 'is_new']).size().unstack(fill_value=0).to_dict()
    
    result = {
        "member_distribution": member_dist,
        "purpose_distribution": purpose_dist,
        "new_customer_distribution": new_dist
    }
    
    with open(r"D:\fcicb6\path_detail.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_path_insight(r"D:\fcicb6\project1 - preprocessed_data.csv")
