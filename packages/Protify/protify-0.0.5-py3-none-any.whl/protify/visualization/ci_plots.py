import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import r2_score
from .pauc.pauc import plot_roc_with_ci


def regression_ci_plot(y_true, y_pred, save_path, title=None):
    """
    Calculate the spearman rho and p-value of the regression model.
    Plot the line of best fit with 95% confidence intervals for spearman rho.
    Display the R-squared value, spearman rho, pearson rho, and p-values.
    """
    # Compute R‑squared, Spearman and Pearson correlations
    y_true, y_pred = y_true.flatten(), y_pred.flatten()
    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    y_true, y_pred = y_true[mask], y_pred[mask]
    r2 = r2_score(y_true, y_pred)
    r_s, p_s = spearmanr(y_true, y_pred)
    r_p, p_p = pearsonr(y_true, y_pred)

    # Create scatter plot and regression line with 95% CI
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(x=y_true, y=y_pred, ax=ax)
    sns.regplot(
        x=y_true, y=y_pred,
        ci=95, ax=ax, scatter=False,
        line_kws={'color': 'red'}
    )

    ax.set_xlabel('True Values')
    ax.set_ylabel('Predicted Values')
    if title:
        ax.set_title(title)
    else:
        ax.set_title('Regression Plot with 95% Confidence Interval')

    # Annotate statistics on the plot
    stats_text = (
        f"$R^2$ = {r2:.2f}\n"
        f"Spearman $\\rho$ = {r_s:.2f}  (p = {p_s:.2e})\n"
        f"Pearson $\\rho$ = {r_p:.2f}  (p = {p_p:.2e})"
    )
    ax.text(
        0.05, 0.95, stats_text,
        transform=ax.transAxes,
        fontsize=12, verticalalignment='top'
    )

    # Save the figure
    fig.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close(fig)


def classification_ci_plot(y_true, y_pred, save_path, title=None):
    """
    Use pauc to display classification plot
    """
    try:
        plot_roc_with_ci(y_true, y_pred, save_path, fig_title=title)
    except Exception as e:
        print(f"Error plotting pAUC curve, likely the wrong version: {e}")


if __name__ == "__main__":
    # py -m visualization.ci_plots
    y_true = np.random.rand(100)
    y_pred = np.random.rand(100)
    regression_ci_plot(y_true, y_pred, "plots/test_plots/regression.png", title="Regression Plot")

    y_true = np.random.randint(0, 2, 100)
    y_pred = np.random.rand(100, 2)
    classification_ci_plot(y_true, y_pred, "plots/test_plots/classification.png", title="Classification Plot")
