import requests
import sqlite3
import csv
import time
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import HELIUS_API_KEY

RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
DB_PATH = "data/transactions.db"
WALLET_CSV = "data/wallets.csv"
SIGNATURE_LIMIT = 10

headers = {"Content-Type": "application/json"}


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
    response = requests.post(RPC_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return [tx["signature"] for tx in response.json().get("result", [])]
    else:
        print(f"[!] Error getting signatures for {wallet}: {response.text}")
        return []


def get_transaction(signature):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [
            signature,
            {"encoding": "jsonParsed"}
        ]
    }
    response = requests.post(RPC_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json().get("result", {})
    else:
        print(f"[!] Error getting tx {signature}: {response.text}")
        return {}


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
              CREATE TABLE IF NOT EXISTS transactions
              (
                  id              INTEGER PRIMARY KEY AUTOINCREMENT,
                  wallet          TEXT,
                  signature       TEXT,
                  block_time      INTEGER,
                  program_ids     TEXT,
                  token_transfers TEXT
              )
              """)
    conn.commit()
    return conn


def extract_tx_info(wallet, signature, tx):
    block_time = tx.get("blockTime", 0)

    # Extract program IDs
    try:
        account_keys = tx["transaction"]["message"]["accountKeys"]
        program_ids = [k["pubkey"] if isinstance(k, dict) else k for k in account_keys]
    except:
        program_ids = []

    # Extract token transfers
    try:
        token_transfers = tx["meta"]["postTokenBalances"]
        transfers = [t["owner"] + ":" + t.get("mint", "") for t in token_transfers if "owner" in t]
    except:
        transfers = []

    return (wallet, signature, block_time, json.dumps(program_ids), json.dumps(transfers))


def fetch_all():
    conn = init_db()
    c = conn.cursor()

    with open(WALLET_CSV, newline='') as f:
        reader = csv.DictReader(f)
        wallets = [row["wallet_address"] for row in reader][:30]

    for wallet in wallets:
        print(f"⏳ Fetching transactions for {wallet}...")
        signatures = get_signatures(wallet)
        for sig in signatures:
            tx = get_transaction(sig)
            if not tx:
                continue
            tx_data = extract_tx_info(wallet, sig, tx)
            c.execute("""
                      INSERT INTO transactions (wallet, signature, block_time, program_ids, token_transfers)
                      VALUES (?, ?, ?, ?, ?)
                      """, tx_data)
            conn.commit()
            time.sleep(0.1)  # rate limit protection

    conn.close()
    print("✅ All transactions fetched and saved.")


if __name__ == "__main__":
    fetch_all()
