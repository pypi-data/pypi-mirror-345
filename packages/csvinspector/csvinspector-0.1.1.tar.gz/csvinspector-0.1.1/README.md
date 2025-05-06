# CSVInspector 🕵️‍♂️

CSVInspector is a powerful Python library for automating preprocessing and exploratory data analysis (EDA) on CSV datasets. It’s built to help data scientists and analysts quickly understand the structure and quality of their data — all in one go.

---

## ✨ Features

- 📌 Basic info summary (rows, columns, data types)
- 🧬 Automatic feature type detection
- 🚫 Missing data detection and heatmaps
- 📉 Correlation matrix + heatmap
- 📊 Distribution plots (before/after outlier removal)
- 🧪 Outlier detection summary
- 🔄 Skewness detection with transformation suggestions
- 🪄 Normalization summaries (MinMaxScaler, StandardScaler)
- 📈 Quantile summaries for quick statistics
- 📋 Optional quality score
- 📄 Comprehensive Markdown report generation

---

## 📦 Installation

```bash
pip install csvinspector
```

---

## 🚀 Usage

Here’s a minimal example using `CSVInspector`:

```python
from csvinspector import CSVInspector

inspector = CSVInspector("your_dataset.csv")
summary = inspector.run_analysis()
```

This will generate:
- A detailed Markdown report in `inspection_output/report.md`
- Plots and visualizations in the same folder
- A dictionary object `summary` with all analysis results

---

## 🖼️ Sample Output (Markdown)

```markdown
# 📊 CSV Data Profiling Report

**File Analyzed**: `your_dataset.csv`  
**Generated On**: 2025-05-05 15:32:21

## 📌 Basic Info
- Rows: 1000  
- Columns: 12  

## 🧬 Feature Types
```
age: numerical  
gender: categorical  
income: numerical  
```

## 📈 Quantile Summary (first 5 columns)
|       | count | mean  | std   | min  | 25%   |
|-------|-------|-------|-------|------|-------|
| age   | 1000  | 35.4  | 9.2   | 18   | 29    |
| income| 1000  | 55000 | 15000 | 2000 | 45000 |

...

## 🔗 Correlation Matrix (first 5 rows)
|       | age   | income | score | ... |
|-------|-------|--------|-------|-----|
| age   | 1.00  | 0.43   | 0.21  |     |
| income| 0.43  | 1.00   | 0.50  |     |

...

## 🕳️ Missing Data Heatmap
![Missing Data Heatmap](inspection_output/missing_data_heatmap.png)
```

---

## 🛠 Development

```bash
git clone https://github.com/abhii14758/csvinspector
cd csvinspector
pip install -e .[dev]
```

To run analysis:

```bash
python -m csvinspector path/to/your.csv
```

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 👤 Author

**Abhi**  
[GitHub Profile](https://github.com/abhii14758)

---

## 🙏 Acknowledgments

- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)
- [Seaborn](https://seaborn.pydata.org/)
- [Scikit-learn](https://scikit-learn.org/)