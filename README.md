# 🔍 Wallet X-Ray

**Wallet X-Ray** is a machine learning-powered behavioral analytics tool for Solana wallets. It clusters wallets into distinct behavioral categories (e.g., Whales, Bots, Casual Users) using transaction patterns, program interactions, and token activity metrics.

The tool provides both a high-level map of wallet behavior across the network and a per-address interpretability module, all visualized through an interactive, Streamlit-based UI.

---

## 🧠 Motivation & Problem

Solana’s public ledger holds rich data, but interpreting wallet behavior at scale is challenging. Users, developers, and protocol teams lack intuitive tools to:

- Understand what kind of wallet they interact with
- Detect anomalous or bot-like behavior
- Visually explore the ecosystem’s behavioral landscape

**Wallet X-Ray bridges this gap** by turning raw transaction data into clustered behavioral profiles using unsupervised learning and visual analytics.

---

## 🔁 Data Pipeline Overview

Wallet X-Ray consists of a custom data pipeline built on top of the [Helius API](https://docs.helius.xyz/):

[ Signatures ]
↓
[ Raw Transactions ]
↓
[ Feature Extraction ]
↓
[ SQLite DB ]
↓
[ Clustering + Projection ]
↓
[ Dashboard (Streamlit) ]

---

## 📐 Feature Engineering

For each wallet, the following behavioral features are extracted:

| Feature Name           | Description |
|------------------------|-------------|
| `tx_count`             | Number of transactions |
| `unique_program_count` | Number of unique program IDs interacted with |
| `token_transfer_count` | Number of SPL token transfers (parsed from postTokenBalances) |
| `active_days`          | Number of distinct block days active |
| `avg_block_time_diff`  | Average block time gap between transactions |
| `most_used_program`    | Most frequently invoked program ID (used for interpretability, not clustering) |

All features are normalized using `StandardScaler` before ML processing.

---

## 🧪 ML & Clustering Process

- **KMeans** is used to group wallets into 5 behavior-based clusters.
- **t-SNE** is applied for 2D projection to visualize wallet distribution.
- Clusters are heuristically labeled based on dominant features:

| Cluster ID | Label             | Example Behavior |
|------------|------------------|------------------|
| 0          | Heavy Swapper     | Many tx, few programs, high token flow |
| 1          | Whale Wallet      | Large interaction volume, diverse usage |
| 2          | System-like Wallet| Interacts only with core programs |
| 3          | Spike Behavior    | Sudden bursts of activity, long gaps |
| 4          | Casual User       | Few tx, low token movement |

> Note: Clustering is unsupervised — no labels are used during training.

---

## 💻 Dashboard Modules

The Streamlit UI has two main components:

### 1. 🔎 Cluster Browser
- Select from pre-analyzed wallets
- View detailed behavioral summary
- See interactive cluster map with t-SNE projection
- Understand which cluster the wallet belongs to

### 2. 🧪 Analyze a New Wallet
- Paste any valid Solana address
- Tool will fetch transactions on-demand
- Output its cluster label and feature summary

Each wallet’s position is marked as a white star on the map when selected.

---

## 📦 Installation
```bash
git clone https://github.com/your-username/wallet-xray.git
cd wallet-xray
```
Create a .env file with your Helius API key:
```bash
HELIUS_API_KEY=your-key-here
```
Install dependencies:
```bash
pip install -r requirements.txt
```
Launch the app:
```bash
streamlit run app.py
```
## ⚠️ Limitations
The current model uses ~200 wallets due to API limits — behavior diversity can be improved.

Clustering labels are heuristic and not verified with external datasets.

NFT, staking, and dApp-specific behaviors are not yet part of the feature set.

Real-time analysis may fail for inactive wallets or under rate-limiting.

## 🧭 Roadmap & Scalability Plan
Wallet X-Ray is designed as a modular and extensible behavioral analysis engine. While the current MVP delivers a functional end-to-end system with clustering and UI, the system was intentionally built on a minimal dataset due to external constraints. Below is a breakdown of what exists and what’s next.

### ✅ MVP Achievements (Current Version)
🔹 Behavioral features extracted from 200+ live wallet addresses

🔹 Feature engineering based on raw transaction metadata from Helius RPC

🔹 KMeans clustering with unsupervised grouping of wallets

🔹 t-SNE dimensionality reduction for intuitive 2D visualization

🔹 Interactive Streamlit dashboard with cluster map and metrics

🔹 “Analyze your wallet” module (on-demand feature inference)

Note: Due to the rate limits of the public Helius API, the current dataset is limited to ~200 wallets with a maximum of 10 transactions each. This ensures fast experimentation and testing without exceeding API quotas during development.

### 🔜 Near-Term Improvements (Post-MVP)
⚙️ Add caching and retry logic to avoid failed live fetches

⚙️ Allow adjustable tx depth (e.g., 50–100 tx per wallet)

⚙️ Extend dataset to 1000+ wallets once dedicated API quota is available

🔍 Introduce wallet “behavior heatmaps” over time and token use

📊 Add cluster-level analytics (token diversity, contract patterns, etc.)

### 🧠 ML & Explainability Additions
🧩 Integrate labeled identities (e.g. whales, bots, team wallets) for semi-supervised training

🤖 Add a lightweight rule engine or LLM-based explainer to clarify why a wallet is clustered a certain way

📉 Integrate anomaly detection: spike detection, inactivity, pattern deviation

🔐 Incorporate external behavioral tagging (e.g., suspicious tokens, rug signals)

### 📤 Output & Integration Features
📄 PDF/CSV export of individual wallet analysis reports

🔗 Embed charts or insights into external dashboards (e.g., Dune, Grafana)

📬 Add Telegram, Discord, or Webhook alerts for wallets that exhibit risky or unusual behavior

🧪 Optional: browser-based wallet connect to instantly analyze a connected address

### 🚀 Long-Term Vision
Make Solana wallets not just visible, but understandable.

A developer tool for forensic analysis

A security layer for DeFi protocols, DAO treasuries, and staking services

A real-time behavior engine with customizable risk profiles

A component for on-chain credit scoring and identity management


