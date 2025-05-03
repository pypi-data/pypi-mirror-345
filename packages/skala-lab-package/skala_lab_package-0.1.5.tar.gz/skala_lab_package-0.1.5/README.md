# 🔬 skala_lab_package

**skala_lab_package** is a Python package for redox feature extraction and structured CSV generation from scientific image or folder data. It includes tools to parse directory names, extract experimental metadata, analyze fluorescence decay, and process `.sdt` files from Bruker microscopy systems.

---

## 📦 Features

- 🔹 Extract metadata from folder names and export to CSV
- 🔹 Allows input for CSV file columns like `dish`, `channel_type`, and `condition`
- 🔹 Load `.sdt` files and convert to NumPy arrays
- 🔹 Utilities for redox decay and PCA-based analysis

---

## 🛠 Installation

Install from PyPI (if published):

```bash
python -m pip install skala-lab-package==0.1.5
