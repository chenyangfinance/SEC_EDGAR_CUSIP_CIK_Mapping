import requests
import pandas as pd
import random

# 一组更广泛的User-Agent字符串
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
]

def fetch_data(year, quarter, retries=2):
    url = f"https://www.sec.gov/Archives/edgar/full-index/{year}/QTR{quarter}/master.idx"
    for attempt in range(retries):
        try:
            user_agent = {"User-agent": random.choice(user_agents)}
            response = requests.get(url, headers=user_agent, timeout=10)
            response.raise_for_status()
            return response.content.decode('latin1').splitlines()
        except requests.RequestException as e:
            print(f"尝试第 {attempt + 1} 次失败，URL: {url}，错误: {e}")
    return []

if __name__ == "__main__":
    all_data = []
    for year in range(1993, 2006):
        print(f"正在处理年份 {year}")
        for q in range(1, 5):
            data = fetch_data(year, q)
            if data:
                filtered_data = [row.strip().split("|") for row in data if ".txt" in row]
                all_data.extend(filtered_data)
            else:
                print(f"未能获取到 {year} 年第 {q} 季度的数据")

    if all_data:
        df = pd.DataFrame(all_data, columns=["cik", "comnam", "form", "date", "url"])
        output_file = r"C:\Users\cheny\OneDrive\Database\Identifier 识别码\cik-cusip-mapping-master - 副本\full_index.csv"  # 请将路径替换为你的实际路径
        df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"数据已写入 {output_file}")
    else:
        print("没有收集到数据，无法写入 CSV 文件")
