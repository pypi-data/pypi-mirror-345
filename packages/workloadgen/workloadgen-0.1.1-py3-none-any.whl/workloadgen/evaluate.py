import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def compare_distributions(original_df, generated_df):
    original_df = original_df.replace(-1, np.nan).dropna()
    generated_df = generated_df.replace([np.inf, -np.inf], np.nan).dropna()

    common_cols = original_df.select_dtypes(include=[np.number]).columns.intersection(generated_df.columns)

    num_cols = len(common_cols)
    cols_per_row = 3
    rows = (num_cols + cols_per_row - 1) // cols_per_row
    plt.figure(figsize=(6 * cols_per_row, 4 * rows))

    for i, col in enumerate(common_cols):
        plt.subplot(rows, cols_per_row, i + 1)
        sns.kdeplot(original_df[col], label='Real', fill=True, color='blue')
        sns.kdeplot(generated_df[col], label='Generated', fill=True, color='orange')
        plt.title(f'Distribution of {col}')
        plt.legend()

    plt.tight_layout()
    plt.show()