import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
from typing import Dict, List, Tuple, Union, Optional, Any, Callable

class ContingencyTable:
    """Class for analyzing and visualizing contingency tables"""
    
    def __init__(self, data: Union[np.ndarray, pd.DataFrame], 
                 row_labels: Optional[List[str]] = None, 
                 col_labels: Optional[List[str]] = None):
        """Initialize a contingency table
        
        Parameters:
        -----------
        data : numpy.ndarray or pandas.DataFrame
            The contingency table data. If numpy array, row and column labels can be specified.
            If DataFrame, the index and column names will be used as labels.
        row_labels : list of str, optional
            Labels for the rows (if data is numpy array)
        col_labels : list of str, optional
            Labels for the columns (if data is numpy array)
        """
        if isinstance(data, pd.DataFrame):
            self.table = data.values
            self.row_labels = list(data.index)
            self.col_labels = list(data.columns)
        else:
            self.table = np.array(data)
            if row_labels is None:
                row_labels = [f"Row {i+1}" for i in range(self.table.shape[0])]
            if col_labels is None:
                col_labels = [f"Col {i+1}" for i in range(self.table.shape[1])]
                
            self.row_labels = row_labels
            self.col_labels = col_labels
        self.n_rows, self.n_cols = self.table.shape
        self.row_totals = self.table.sum(axis=1)
        self.col_totals = self.table.sum(axis=0)
        self.grand_total = self.table.sum()
        self.row_proportions = self.table / self.row_totals[:, np.newaxis]
        self.col_proportions = self.table / self.col_totals
        self.total_proportions = self.table / self.grand_total
        
    def expected_frequencies(self) -> np.ndarray:
        """Calculate expected frequencies under independence
        
        Returns:
        --------
        numpy.ndarray : Expected frequencies
        """
        expected = np.outer(self.row_totals, self.col_totals) / self.grand_total
        return expected
    
    def chi_square_test(self) -> Dict[str, Any]:
        """Perform chi-square test of independence
        
        Returns:
        --------
        dict : Dictionary with test results
        """
        chi2_stat, p_value, dof, expected = stats.chi2_contingency(self.table)
        contributions = (self.table - expected)**2 / expected
        
        return {
            'chi2_statistic': chi2_stat,
            'p_value': p_value,
            'degrees_of_freedom': dof,
            'expected_frequencies': expected,
            'chi2_contributions': contributions,
            'critical_value': stats.chi2.ppf(0.95, dof),  # 95% critical value
            'reject_null': p_value < 0.05,
            'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} the null hypothesis at α = 0.05."
        }
    
    def plot(self, kind: str = 'heatmap', **kwargs) -> plt.Figure:
        """Plot the contingency table
        
        Parameters:
        -----------
        kind : str, optional
            Type of plot: 'heatmap', 'mosaic', or 'bar'. Default is 'heatmap'.
        **kwargs :
            Additional keyword arguments for the plots
            
        Returns:
        --------
        matplotlib.figure.Figure
        """
        if kind == 'heatmap':
            return self._plot_heatmap(**kwargs)
        elif kind == 'mosaic':
            return self._plot_mosaic(**kwargs)
        elif kind == 'bar':
            return self._plot_bar(**kwargs)
        else:
            raise ValueError(f"Unknown plot type: {kind}. Choose from 'heatmap', 'mosaic', or 'bar'.")
    
    def _plot_heatmap(self, annot: bool = True, cmap: str = 'YlGnBu', 
                     figsize: Tuple[int, int] = (10, 8), **kwargs) -> plt.Figure:
        """Create a heatmap of the contingency table"""
        fig, ax = plt.subplots(figsize=figsize)
        im = ax.imshow(self.table, cmap=cmap)
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel('Frequency', rotation=-90, va='bottom')
        ax.set_xticks(np.arange(self.n_cols))
        ax.set_yticks(np.arange(self.n_rows))
        ax.set_xticklabels(self.col_labels)
        ax.set_yticklabels(self.row_labels)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
        if annot:
            for i in range(self.n_rows):
                for j in range(self.n_cols):
                    text = ax.text(j, i, self.table[i, j],
                                  ha='center', va='center', color='black')
        
        ax.set_title('Contingency Table', **kwargs.pop('title_kwargs', {}))
        fig.tight_layout()
        return fig
    
    def _plot_mosaic(self, figsize: Tuple[int, int] = (10, 8), **kwargs) -> plt.Figure:
        """Create a mosaic plot of the contingency table"""
        from matplotlib import patches
        
        fig, ax = plt.subplots(figsize=figsize)
        col_widths = self.col_totals / self.grand_total
        for j, col_width in enumerate(col_widths):
            col_start = np.sum(col_widths[:j])
            if self.col_totals[j] > 0:
                heights = self.table[:, j] / self.col_totals[j]
            else:
                heights = np.zeros(self.n_rows)
            y_offset = 0
            for i, height in enumerate(heights):
                rect = patches.Rectangle(
                    (col_start, y_offset), col_width, height,
                    linewidth=1, edgecolor='black', facecolor=plt.cm.tab10(i % 10)
                )
                y_offset += height
                ax.add_patch(rect)
        for j, col_width in enumerate(col_widths):
            col_middle = np.sum(col_widths[:j]) + col_width / 2
            ax.text(col_middle, -0.05, self.col_labels[j], 
                   ha='center', va='top', fontsize=10)
        handles = [patches.Patch(color=plt.cm.tab10(i % 10), label=self.row_labels[i]) 
                 for i in range(self.n_rows)]
        ax.legend(handles=handles, bbox_to_anchor=(1.05, 1), loc='upper left')
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title('Mosaic Plot', **kwargs.pop('title_kwargs', {}))
        
        fig.tight_layout()
        return fig
    
    def _plot_bar(self, stacked: bool = True, figsize: Tuple[int, int] = (10, 8), 
                 **kwargs) -> plt.Figure:
        """Create a bar plot of the contingency table"""
        fig, ax = plt.subplots(figsize=figsize)
        
        x = np.arange(self.n_cols)
        bar_width = 0.8
        colors = plt.cm.tab10.colors
        
        if stacked:
            bottom = np.zeros(self.n_cols)
            for i in range(self.n_rows):
                ax.bar(x, self.table[i, :], bar_width, bottom=bottom, 
                      label=self.row_labels[i], color=colors[i % len(colors)])
                bottom += self.table[i, :]
        else:
            bar_width = 0.8 / self.n_rows
            offsets = np.linspace(-0.4, 0.4, self.n_rows)
            
            for i in range(self.n_rows):
                ax.bar(x + offsets[i], self.table[i, :], bar_width, 
                      label=self.row_labels[i], color=colors[i % len(colors)])
        
        ax.set_ylabel('Frequency')
        ax.set_title('Bar Plot of Contingency Table', **kwargs.pop('title_kwargs', {}))
        ax.set_xticks(x)
        ax.set_xticklabels(self.col_labels)
        ax.legend()
        
        fig.tight_layout()
        return fig
    
    def print_summary(self, round_to: int = 2) -> None:
        """Print a summary of the contingency table
        
        Parameters:
        -----------
        round_to : int, optional
            Number of decimal places to round to. Default is 2.
        """
        print("=== Contingency Table Summary ===")
        print("\nObserved Frequencies:")
        observed_df = pd.DataFrame(self.table, index=self.row_labels, columns=self.col_labels)
        observed_df.loc['Total'] = observed_df.sum()
        observed_df['Total'] = observed_df.sum(axis=1)
        print(observed_df)
        print("\nExpected Frequencies (under independence):")
        expected = self.expected_frequencies()
        expected_df = pd.DataFrame(expected, index=self.row_labels, columns=self.col_labels)
        print(expected_df.round(round_to))
        chi2_results = self.chi_square_test()
        print("\nChi-Square Test of Independence:")
        print(f"Chi-square statistic: {chi2_results['chi2_statistic']:.{round_to}f}")
        print(f"Degrees of freedom: {chi2_results['degrees_of_freedom']}")
        print(f"P-value: {chi2_results['p_value']:.{round_to}f}")
        print(f"Critical value (α = 0.05): {chi2_results['critical_value']:.{round_to}f}")
        print(f"Conclusion: {chi2_results['conclusion']}")
        print("\nPercentages by Row:")
        row_pct_df = pd.DataFrame(self.row_proportions * 100, index=self.row_labels, columns=self.col_labels)
        print(row_pct_df.round(round_to))
        
        print("\nPercentages by Column:")
        col_pct_df = pd.DataFrame((self.table / self.col_totals[np.newaxis, :]) * 100, 
                                  index=self.row_labels, columns=self.col_labels)
        print(col_pct_df.round(round_to))
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert contingency table to pandas DataFrame
        
        Returns:
        --------
        pandas.DataFrame
        """
        return pd.DataFrame(self.table, index=self.row_labels, columns=self.col_labels)
    
    def __repr__(self) -> str:
        """String representation of the contingency table"""
        return str(self.to_dataframe())


def chi_square_goodness_of_fit(observed: np.ndarray, expected: Optional[np.ndarray] = None,
                             categories: Optional[List[str]] = None) -> Dict[str, Any]:
    """Perform chi-square goodness of fit test
    
    Parameters:
    -----------
    observed : array-like
        Observed frequencies
    expected : array-like, optional
        Expected frequencies. If None, assumes equal probability for all categories.
    categories : list of str, optional
        Category labels for the data. Default is None.
        
    Returns:
    --------
    dict with test results
    """
    observed = np.array(observed)
    
    if expected is None:
        expected = np.ones_like(observed) * observed.sum() / observed.size
    else:
        expected = np.array(expected)
        if np.abs(expected.sum() - 1.0) < 1e-10:
            expected = expected * observed.sum()
    
    if categories is None:
        categories = [f"Category {i+1}" for i in range(observed.size)]
    chi2_stat, p_value = stats.chisquare(observed, expected)
    dof = observed.size - 1
    contributions = (observed - expected)**2 / expected
    result = {
        'chi2_statistic': chi2_stat,
        'p_value': p_value,
        'degrees_of_freedom': dof,
        'observed': observed,
        'expected': expected,
        'categories': categories,
        'chi2_contributions': contributions,
        'critical_value': stats.chi2.ppf(0.95, dof),
        'reject_null': p_value < 0.05,
        'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} the null hypothesis at α = 0.05."
    }
    
    return result


def plot_chi_square_goodness_of_fit(result: Dict[str, Any], figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """Create a plot for chi-square goodness of fit test results
    
    Parameters:
    -----------
    result : dict
        Result dictionary from chi_square_goodness_of_fit
    figsize : tuple, optional
        Figure size. Default is (10, 6).
        
    Returns:
    --------
    matplotlib.figure.Figure
    """
    observed = result['observed']
    expected = result['expected']
    categories = result['categories']
    contributions = result['chi2_contributions']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    x = np.arange(len(categories))
    width = 0.35
    ax1.bar(x - width/2, observed, width, label='Observed', color='steelblue')
    ax1.bar(x + width/2, expected, width, label='Expected', color='orange')
    
    ax1.set_ylabel('Frequency')
    ax1.set_title('Observed vs Expected Frequencies')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories)
    ax1.legend()
    ax2.bar(x, contributions, color='red', alpha=0.7)
    ax2.axhline(y=contributions.mean(), color='black', linestyle='--', 
               label=f'Average Contribution: {contributions.mean():.2f}')
    
    ax2.set_ylabel('Contribution to Chi-Square')
    ax2.set_title('Chi-Square Contributions by Category')
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories)
    ax2.legend()
    fig.suptitle(f"Chi-Square Goodness of Fit Test Results\n" 
                f"χ² = {result['chi2_statistic']:.2f}, df = {result['degrees_of_freedom']}, "
                f"p-value = {result['p_value']:.4f}", 
                fontsize=14)
    
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    return fig


def fisher_exact_test(table: np.ndarray) -> Dict[str, Any]:
    """Perform Fisher's exact test for 2x2 contingency tables
    
    Parameters:
    -----------
    table : array-like
        2x2 contingency table
        
    Returns:
    --------
    dict with test results
    """
    table = np.array(table)
    
    if table.shape != (2, 2):
        raise ValueError("Fisher's exact test requires a 2x2 contingency table")
    odds_ratio, p_value = stats.fisher_exact(table)
    result = {
        'odds_ratio': odds_ratio,
        'p_value': p_value,
        'table': table,
        'reject_null': p_value < 0.05,
        'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} the null hypothesis at α = 0.05."
    }
    
    return result


def mcnemar_test(table: np.ndarray) -> Dict[str, Any]:
    """Perform McNemar's test for paired nominal data
    
    Parameters:
    -----------
    table : array-like
        2x2 contingency table
        
    Returns:
    --------
    dict with test results
    """
    table = np.array(table)
    
    if table.shape != (2, 2):
        raise ValueError("McNemar's test requires a 2x2 contingency table")
    result = stats.mcnemar(table, exact=False, correction=True)
    b = table[0, 1]  # off-diagonal elements
    c = table[1, 0]
    odds_ratio = b / c if c != 0 else np.inf if b != 0 else np.nan
    return {
        'statistic': result.statistic,
        'p_value': result.pvalue,
        'odds_ratio': odds_ratio,
        'table': table,
        'reject_null': result.pvalue < 0.05,
        'conclusion': f"{'Reject' if result.pvalue < 0.05 else 'Fail to reject'} the null hypothesis at α = 0.05."
    }


def cramers_v(table: np.ndarray) -> float:
    """Calculate Cramér's V for a contingency table
    
    Parameters:
    -----------
    table : array-like
        Contingency table
        
    Returns:
    --------
    float : Cramér's V statistic
    """
    table = np.array(table)
    chi2 = stats.chi2_contingency(table)[0]
    n = table.sum()
    r, k = table.shape
    phi2 = chi2 / n
    phi2corr = max(0, phi2 - ((k-1)*(r-1))/(n-1))
    rcorr = r - ((r-1)**2)/(n-1)
    kcorr = k - ((k-1)**2)/(n-1)
    
    return np.sqrt(phi2corr / min(kcorr-1, rcorr-1))


def contingency_residuals(table: np.ndarray) -> Dict[str, np.ndarray]:
    """Calculate residuals for a contingency table
    
    Parameters:
    -----------
    table : array-like
        Contingency table
        
    Returns:
    --------
    dict with different types of residuals
    """
    table = np.array(table)
    row_totals = table.sum(axis=1, keepdims=True)
    col_totals = table.sum(axis=0, keepdims=True)
    grand_total = table.sum()
    expected = row_totals @ col_totals / grand_total
    residuals = table - expected
    std_residuals = residuals / np.sqrt(expected)
    adj_denominator = np.sqrt(expected * (1 - row_totals / grand_total) * (1 - col_totals / grand_total))
    adj_residuals = residuals / adj_denominator
    
    return {
        'raw_residuals': residuals,
        'standardized_residuals': std_residuals,
        'adjusted_residuals': adj_residuals,
        'expected': expected
    }


def plot_residuals(table: np.ndarray, row_labels: Optional[List[str]] = None, 
                  col_labels: Optional[List[str]] = None, 
                  figsize: Tuple[int, int] = (10, 8)) -> plt.Figure:
    """Plot adjusted residuals from a contingency table
    
    Parameters:
    -----------
    table : array-like
        Contingency table
    row_labels : list of str, optional
        Labels for the rows. Default is None.
    col_labels : list of str, optional
        Labels for the columns. Default is None.
    figsize : tuple, optional
        Figure size. Default is (10, 8).
        
    Returns:
    --------
    matplotlib.figure.Figure
    """
    table = np.array(table)
    r, c = table.shape
    if row_labels is None:
        row_labels = [f"Row {i+1}" for i in range(r)]
    if col_labels is None:
        col_labels = [f"Col {i+1}" for i in range(c)]
    res = contingency_residuals(table)
    adj_residuals = res['adjusted_residuals']
    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(adj_residuals, cmap='RdBu_r', vmin=-4, vmax=4)
    ax.set_xticks(np.arange(c))
    ax.set_yticks(np.arange(r))
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('Adjusted Residuals', rotation=-90, va='bottom')
    for i in range(r):
        for j in range(c):
            value = adj_residuals[i, j]
            color = 'white' if abs(value) > 2.5 else 'black'
            text = ax.text(j, i, f"{value:.2f}", ha='center', va='center', color=color)
    
    ax.set_title('Adjusted Residuals (>2 or <-2 are significant)')
    fig.tight_layout()
    return fig