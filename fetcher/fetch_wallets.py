import requests
import csv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import HELIUS_API_KEY
import json
import time

# Jupiter Aggregator program ID
PROGRAM_ID = "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB"

# RPC endpoint with key
HELIUS_RPC_URL = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
OUTPUT_FILE = "data/wallets.csv"

def get_signatures(limit=250):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [
            PROGRAM_ID,
            {"limit": limit}
        ]
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(HELIUS_RPC_URL, json=payload, headers=headers)
    return resp.json().get("result", [])

def get_wallets_from_transactions(signatures):
    headers = {"Content-Type": "application/json"}
    wallets = set()

    for sig in signatures:
        tx_sig = sig["signature"]
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTransaction",
            "params": [
                tx_sig,
                {"encoding": "jsonParsed"}
            ]
        }

        resp = requests.post(HELIUS_RPC_URL, json=payload, headers=headers)
        if resp.status_code != 200:
            print(f"Hata: {resp.status_code} - {resp.text}")
            continue

        try:
            tx = resp.json().get("result", {})
            if not tx or "transaction" not in tx:
                continue  # boş veya eksik işlem

            keys = tx["transaction"]["message"]["accountKeys"]
            for key in keys:
                if isinstance(key, dict):
                    wallets.add(key["pubkey"])
                else:
                    wallets.add(key)

        except Exception as e:
            print("Parsing error:", e)
            continue

        time.sleep(0.1)  # rate limit'e takılmamak için

    return list(wallets)


EXCLUDE_PREFIXES = [
    "1111", "Tokenkeg", "ComputeBudget", "Memo", "Sysvar", "JUP4", "Stake111"
]

def save_wallets(wallets):
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["wallet_address"])
        count = 0
        for w in wallets:
            if any(w.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
                continue
            writer.writerow([w])
            count += 1
    print(f"{count} geçerli cüzdan kaydedildi → {OUTPUT_FILE}")

if __name__ == "__main__":
    print("İşlem imzaları alınıyor...")
    signatures = get_signatures()
    print(f"{len(signatures)} işlem bulundu.")

    print("Cüzdanlar çıkarılıyor...")
    wallets = get_wallets_from_transactions(signatures)

    print("Kayıt başlatılıyor...")
    save_wallets(wallets)

    print(f"{len(wallets)} benzersiz cüzdan bulundu.")