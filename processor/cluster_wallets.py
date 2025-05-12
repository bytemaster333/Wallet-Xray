import pandas as pd
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

INPUT_CSV = "data/features.csv"
OUTPUT_CSV = "data/features_with_clusters.csv"

def cluster_wallets(n_clusters=5):
    df = pd.read_csv(INPUT_CSV)

    # Kullanılacak sayısal sütunlar
    numeric_cols = [
        "tx_count",
        "unique_program_count",
        "token_transfer_count",
        "active_days",
        "avg_block_time_diff"
    ]

    X = df[numeric_cols].fillna(0)

    # Normalize et
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # KMeans ile kümelendir
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df["cluster"] = kmeans.fit_predict(X_scaled)

    # Görselleştirme için t-SNE
    tsne = TSNE(n_components=2, random_state=42, perplexity=10)
    tsne_results = tsne.fit_transform(X_scaled)
    df["tsne_x"] = tsne_results[:, 0]
    df["tsne_y"] = tsne_results[:, 1]

    # Kaydet
    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Clustered features saved → {OUTPUT_CSV}")

    # Opsiyonel görselleştirme
    plt.figure(figsize=(8, 6))
    for cluster in sorted(df["cluster"].unique()):
        sub = df[df["cluster"] == cluster]
        plt.scatter(sub["tsne_x"], sub["tsne_y"], label=f"Cluster {cluster}", alpha=0.7)
    plt.title("Solana Wallet Behavior Clusters (t-SNE)")
    plt.legend()
    plt.savefig("data/cluster_plot.png")
    print("📊 Cluster plot saved → data/cluster_plot.png")

if __name__ == "__main__":
    cluster_wallets()
