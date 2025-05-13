import requests
import time
import json
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances

from config import HELIUS_API_KEY

RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
SIGNATURE_LIMIT = 10

HEADERS = {"Content-Type": "application/json"}

def get_signatures(wallet):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            wallet,
            {"limit": SIGNATURE_LIMIT}
        ]
    }
    resp = requests.post(RPC_URL, headers=HEADERS, json=payload)
    if resp.status_code == 200:
        return [tx["signature"] for tx in resp.json().get("result", [])]
    return []

def get_transaction(sig):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            sig,
            {"encoding": "jsonParsed"}
        ]
    }
    resp = requests.post(RPC_URL, headers=HEADERS, json=payload)
    if resp.status_code == 200:
        return resp.json().get("result", {})
    return {}

def extract_features_for_wallet(wallet):
    sigs = get_signatures(wallet)
    if not sigs:
        return None  # No data

    txs = []
    for sig in sigs:
        tx = get_transaction(sig)
        if tx:
            txs.append(tx)
        time.sleep(0.1)

    if not txs:
        return None

    all_programs = []
    token_transfer_count = 0
    block_times = []

    for tx in txs:
        try:
            keys = tx["transaction"]["message"]["accountKeys"]
            programs = [k["pubkey"] if isinstance(k, dict) else k for k in keys]
            all_programs.extend(programs)
        except:
            continue

        try:
            transfers = tx["meta"]["postTokenBalances"]
            token_transfer_count += len(transfers)
        except:
            pass

        try:
            bt = tx.get("blockTime", 0)
            if bt:
                block_times.append(bt)
        except:
            pass

    tx_count = len(txs)
    unique_program_count = len(set(all_programs))
    active_days = len(set([pd.to_datetime(bt, unit="s").date() for bt in block_times]))
    time_diffs = [t2 - t1 for t1, t2 in zip(sorted(block_times), sorted(block_times)[1:])]
    avg_block_time_diff = sum(time_diffs) / len(time_diffs) if time_diffs else 0

    return {
        "wallet": wallet,
        "tx_count": tx_count,
        "unique_program_count": unique_program_count,
        "token_transfer_count": token_transfer_count,
        "active_days": active_days,
        "avg_block_time_diff": avg_block_time_diff
    }

def predict_cluster(new_features, reference_csv="data/features_with_clusters.csv"):
    df = pd.read_csv(reference_csv)
    feature_cols = [
        "tx_count",
        "unique_program_count",
        "token_transfer_count",
        "active_days",
        "avg_block_time_diff"
    ]

    ref_X = df[feature_cols].fillna(0)
    scaler = StandardScaler()
    ref_X_scaled = scaler.fit_transform(ref_X)

    new_X = pd.DataFrame([new_features])[feature_cols].fillna(0)
    new_X_scaled = scaler.transform(new_X)

    distances = euclidean_distances(new_X_scaled, ref_X_scaled)[0]
    nearest_index = distances.argmin()
    predicted_cluster = int(df.iloc[nearest_index]["cluster"])

    return predicted_cluster
