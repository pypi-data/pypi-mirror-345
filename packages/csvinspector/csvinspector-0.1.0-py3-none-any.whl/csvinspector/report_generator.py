import os
from datetime import datetime
from typing import Dict, Any


class ReportGenerator:
    @staticmethod
    def generate_markdown_report(output_dir: str, summary: Dict[str, Any]):
        report_path = os.path.join(output_dir, "report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# 📊 CSV Data Profiling Report\n\n")
            f.write(f"**File Analyzed**: `{summary['file_name']}`\n")
            f.write(f"**Generated On**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Basic Info
            f.write("## 📌 Basic Info\n")
            f.write(f"- Rows: {summary['shape'][0]}\n")
            f.write(f"- Columns: {summary['shape'][1]}\n\n")

            # Feature Types
            f.write("## 🧬 Feature Types\n")
            f.write("```\n")
            for col, dtype in summary["feature_types"].items():
                f.write(f"{col}: {dtype}\n")
            f.write("```\n\n")

            # Quantiles
            f.write("## 📈 Quantile Summary (first 5 columns)\n")
            f.write(summary["quantile_summary"].iloc[:, :5].to_markdown() + "\n\n")

            # Missing Data
            f.write("## 🚫 Missing Data\n")
            f.write(summary["missing_data"].to_markdown() + "\n\n")

            # Correlation Matrix
            f.write("## 🔗 Correlation Matrix (first 5 rows)\n")
            f.write(summary["correlation_matrix"].head().to_markdown() + "\n\n")

            # Outlier Summary
            f.write("## 🧪 Outlier Summary\n")
            f.write(summary["outliers"].to_markdown() + "\n\n")

            # Optional: Before/After Outlier Cleanup
            if "outlier_cleanup_stats" in summary:
                f.write("## 🧹 Outlier Removal Summary\n")
                for col, stats in summary["outlier_cleanup_stats"].items():
                    f.write(f"- **{col}**: {stats['outlier_count']} outliers removed, "
                            f"{stats['retained_count']} rows retained from {stats['original_count']}\n")
                f.write("\n")

            # Distributions
            f.write("## 📊 Sample Distributions (Before)\n")
            f.write("![Distributions](distribution_before_outlier_removal.png)\n\n")
            if os.path.exists(os.path.join(output_dir, "distribution_after_outlier_removal.png")):
                f.write("## ✅ Distributions After Outlier Removal\n")
                f.write("![Distributions](distribution_after_outlier_removal.png)\n\n")

            # Heatmaps
            f.write("## 📉 Correlation Heatmap\n")
            f.write("![Correlation Heatmap](correlation_heatmap.png)\n\n")

            f.write("## 🕳️ Missing Data Heatmap\n")
            f.write("![Missing Data Heatmap](missing_data_heatmap.png)\n\n")

            # Skewness Section
            f.write("## 🔄 Skewness and Suggested Transformations\n")
            if summary["skewed_features"]:
                f.write(
                    "| Feature | Skewness | Suggested Transformation |\n|:--------|----------:|:-------------------------|\n")
                for feature, info in summary["skewed_features"].items():
                    f.write(f"| {feature} | {info['skew']:.2f} | {info['suggested_transform']} |\n")
            else:
                f.write("No significantly skewed features found.\n")

            # Normalization Summary
            f.write("\n## 🪄 Normalization Summary\n")
            for method, desc_df in summary["normalization_summary"].items():
                f.write(f"### {method}\n")
                f.write(desc_df.to_markdown())
                f.write("\n")

            # Advanced Feature Suggestions
            f.write("## 🧠 Advanced Feature Suggestions\n")
            f.write("| Feature | Description |\n")
            f.write("|---------|-------------|\n")
            f.write("| 🔄 Skewness Fix | Identify and suggest log/sqrt transformations for skewed data |\n")
            f.write("| 🧮 Feature Engineering | Generate interaction terms, polynomial features (optional) |\n")
            f.write("| 🪄 Auto Normalization | StandardScaler or MinMaxScaler summaries |\n")
            f.write("| 📊 PCA Visualization | Optional: PCA plot for numeric data |\n")
            f.write("| 💡 Insights | Flag features with very high correlation or constant values |\n")
            f.write("| ✅ Data Quality Score | Rate datasets (e.g., based on missing % and outlier % ) |\n\n")

            # Optional: Quality Score
            if "quality_score" in summary:
                f.write("### 📋 Data Quality Score\n")
                f.write(f"- **Score**: {summary['quality_score']} / 10\n")
                f.write(f"- **Comment**: {summary.get('quality_comment', 'Not available')}\n\n")

        print(f"✅ Report generated: {report_path}")
