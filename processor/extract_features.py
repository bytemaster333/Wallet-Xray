import sqlite3
import pandas as pd
import json
import os
from collections import Counter
from datetime import datetime

DB_PATH = "data/transactions.db"
OUTPUT_CSV = "data/features.csv"

def extract_features():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)

    features = []

    for wallet, group in df.groupby("wallet"):
        tx_count = len(group)

        # Unpack program_ids
        all_programs = []
        for row in group["program_ids"]:
            try:
                progs = json.loads(row)
                all_programs.extend(progs)
            except:
                continue

        unique_program_count = len(set(all_programs))
        most_common_program = Counter(all_programs).most_common(1)[0][0] if all_programs else "None"

        # Token transfer count
        token_transfer_count = 0
        for row in group["token_transfers"]:
            try:
                transfers = json.loads(row)
                token_transfer_count += len(transfers)
            except:
                continue

        # Active days
        block_times = group["block_time"].dropna().tolist()
        days = set()
        for t in block_times:
            if t:
                day = datetime.utcfromtimestamp(t).date()
                days.add(day)
        active_days = len(days)

        # Avg block time difference
        time_diffs = []
        sorted_times = sorted([t for t in block_times if t])
        if len(sorted_times) > 1:
            time_diffs = [t2 - t1 for t1, t2 in zip(sorted_times, sorted_times[1:])]
            avg_time_diff = sum(time_diffs) / len(time_diffs)
        else:
            avg_time_diff = 0

        features.append({
            "wallet": wallet,
            "tx_count": tx_count,
            "unique_program_count": unique_program_count,
            "most_used_program": most_common_program,
            "token_transfer_count": token_transfer_count,
            "active_days": active_days,
            "avg_block_time_diff": round(avg_time_diff, 2)
        })

    df_out = pd.DataFrame(features)
    os.makedirs("data", exist_ok=True)
    df_out.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Features extracted → {OUTPUT_CSV}")

if __name__ == "__main__":
    extract_features()
