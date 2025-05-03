import skimage.io
import matplotlib.pyplot as plt
import numpy as np
import os
import re
from sdtfile.sdtfile import SdtFile
import torch
import pandas as pd
from skala_lab_package.sdt_reading import read_sdt150

gpu = 3
device = f"cuda:{gpu}" if torch.cuda.is_available() else 'cpu'
    

class SingleCellFeatureExtractor:
    def __init__(self, path, image_type='n'):
        self.path = path
        self.image_type = image_type.lower()
        if self.image_type == 'n':
            self.channel_2ch = 1
            self.channel_1ch = 0
            self.default_ymax = 25000
        else:
            self.channel_2ch = 0
            self.channel_1ch = 0
            self.default_ymax = 6000
        self.features_dict = {}

    def load_features(self):
        d = {}

        df = pd.read_csv(self.path)

        list_file_path = df["file_path"].tolist()
        list_channel_type = df["channel_type"].tolist()

        for i in range(len(list_file_path)):
            if (list_channel_type[i] != self.image_type):
                continue
            fp = os.path.join(list_file_path[i])
            sdt_files = [nm for nm in os.listdir(fp) if nm.endswith('.sdt')]
            if not sdt_files:
                continue

            sdt_full = os.path.join(fp, sdt_files[0])

            arr = read_sdt150(sdt_full)
            if arr.ndim == 3:
                arr = arr[None, ...]  # ensure shape is (1, X, Y, T)
            d[sdt_full] = arr

        self.features_dict = d

    @staticmethod
    def compute_matrix(raw, masks, channel):
        f = []
        u = np.unique(masks)
        for c in u[u > 0]:
            m = masks == c
            if not np.any(m):
                continue
            mc = raw[channel] * m[:, :, None]
            r, col = np.where(m)
            mnr, mxr = np.min(r), np.max(r)
            mnc, mxc = np.min(col), np.max(col)
            sc = mc[mnr:mxr+1, mnc:mxc+1]
            t = np.sum(sc, axis=(0, 1))
            f.append(t)
        return np.asarray(f)

    def plot_features(self, matrix, y_max=None):
        if y_max is None:
            y_max = self.default_ymax
        print("Matrix shape:", matrix.shape)
        for i in range(matrix.shape[0]):
            plt.plot(matrix[i])
        plt.ylim([0, y_max])
        plt.show()

    def process_features(self):
        for sdt_path, raw in self.features_dict.items():
            if raw.shape[0] == 2:
                ch = self.channel_2ch
            else:
                ch = self.channel_1ch

            if self.image_type == 'n':
                mask_path = sdt_path.replace(".sdt", "_photons_cyto3.tiff")
            elif self.image_type == 'f':
                mask_path = re.sub(r'(_\d)f', r'\1n', sdt_path)
                mask_path = mask_path.replace(".sdt", "_photons_cyto3.tiff")
            else:
                mask_path = sdt_path.replace(".sdt", "_photons_cyto3.tiff")

            if not os.path.exists(mask_path):
                print(f"Skipping {sdt_path}, mask not found: {mask_path}")
                continue

            m = skimage.io.imread(mask_path)
            mat = self.compute_matrix(raw, m, ch)
            self.plot_features(mat, None)
            out = sdt_path.replace(".sdt", "_feature_matrix.npy")
            np.save(out, mat)
            print(f"Saved feature matrix: {out}")

    def run(self):
        self.load_features()
        self.process_features()