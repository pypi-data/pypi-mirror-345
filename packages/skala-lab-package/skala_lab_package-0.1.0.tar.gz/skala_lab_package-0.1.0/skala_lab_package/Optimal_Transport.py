import os
import numpy as np
import pandas as pd
import ot
import matplotlib.pyplot as plt
from sklearn.preprocessing import Normalizer
from sklearn.decomposition import PCA

class Optimal_Transport:
    def __init__(self, root, conditions):
        self.root = root
        self.conditions = conditions
        self.decay_features = None
        self.nadh_decay = None
        self.fad_decay = None
        self.decay_multi_channel_features = None
        self.pca = None
        self.normalizer = None
        self.results = {}
    
    def load_decay_data(self):
        cytoplasm_decay_matrices = {}
        for condition in self.conditions:
            files = os.listdir(os.path.join(self.root, condition))
            for f in files:
                path = os.path.join(self.root, condition, f)
                if path[-2] == "1" and "Dish1" in path and "Control" in path:
                    continue
                decay_file = [name for name in os.listdir(path) if '_decay_matrix.npy' in name and 'cytoplasm' not in name]
                if not decay_file:
                    continue
                decay_path = os.path.join(path, decay_file[0])
                cytoplasm_decay_matrices[decay_path] = np.load(decay_path)
        
        decay_features = []
        for k, v in cytoplasm_decay_matrices.items():
            df = pd.DataFrame(v)
            info = os.path.basename(k).split("_")
            df.insert(0, 'fullName', k)
            df.insert(1, 'treatment', os.path.basename(os.path.dirname(os.path.dirname(k))))  
            df.insert(2, 'dish', info[2])
            df.insert(3, 'site', info[3][0])
            df.insert(4, 'Channel', info[3][-1])
            df.insert(5, 'cell_id', np.arange(v.shape[0]))
            decay_features.append(df)
        
        self.decay_features = pd.concat(decay_features).reset_index()
        self.nadh_decay = self.decay_features[self.decay_features.Channel == "n"].copy()
        self.fad_decay = self.decay_features[self.decay_features.Channel == "f"].copy()
        
        # self.nadh_decay.iloc[:, 7:] = Normalizer(norm="l1").fit_transform(self.nadh_decay.iloc[:, 7:])
        # self.fad_decay.iloc[:, 7:] = Normalizer(norm="l1").fit_transform(self.fad_decay.iloc[:, 7:])
        
        # self.decay_multi_channel_features = pd.merge(self.nadh_decay, self.fad_decay, on=["treatment", "dish", "site", "cell_id"], how="inner")
        # self.decay_multi_channel_features.drop(["fullName_x", "fullName_y", "index_x","Channel_x","index_y","Channel_y"], axis=1, inplace=True)
        # self.decay_multi_channel_features.columns = ["treatment", "dish", "site", "cell_id"] + [str(x) for x in range(256*2)]
    
    def compute_global_pca(self, n_components=10):
        X_all = self.nadh_decay.iloc[:, 7:].values
        self.normalizer = Normalizer(norm='l1')
        X_all_norm = self.normalizer.fit_transform(X_all)
        self.pca = PCA(n_components=n_components)
        self.pca.fit(X_all_norm)
    
    def get_ot_distance(self, treat_control, treat_experiment):
        df_group1 = self.nadh_decay[self.nadh_decay['treatment'] == treat_control]
        df_group2 = self.nadh_decay[self.nadh_decay['treatment'] == treat_experiment]
        
        if df_group1.empty or df_group2.empty:
            print(f"Warning: No cells found for {treat_control} or {treat_experiment}. Skipping.")
            return None
        
        X_group1 = self.normalizer.transform(df_group1.iloc[:, 7:].values)
        X_group2 = self.normalizer.transform(df_group2.iloc[:, 7:].values)
        X_group1_pca = self.pca.transform(X_group1)
        X_group2_pca = self.pca.transform(X_group2)
        
        M = ot.dist(X_group1_pca, X_group2_pca, metric='euclidean')
        M /= M.max()
        
        M1 = ot.dist(X_group1_pca, X_group1_pca, metric='euclidean')
        M1 /= M1.max()
        
        M2 = ot.dist(X_group2_pca, X_group2_pca, metric='euclidean')
        M2 /= M2.max()
        
        G_matrix = ot.emd(np.ones(X_group1_pca.shape[0]) / X_group1_pca.shape[0],
                          np.ones(X_group2_pca.shape[0]) / X_group2_pca.shape[0], M, numItermax=1e7)
        dist = np.sum(G_matrix * M)
        
        self.results[(treat_control, treat_experiment)] = {
            "dist": dist,
            "M": M,
            "M1": M1,
            "M2": M2
        }
        
        return self.results[(treat_control, treat_experiment)]
    
    def plot_ot_distances(self, pairs):
        distances = []
        labels = []
        
        for (control_name, treat_name) in pairs:
            result = self.get_ot_distance(control_name, treat_name)
            if result is not None:
                distances.append(result["dist"])
                labels.append(f"{control_name}\nvs\n{treat_name}")
                print(f"OT distance: {control_name} vs {treat_name} = {result['dist']:.4f}")
        
        plt.figure(figsize=(10, 6))
        plt.bar(labels, distances, color='skyblue')
        plt.ylabel("OT Distance")
        plt.title("Pairwise OT Distances (Control vs Treatment) with L1 Normalization + PCA")
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        plt.show()
    
    def compare_distance_histograms(self, M1, M):
        vals_M1 = M1[np.triu_indices(M1.shape[0], k=1)]
        vals_M = M.flatten()
        
        plt.figure(figsize=(8, 6))
        plt.hist(vals_M1, bins=50, alpha=0.5, label="M1 (within-group)", density=True)
        plt.hist(vals_M, bins=50, alpha=0.5, label="M (between-group)", density=True)
        plt.xlabel("Pairwise Distance")
        plt.ylabel("Density")
        plt.title("Comparison of Distance Distributions")
        plt.legend()
        plt.show()
    
    def compare_distance_histograms_fair(self, M1, M):
        vals_M1 = M1[np.triu_indices(M1.shape[0], k=1)]
        vals_M = M.flatten()
        
        min_samples = min(len(vals_M1), len(vals_M))
        vals_M1_sampled = np.random.choice(vals_M1, size=min_samples, replace=False)
        vals_M_sampled = np.random.choice(vals_M, size=min_samples, replace=False)
        
        plt.figure(figsize=(8, 6))
        plt.hist(vals_M1_sampled, bins=50, alpha=0.5, label="M1 (within-group)", density=True)
        plt.hist(vals_M_sampled, bins=50, alpha=0.5, label="M (between-group)", density=True)
        plt.xlabel("Pairwise Distance")
        plt.ylabel("Density")
        plt.title("Comparison of Distance Distributions (Matched Samples)")
        plt.legend()
        plt.show()
