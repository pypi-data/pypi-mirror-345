# csvinspector/visualizer.py

import os
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno

class Visualizer:
    @staticmethod
    def ensure_output_dir(output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    @staticmethod
    def plot_distributions(df, output_dir, filename="distribution_plots.png", title="Feature Distributions"):
        Visualizer.ensure_output_dir(output_dir)
        num_cols = df.select_dtypes(include='number').columns

        for col in num_cols:
            plt.figure(figsize=(8, 4))
            sns.histplot(df[col].dropna(), kde=True, bins=30)
            plt.title(f'Distribution of {col}')
            plt.suptitle(title)
            plt.savefig(os.path.join(output_dir, filename))
            plt.close()

    @staticmethod
    def plot_correlation_heatmap(df, output_dir):
        Visualizer.ensure_output_dir(output_dir)
        corr = df.select_dtypes(include='number').corr()

        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm")
        plt.title("Correlation Heatmap")
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        plt.savefig(f"{output_dir}/correlation_heatmap.png")
        plt.close()

    @staticmethod
    def plot_missing_data(df, output_dir):
        Visualizer.ensure_output_dir(output_dir)

        plt.figure(figsize=(10, 4))
        msno.matrix(df)
        plt.title("Missing Data Matrix")
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        plt.savefig(f"{output_dir}/missing_data_matrix.png")
        plt.close()
