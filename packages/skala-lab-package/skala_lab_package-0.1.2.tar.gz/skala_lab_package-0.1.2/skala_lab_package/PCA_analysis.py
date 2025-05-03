import os
import scipy
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import Normalizer
from sklearn.decomposition import PCA

SITE = 'site'
DISH = 'dish'
TOTAL = 'total'

class SingleCellPCAAnalysis:
    def __init__(self, root: str, conditions: list):
        self.root = root
        self.conditions = conditions
        self.decay_matrices = {}         
        self.decay_features = pd.DataFrame()
        self.nadh_decay = pd.DataFrame()
        self.fad_decay = pd.DataFrame()
        self.decay_multi_channel = pd.DataFrame()
        self.pca_model = None            
        self.explained_variance = None  

    def load_decay_data(self):
        for condition in self.conditions:
            condition_path = os.path.join(self.root, condition)
            if not os.path.exists(condition_path):
                continue
            for f in os.listdir(condition_path):
                path = os.path.join(condition_path, f)
                if not os.path.isdir(path):
                    continue
                decay_files = [name for name in os.listdir(path) if '_decay_matrix.npy' in name]
                for df in decay_files:
                    full_decay_path = os.path.join(path, df)
                    matrix = np.load(full_decay_path)
                    self.decay_matrices[full_decay_path] = matrix

    def build_features_dataframe(self):
        decay_features_list = []
        for path, matrix_data in self.decay_matrices.items():
            info = path.split(os.sep)[-1].split("_")
            df = pd.DataFrame(matrix_data)
            df.insert(loc=0, column='fullName', value=path)
            df.insert(loc=1, column='treatment', value=info[1])
            df.insert(loc=2, column='dish', value=info[2])
            df.insert(loc=3, column='site', value=info[3][0])
            df.insert(loc=4, column='Channel', value=info[3][-1])
            df.insert(loc=5, column='cell_id', value=np.arange(matrix_data.shape[0]))
            decay_features_list.append(df)

        self.decay_features = pd.concat(decay_features_list).reset_index(drop=True)

    def separate_nadh_fad(self):
        self.nadh_decay = self.decay_features[self.decay_features.Channel == 'n'].copy()
        self.fad_decay = self.decay_features[self.decay_features.Channel == 'f'].copy()

    def normalize_data(self):
        # NADH
        nadh_cols = [col for col in self.nadh_decay.columns if isinstance(col, int)]
        if nadh_cols:
            F_nadh = self.nadh_decay.loc[:, nadh_cols]
            normalized_n = Normalizer(norm='l1').fit_transform(F_nadh)
            self.nadh_decay.loc[:, nadh_cols] = normalized_n

        # FAD
        fad_cols = [col for col in self.fad_decay.columns if isinstance(col, int)]
        if fad_cols:
            F_fad = self.fad_decay.loc[:, fad_cols]
            normalized_f = Normalizer(norm='l1').fit_transform(F_fad)
            self.fad_decay.loc[:, fad_cols] = normalized_f

    def merge_nadh_fad(self):
        merged = pd.merge(
            self.nadh_decay,
            self.fad_decay,
            on=["treatment", "dish", "site", "cell_id"],
            how="inner"
        )

        to_drop = ["fullName_x", "fullName_y", "index_x", "Channel_x", "index_y", "Channel_y"]
        for c in to_drop:
            if c in merged.columns:
                merged.drop(columns=c, inplace=True)

        col_names = ["treatment", "dish", "site", "cell_id"] + [x for x in range(256 * 2)]
        if len(merged.columns) == len(col_names):
            merged.columns = col_names

        self.decay_multi_channel = merged

    def pca_plot_any(self, df, comp_x=0, comp_y=1, title="Scatter Plot"):
        if df.empty:
            print("DataFrame is empty, cannot perform PCA.")
            return None, None, None, None

        if 'treatment' not in df.columns:
            print("DataFrame has no 'treatment' column, cannot color by treatment.")
            return None, None, None, None

        numeric_cols = [col for col in df.columns if isinstance(col, int)]
        if not numeric_cols:
            print("No numeric columns to perform PCA on.")
            return None, None, None, None

        features_data = df[numeric_cols]

        pca_model = PCA()
        X = pca_model.fit_transform(features_data)
        explained_variance = pca_model.explained_variance_ratio_

        plot_df = pd.concat([
            df[['treatment']].reset_index(drop=True),
            pd.DataFrame(X)
        ], axis=1)
        plot_df = plot_df.rename(columns={
            comp_x: f'PC{comp_x}',
            comp_y: f'PC{comp_y}'
        })

        sns.scatterplot(
            data=plot_df,
            x=f'PC{comp_x}',
            y=f'PC{comp_y}',
            hue='treatment',
            palette=sns.color_palette('Set2'),
            s=12,
            alpha=0.75
        )
        plt.title(title)
        plt.legend(title='Treatment')
        plt.show()

        print(f"Explained Variance Ratio (PC{comp_x+1}, PC{comp_y+1}):")
        for i in range(min(len(explained_variance), 10)):
            print(f"PC{i+1}: {explained_variance[i]:.4f}")

        return plot_df, pca_model, features_data, explained_variance

    def pca_plot(self, comp_x=0, comp_y=1, title="Scatter Plot"):
        if self.decay_multi_channel.empty:
            print("No data in self.decay_multi_channel. Please run merge_nadh_fad() first.")
            return None, None, None, None

        plot_df, pca_model, features_data, explained_variance = self.pca_plot_any(
            self.decay_multi_channel, comp_x, comp_y, title
        )
        self.pca_model = pca_model
        self.explained_variance = explained_variance

        return plot_df, pca_model, features_data, explained_variance

    def anova_analysis(self, data: pd.DataFrame) -> pd.DataFrame:
        if 'treatment' not in data.columns:
            raise ValueError("Data does not contain 'treatment' column.")

        treatments = data['treatment'].unique()
        anova_results = []
        drop_cols = ["treatment"]
        use_cols = [c for c in data.columns if c not in drop_cols]

        for col in use_cols:
            groups = [data[data['treatment'] == treatment][col] for treatment in treatments]
            f_statistic, p_value = scipy.stats.f_oneway(*groups)
            anova_results.append({"statistic": f_statistic, "pvalue": p_value})

        anova_df = pd.DataFrame(anova_results, index=use_cols)
        anova_df.sort_values("statistic", ascending=False, inplace=True)
        return anova_df

    def run_pipeline(self):
        self.load_decay_data()
        self.build_features_dataframe()
        self.separate_nadh_fad()
        self.normalize_data()
        self.merge_nadh_fad()
        self.pca_plot()

