import os
import csv
import requests
import re
import pandas as pd
from tqdm import tqdm
import random

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
]

def get_cusip(text):
    patterns = [
        r"CUSIP(?:N[oO].?|Number):?\s?(\d{3}[A-Z\d]{2}[\dA-Z*#@]{3}\d?)",
        r"\(E\).?CUSIPNUMBER:(\d{3}[A-Z\d]{2}[\dA-Z*#@]{3}\d?)"
    ]

    for pattern in patterns:
        match = re.compile(pattern, re.DOTALL | re.IGNORECASE).search(text)
        if match:
            cusip = match.group(1).strip()
            return cusip
    return

def filter_index(input_filename):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_filename)
    
    # Filter rows where form contains "13D" or "13G" and does not contain "13G/A" or "13D/A"
    df = df[df['form'].str.contains('13D|13G') & ~df['form'].str.contains('13G/A|13D/A')]
    
    # Convert date column to datetime and extract year
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    
    # Sort by cik, year, form, and date to prioritize keeping the earliest date if needed
    df = df.sort_values(by=['cik', 'year', 'form', 'date'])
    
    # Drop duplicates but keep one '13D' and one '13G' per cik per year
    df_unique = df.drop_duplicates(subset=['cik', 'year', 'form'])
    
    # Drop the 'year' column as it's no longer needed
    df_unique = df_unique.drop(columns=['year'])
    
    # Save the resulting DataFrame to a new CSV file
    output_filename = input_filename.replace('.csv', '_filtered.csv')
    df_unique.to_csv(output_filename, index=False)
    
    return output_filename

def fetch_documents_chunk(filename, num_chunks, output_dir, user_agents):
    base_url = "https://www.sec.gov/Archives/"
    
    with open(filename, mode='r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)
        rows = list(reader)
        chunk_size = (len(rows) // num_chunks) + 1
        
        for chunk_idx in range(num_chunks):
            chunk_start = chunk_idx * chunk_size
            chunk_end = min((chunk_idx + 1) * chunk_size, len(rows))
            chunk_rows = rows[chunk_start:chunk_end]
            
            results = []
            
            for row in tqdm(chunk_rows, desc=f"Processing chunk {chunk_idx+1}/{num_chunks}", dynamic_ncols=True, leave=True):
                cik, comnam, form, date, url_suffix = row
                full_url = base_url + url_suffix
                try:
                    headers = {'User-Agent': random.choice(user_agents)}
                    response = requests.get(full_url, headers=headers, timeout=10)
                    response.raise_for_status()
                    text = response.text
                    lines = text.split('\n')[:400]
                    partial_text = '\n'.join(lines)
                    clean_text = re.sub(r'<[^>]+>|\s+|-', '', partial_text, flags=re.DOTALL).split('\n')
                    cusip = None
                    for line in clean_text:  # Stop after processing first 200 lines
                        cusip = get_cusip(line)
                        if cusip:
                            break
                    results.append({'company_name': comnam, 'cik': cik, 'report_date': date, 'cusip': cusip})
                except requests.RequestException as e:
                    print(f"Failed to fetch data for {comnam}: {e}")
                    results.append({'company_name': comnam, 'cik': cik, 'report_date': date, 'cusip': None})
            
            chunk_df = pd.DataFrame(results)
            chunk_output_file = os.path.join(output_dir, f'chunk_{chunk_idx+1}.csv')
            chunk_df.to_csv(chunk_output_file, index=False)
            print(f"Chunk {chunk_idx+1} has been written to {chunk_output_file}")

def merge_csv_files(output_dir, final_output_file):
    all_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.csv')]
    combined_df = pd.concat((pd.read_csv(f) for f in all_files), ignore_index=True)
    combined_df.to_csv(final_output_file, index=False)
    print(f"All chunks have been merged into {final_output_file}")


filtered_csv = filter_index('full_index.csv')

output_dir = 'output_chunks'
os.makedirs(output_dir, exist_ok=True)
fetch_documents_chunk(filtered_csv, 100, output_dir, user_agents)
merge_csv_files(output_dir, 'output_data.csv')
