# csvinspector/inspector.py

import pandas as pd
import os
from .visualizer import Visualizer
from .utils import detect_feature_types, get_missing_data_info, get_outlier_summary, get_correlation_matrix, get_skewed_features, get_normalization_summary
from .report_generator import ReportGenerator

class CSVInspector:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_csv(file_path)
        self.summary = {}
        self.feature_types = detect_feature_types(self.df)

    def run_analysis(self, output_dir="report"):
        self.summary = {
            "shape": self.df.shape,
            "dtypes": self.df.dtypes.to_dict(),
            "feature_types": self.feature_types,
            "missing_data": get_missing_data_info(self.df),
            "correlation_matrix": get_correlation_matrix(self.df),
            "outliers": get_outlier_summary(self.df)
        }

        self.summary["file_name"] = os.path.basename(self.file_path)
        self.summary["quantile_summary"] = self.df.describe().T  # <-- Ensure this line is present
        # Detect skewed features and suggest transformations
        self.summary["skewed_features"] = get_skewed_features(self.df)
        # Summarize normalization results
        self.summary["normalization_summary"] = get_normalization_summary(self.df)

        output_dir = "inspection_output"
        os.makedirs(output_dir, exist_ok=True)

        # # Generate report
        # ReportGenerator.generate_markdown_report(output_dir, self.summary)

        # Show report in terminal instead of writing file
        ReportGenerator.print_report_to_terminal(self.summary)

        # Create visualizations
        Visualizer.plot_distributions(self.df, output_dir)
        Visualizer.plot_correlation_heatmap(self.df, output_dir)
        Visualizer.plot_missing_data(self.df, output_dir)

        return self.summary

def main():
    import sys

    if len(sys.argv) < 2:
        print("❌ Usage: csvinspector <path_to_csv>")
        sys.exit(1)

    file_path = sys.argv[1]
    inspector = CSVInspector(file_path)
    inspector.run_analysis()
