import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from processor.on_demand_analyze import extract_features_for_wallet, predict_cluster

DATA_PATH = "data/features_with_clusters.csv"

CLUSTER_LABELS = {
    0: "Heavy Swapper",
    1: "Whale Wallet",
    2: "System-like Wallet",
    3: "Spike Behavior",
    4: "Casual User"
}

st.set_page_config(page_title="Solana Wallet X-Ray", layout="centered")
st.title("🧐 Solana Wallet X-Ray")
st.markdown("Understand your wallet's behavior and see how it compares with others in the Solana ecosystem.")

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

df = load_data()

# --- Module 1: Select wallet from list
st.subheader("📂 Select From Analyzed Wallets")

wallet_list = df["wallet"].tolist()
selected_wallet = st.selectbox("Choose a wallet address", wallet_list)

if selected_wallet:
    wallet_info = df[df["wallet"] == selected_wallet].iloc[0]
    cluster_id = int(wallet_info["cluster"])
    cluster_label = CLUSTER_LABELS.get(cluster_id, "Unknown")

    st.markdown(f"### 🧬 Behavior Summary: `{selected_wallet}`")
    col1, col2, col3 = st.columns(3)
    col1.metric("Transactions", wallet_info["tx_count"])
    col2.metric("Unique Programs", wallet_info["unique_program_count"])
    col3.metric("Token Transfers", wallet_info["token_transfer_count"])

    col4, col5 = st.columns(2)
    col4.metric("Active Days", wallet_info["active_days"])
    col5.metric("Avg. Time Gap (s)", round(wallet_info["avg_block_time_diff"], 2))

    st.info(f"🔎 **Cluster Prediction:** {cluster_label}")
    st.caption(f"Most frequently used program: `{wallet_info['most_used_program']}`")

    st.markdown("### 📈 Cluster Visualization")


    def plotly_cluster_map(df, selected_wallet=None):
        import plotly.express as px

        df_vis = df.copy()
        df_vis["cluster_label"] = df_vis["cluster"].apply(lambda x: CLUSTER_LABELS.get(x, f"Cluster {x}"))
        df_vis["is_selected"] = df_vis["wallet"] == selected_wallet

        # Cluster renkleri: parlak + dark uyumlu
        color_map = {
            "Heavy Swapper": "#29B6F6",  # Light Blue
            "Whale Wallet": "#FF7043",  # Orange
            "System-like Wallet": "#AB47BC",  # Purple
            "Spike Behavior": "#66BB6A",  # Green
            "Casual User": "#FFCA28"  # Yellow
        }
        df_vis["color"] = df_vis["cluster_label"].map(color_map)

        fig = px.scatter(
            df_vis,
            x="tsne_x",
            y="tsne_y",
            color="cluster_label",
            color_discrete_map=color_map,
            symbol="is_selected",
            symbol_map={True: "star", False: "circle"},
            hover_data={
                "wallet": True,
                "tx_count": True,
                "unique_program_count": True,
                "token_transfer_count": True,
                "cluster_label": True,
                "tsne_x": False,
                "tsne_y": False,
                "is_selected": False
            },
        )

        fig.update_traces(marker=dict(size=10, opacity=0.85, line=dict(width=1, color="white")))

        fig.update_layout(
            template="plotly_dark",
            height=720,
            margin=dict(l=30, r=30, t=50, b=30),
            font=dict(family="Segoe UI", size=13),
            legend_title_text="Wallet Behavior",
            legend=dict(
                bgcolor="rgba(0,0,0,0)",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )

        st.plotly_chart(fig, use_container_width=True)

    plotly_cluster_map(df, selected_wallet)

# --- Module 2: Enter your own wallet address
st.markdown("---")
st.subheader("🧪 Analyze a New Wallet")

new_wallet = st.text_input("Paste any Solana wallet address below to analyze its behavior", placeholder="Enter wallet address...")

if new_wallet:
    if new_wallet in df["wallet"].values:
        st.success("✅ This wallet is already in the dataset. See above for details.")
    else:
        with st.spinner("🔍 Fetching and analyzing wallet data..."):
            features = extract_features_for_wallet(new_wallet)

        if features:
            predicted_cluster = predict_cluster(features)
            label = CLUSTER_LABELS.get(predicted_cluster, f"Cluster {predicted_cluster}")

            st.success(f"✅ This wallet most likely belongs to: **{label}**")

            st.markdown("### 🔬 Feature Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Transactions", features["tx_count"])
            col2.metric("Unique Programs", features["unique_program_count"])
            col3.metric("Token Transfers", features["token_transfer_count"])

            col4, col5 = st.columns(2)
            col4.metric("Active Days", features["active_days"])
            col5.metric("Avg. Time Gap (s)", round(features["avg_block_time_diff"], 2))

        else:
            st.error("❌ Could not fetch data for this wallet. It may be inactive or rate-limited.")

st.markdown("---")
st.caption("Built with ❤️ using Solana, Helius API, and Streamlit.")
