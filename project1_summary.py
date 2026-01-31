import pandas as pd
import json

def get_summary(file_path):
    df = pd.read_csv(file_path)
    
    # Preprocessing
    df['실결제 금액'] = df['실결제 금액'].str.replace(',', '').astype(float)
    df['주문일'] = pd.to_datetime(df['주문일'])
    
    summary = {}
    
    # 1. Top 5 Sellers by Revenue
    summary['top_sellers'] = df.groupby('셀러명')['실결제 금액'].sum().nlargest(5).to_dict()
    
    # 2. Strong Products for Top 3 Sellers
    top_3_sellers = list(summary['top_sellers'].keys())[:3]
    seller_products = {}
    for seller in top_3_sellers:
        seller_products[seller] = df[df['셀러명'] == seller]['품종'].value_counts().head(3).to_dict()
    summary['seller_top_products'] = seller_products
    
    # 3. Repeat Customers
    repeat_df = df[df['재구매 횟수'] > 0]
    summary['repeat_customer_count'] = int(df[df['재구매 횟수'] > 0]['UID'].nunique())
    summary['repeat_customer_top_regions'] = repeat_df['광역지역(정식)'].value_counts().head(3).to_dict()
    summary['repeat_customer_top_channels'] = repeat_df['주문경로'].value_counts().head(3).to_dict()
    
    # 4. Inflow Channels
    channel_revenue = df.groupby('주문경로')['실결제 금액'].sum().sort_values(ascending=False).to_dict()
    summary['channel_revenue'] = channel_revenue
    
    # 5. Additional: Regional Revenue
    summary['regional_revenue'] = df.groupby('광역지역(정식)')['실결제 금액'].sum().nlargest(5).to_dict()

    with open(r"D:\fcicb6\eda_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    get_summary(r"D:\fcicb6\project1 - preprocessed_data.csv")
