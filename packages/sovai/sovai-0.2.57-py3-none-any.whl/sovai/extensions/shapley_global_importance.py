import pandas as pd
import numpy as np
import random
from lightgbm import LGBMClassifier
from sklearn.cluster import KMeans, MeanShift, HDBSCAN
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.preprocessing import StandardScaler
import shap
from joblib import Parallel, delayed
import hashlib
from scipy import stats
import os
import warnings


def hash_of_df(df, sample_size=100):
    df_sample = (
        df.sample(n=min(sample_size, len(df)), random_state=42).to_string().encode()
    )
    return hashlib.sha256(df_sample).hexdigest()

class ClusteringExplainer:
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.model = None
        self.explainer = None
        self.scaler = StandardScaler()

    def fit(self, X, y):
        classes_weights = compute_sample_weight(class_weight="balanced", y=y)
        self.model = LGBMClassifier(
            objective="multiclass",
            random_state=self.random_state,
            verbose=-1,
            force_col_wise=True,
            min_gain_to_split=0.01
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.model.fit(X, y, sample_weight=classes_weights)
        self.explainer = shap.Explainer(self.model)

    def get_shap_values(self, X):
        return self.explainer(X)

def get_shap_values_for_dataset(df, clustering_method="KMEANS", n_clusters=10, random_state=42, sample_size=5000):
    # Sample for clustering and model training
    X_sample = df.sample(n=min(sample_size, len(df)), random_state=random_state)
    
    scaler = StandardScaler()
    X_sample_scaled = scaler.fit_transform(X_sample)

    if clustering_method == "KMEANS":
        num_clusters = random.randint(5, 10)
        clustering = KMeans(n_clusters=num_clusters, random_state=random_state)
    elif clustering_method == "MEANSHIFT":
        clustering = MeanShift()
    elif clustering_method == "HDBSCAN":
        clustering = HDBSCAN(min_cluster_size=5)
    else:
        raise ValueError(f"Unsupported clustering method: {clustering_method}")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        clustering.fit(X_sample_scaled)

    y_sample = clustering.labels_

    if clustering_method == "HDBSCAN":
        noise_label = max(y_sample) + 1
        y_sample[y_sample == -1] = noise_label

    clust_explnr = ClusteringExplainer(random_state=random_state)
    clust_explnr.fit(X_sample_scaled, y_sample)

    # Transform the entire dataset
    X_full_scaled = scaler.transform(df)

    # Get SHAP values for the entire dataset
    shap_values = clust_explnr.get_shap_values(X_full_scaled)
    mean_abs_shap = np.mean(np.abs(shap_values.values), axis=2)
    mean_abs_shap_df = pd.DataFrame(mean_abs_shap, columns=df.columns, index=df.index)

    return mean_abs_shap_df

def run_simulations_frame_global(df, num_simulations=4, clustering_method="KMEANS"):
    data_hash = hash_of_df(df)
    tasks = []
    for i in range(num_simulations):
        random.seed(int(data_hash, 16) + i)
        kmeans_random_state = random.randint(0, 1000)
        lgbm_random_state = random.randint(0, 1000)
        tasks.append(
            delayed(get_shap_values_for_dataset)(
                df, clustering_method, 10, kmeans_random_state
            )
        )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        all_shap_values = Parallel(n_jobs=-1, verbose=0)(tasks)
    # print(all_shap_values)
    # print(all_shap_values.shape)

    # print(all_shap_values[0].index)
    # print(all_shap_values[2].index)
    avg_shap_values = pd.concat(all_shap_values).abs().reset_index().groupby(by=["ticker","date"]).mean()
    # avg_shap_values.index = df.index
    return avg_shap_values

def run_simulations_global_importance(df, num_simulations=4, clustering_method="KMEANS"):
    avg_shap_values = run_simulations_frame_global(df, num_simulations=num_simulations, clustering_method=clustering_method)
    feature_importance = pd.DataFrame(
        {
            "feature": avg_shap_values.columns,
            "importance": avg_shap_values.mean().values,
        }
    )
    feature_importance["importance_percentile"] = stats.percentileofscore(
        feature_importance["importance"], feature_importance["importance"]
    )
    return feature_importance.sort_values(
        "importance_percentile", ascending=False
    ).reset_index(drop=True)


# Usage example:
# importance_df = run_simulations(df, num_simulations=4, clustering_method='KMEANS')