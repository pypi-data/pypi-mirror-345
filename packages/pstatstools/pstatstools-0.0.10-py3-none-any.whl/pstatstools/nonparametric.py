import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
from typing import Dict, List, Tuple, Union, Optional, Any, Callable

def mann_whitney_test(x: np.ndarray, y: np.ndarray, alternative: str = 'two-sided') -> Dict[str, Any]:
    """Perform Mann-Whitney U test (non-parametric alternative to t-test for independent samples)
    
    Parameters:
    -----------
    x : array-like
        First sample
    y : array-like
        Second sample
    alternative : str, optional
        Alternative hypothesis: 'two-sided' (default), 'less', or 'greater'
        
    Returns:
    --------
    dict with test results
    """
    x = np.asarray(x)
    y = np.asarray(y)
    statistic, p_value = stats.mannwhitneyu(x, y, alternative=alternative)
    n1, n2 = len(x), len(y)
    n_total = n1 + n2
    u_max = n1 * n2
    mean_rank_x = np.mean(stats.rankdata(np.concatenate([x, y]))[:n1])
    mean_rank_y = np.mean(stats.rankdata(np.concatenate([x, y]))[n1:])
    z = (statistic - u_max / 2) / np.sqrt(u_max * (n1 + n2 + 1) / 12)
    effect_size_r = abs(z) / np.sqrt(n_total)
    result = {
        'test': f"Mann-Whitney U ({alternative})",
        'statistic': statistic,
        'p_value': p_value,
        'n1': n1,
        'n2': n2,
        'mean_rank_1': mean_rank_x,
        'mean_rank_2': mean_rank_y,
        'effect_size_r': effect_size_r,
        'effect_size_interpretation': interpret_effect_size_r(effect_size_r),
        'alternative': alternative,
        'reject_null': p_value < 0.05,
        'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} the null hypothesis at α = 0.05."
    }
    
    return result


def wilcoxon_test(x: np.ndarray, y: Optional[np.ndarray] = None, zero_method: str = 'wilcox',
                 alternative: str = 'two-sided') -> Dict[str, Any]:
    """Perform Wilcoxon signed-rank test (non-parametric alternative to paired t-test)
    
    Parameters:
    -----------
    x : array-like
        First sample or differences if y is None
    y : array-like, optional
        Second sample. If None, x is treated as differences. Default is None.
    zero_method : str, optional
        Method for handling zeros: 'wilcox', 'pratt', or 'zsplit'. Default is 'wilcox'.
    alternative : str, optional
        Alternative hypothesis: 'two-sided' (default), 'less', or 'greater'
        
    Returns:
    --------
    dict with test results
    """
    x = np.asarray(x)
    
    if y is not None:
        y = np.asarray(y)
        d = x - y
    else:
        d = x
    statistic, p_value = stats.wilcoxon(d, zero_method=zero_method, alternative=alternative)
    n = len(d)
    n_nonzero = np.sum(d != 0)
    n_pos = np.sum(d > 0)
    n_neg = np.sum(d < 0)
    n_zero = np.sum(d == 0)
    if n_nonzero > 0:
        z = (statistic - (n_nonzero * (n_nonzero + 1) / 4)) / np.sqrt(n_nonzero * (n_nonzero + 1) * (2 * n_nonzero + 1) / 24)
        effect_size_r = abs(z) / np.sqrt(n)
    else:
        effect_size_r = np.nan
    result = {
        'test': f"Wilcoxon Signed-Rank ({alternative})",
        'statistic': statistic,
        'p_value': p_value,
        'n': n,
        'n_nonzero': n_nonzero,
        'n_positive': n_pos,
        'n_negative': n_neg,
        'n_zero': n_zero,
        'effect_size_r': effect_size_r,
        'effect_size_interpretation': interpret_effect_size_r(effect_size_r),
        'alternative': alternative,
        'reject_null': p_value < 0.05,
        'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} the null hypothesis at α = 0.05."
    }
    
    return result


def sign_test(x: np.ndarray, y: Optional[np.ndarray] = None, alternative: str = 'two-sided') -> Dict[str, Any]:
    """Perform sign test (a simple non-parametric test for paired samples)
    
    Parameters:
    -----------
    x : array-like
        First sample or differences if y is None
    y : array-like, optional
        Second sample. If None, x is treated as differences. Default is None.
    alternative : str, optional
        Alternative hypothesis: 'two-sided' (default), 'less', or 'greater'
        
    Returns:
    --------
    dict with test results
    """
    x = np.asarray(x)
    
    if y is not None:
        y = np.asarray(y)
        d = x - y
    else:
        d = x
    n_pos = np.sum(d > 0)
    n_neg = np.sum(d < 0)
    n_zero = np.sum(d == 0)
    n = n_pos + n_neg  # Exclude zeros
    statistic = min(n_pos, n_neg)
    if alternative == 'two-sided':
        p_value = 2 * stats.binom.cdf(statistic, n, 0.5)
    elif alternative == 'less':
        p_value = stats.binom.cdf(n_pos, n, 0.5)
    else:  # 'greater'
        p_value = stats.binom.cdf(n_neg, n, 0.5)
    p_value = min(p_value, 1.0)
    result = {
        'test': f"Sign Test ({alternative})",
        'statistic': statistic,
        'p_value': p_value,
        'n': n_pos + n_neg + n_zero,  # Total including zeros
        'n_nonzero': n,  # Excluding zeros
        'n_positive': n_pos,
        'n_negative': n_neg,
        'n_zero': n_zero,
        'alternative': alternative,
        'reject_null': p_value < 0.05,
        'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} the null hypothesis at α = 0.05."
    }
    
    return result


def kruskal_wallis_test(samples: List[np.ndarray], 
                       sample_names: Optional[List[str]] = None) -> Dict[str, Any]:
    """Perform Kruskal-Wallis H test (non-parametric alternative to one-way ANOVA)
    
    Parameters:
    -----------
    samples : list of array-like
        List of samples to compare
    sample_names : list of str, optional
        Names for the samples. Default is None (uses Sample 1, Sample 2, etc.).
        
    Returns:
    --------
    dict with test results
    """
    samples = [np.asarray(sample) for sample in samples]
    if sample_names is None:
        sample_names = [f"Sample {i+1}" for i in range(len(samples))]
    statistic, p_value = stats.kruskal(*samples)
    df = len(samples) - 1
    n_samples = [len(sample) for sample in samples]
    n_total = sum(n_samples)
    all_data = np.concatenate(samples)
    all_ranks = stats.rankdata(all_data)
    start_idx = 0
    mean_ranks = []
    for n in n_samples:
        mean_ranks.append(np.mean(all_ranks[start_idx:start_idx+n]))
        start_idx += n
    result = {
        'test': "Kruskal-Wallis H Test",
        'statistic': statistic,
        'p_value': p_value,
        'degrees_of_freedom': df,
        'sample_sizes': n_samples,
        'sample_names': sample_names,
        'mean_ranks': mean_ranks,
        'critical_value': stats.chi2.ppf(0.95, df),  # 95% critical value from chi-square
        'reject_null': p_value < 0.05,
        'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} the null hypothesis at α = 0.05."
    }
    
    return result


def friedman_test(data: np.ndarray, blocks: Optional[np.ndarray] = None,
                treatments: Optional[np.ndarray] = None) -> Dict[str, Any]:
    """Perform Friedman test (non-parametric alternative to repeated measures ANOVA)
    
    Parameters:
    -----------
    data : array-like
        Data matrix where rows are blocks (subjects) and columns are treatments,
        or a 1-D array if blocks and treatments are specified
    blocks : array-like, optional
        Block labels (required if data is 1-D). Default is None.
    treatments : array-like, optional
        Treatment labels (required if data is 1-D). Default is None.
        
    Returns:
    --------
    dict with test results
    """
    data = np.asarray(data)
    if data.ndim == 1:
        if blocks is None or treatments is None:
            raise ValueError("blocks and treatments must be provided if data is 1-D")
        blocks = np.asarray(blocks)
        treatments = np.asarray(treatments)
        
        unique_blocks = np.unique(blocks)
        unique_treatments = np.unique(treatments)
        
        n_blocks = len(unique_blocks)
        n_treatments = len(unique_treatments)
        
        data_matrix = np.full((n_blocks, n_treatments), np.nan)
        
        for i, block in enumerate(unique_blocks):
            for j, treatment in enumerate(unique_treatments):
                mask = (blocks == block) & (treatments == treatment)
                if np.any(mask):
                    data_matrix[i, j] = data[mask][0]  # Assuming one measurement per block-treatment
    else:
        data_matrix = data
        n_blocks, n_treatments = data_matrix.shape
    statistic, p_value = stats.friedmanchisquare(*[data_matrix[:, j] for j in range(n_treatments)])
    df = n_treatments - 1
    ranks = np.zeros_like(data_matrix)
    for i in range(n_blocks):
        ranks[i, :] = stats.rankdata(data_matrix[i, :])
    
    mean_ranks = np.mean(ranks, axis=0)
    result = {
        'test': "Friedman Test",
        'statistic': statistic,
        'p_value': p_value,
        'degrees_of_freedom': df,
        'n_blocks': n_blocks,
        'n_treatments': n_treatments,
        'mean_ranks': mean_ranks,
        'critical_value': stats.chi2.ppf(0.95, df),  # 95% critical value from chi-square
        'reject_null': p_value < 0.05,
        'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} the null hypothesis at α = 0.05."
    }
    
    return result


def interpret_effect_size_r(r: float) -> str:
    """Interpret effect size r for non-parametric tests
    
    Parameters:
    -----------
    r : float
        Effect size r value
        
    Returns:
    --------
    str : Interpretation of effect size
    """
    if np.isnan(r):
        return "Unable to calculate"
    elif r < 0.1:
        return "Negligible effect"
    elif r < 0.3:
        return "Small effect"
    elif r < 0.5:
        return "Medium effect"
    else:
        return "Large effect"


def runs_test(x: np.ndarray, threshold: Optional[float] = None) -> Dict[str, Any]:
    """Perform Wald-Wolfowitz runs test for randomness
    
    Parameters:
    -----------
    x : array-like
        Data sequence
    threshold : float, optional
        Threshold for converting to binary sequence. If None, median is used. Default is None.
        
    Returns:
    --------
    dict with test results
    """
    x = np.asarray(x)
    if threshold is None:
        threshold = np.median(x)
    binary = (x > threshold).astype(int)
    runs = np.diff(np.hstack(([0], binary, [0])) != 0).sum() - 1
    n1 = np.sum(binary == 0)
    n2 = np.sum(binary == 1)
    n = n1 + n2
    expected_runs = 1 + (2 * n1 * n2) / n
    var_runs = (2 * n1 * n2 * (2 * n1 * n2 - n)) / (n**2 * (n - 1))
    z = (runs - expected_runs) / np.sqrt(var_runs)
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    result = {
        'test': "Runs Test for Randomness",
        'runs': runs,
        'expected_runs': expected_runs,
        'n1': n1,  # Number of values below/equal to threshold
        'n2': n2,  # Number of values above threshold
        'threshold': threshold,
        'z_statistic': z,
        'p_value': p_value,
        'reject_null': p_value < 0.05,
        'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} the null hypothesis at α = 0.05."
    }
    
    return result


def plot_nonparametric_test(result: Dict[str, Any], data1: np.ndarray, 
                          data2: Optional[np.ndarray] = None,
                          figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """Create a visualization for non-parametric test results
    
    Parameters:
    -----------
    result : dict
        Result dictionary from a non-parametric test function
    data1 : array-like
        First sample
    data2 : array-like, optional
        Second sample. Default is None.
    figsize : tuple, optional
        Figure size. Default is (10, 6).
        
    Returns:
    --------
    matplotlib.figure.Figure
    """
    test_name = result.get('test', 'Non-parametric Test')
    if "Mann-Whitney" in test_name or "Wilcoxon" in test_name or "Sign Test" in test_name:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        if "Wilcoxon" in test_name or "Sign Test" in test_name and data2 is not None:
            diff = np.asarray(data1) - np.asarray(data2)
            ax1.hist(diff, bins='auto', alpha=0.7, color='skyblue', 
                    edgecolor='black', label='Differences')
            ax1.axvline(0, color='red', linestyle='--', linewidth=2, label='Zero')
            ax1.set_xlabel('Differences (Sample 1 - Sample 2)')
            ax1.set_ylabel('Frequency')
            ax1.set_title('Histogram of Differences')
            ax1.legend()
            ax2.scatter(data1, data2, alpha=0.7)
            min_val = min(np.min(data1), np.min(data2))
            max_val = max(np.max(data1), np.max(data2))
            ax2.plot([min_val, max_val], [min_val, max_val], 'r--', label='Identity Line')
            
            ax2.set_xlabel('Sample 1')
            ax2.set_ylabel('Sample 2')
            ax2.set_title('Paired Samples')
            ax2.legend()
            
        else:  # For Mann-Whitney (unpaired)
            boxdata = [data1, data2] if data2 is not None else [data1]
            labels = ['Sample 1', 'Sample 2'] if data2 is not None else ['Sample 1']
            
            ax1.boxplot(boxdata, labels=labels, notch=True)
            ax1.set_ylabel('Value')
            ax1.set_title('Box Plots')
            ax2.violinplot(boxdata, showmeans=True, showmedians=True)
            ax2.set_xticks(np.arange(1, len(boxdata) + 1))
            ax2.set_xticklabels(labels)
            ax2.set_ylabel('Value')
            ax2.set_title('Violin Plots')
    
    elif "Kruskal-Wallis" in test_name or "Friedman" in test_name:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        if "Friedman" in test_name and data1.ndim > 1:
            samples = [data1[:, j] for j in range(data1.shape[1])]
            sample_names = result.get('sample_names', [f"Treatment {j+1}" for j in range(data1.shape[1])])
        else:
            if isinstance(data1, list):
                samples = data1
            else:
                samples = [data1]
                if data2 is not None:
                    if isinstance(data2, list):
                        samples.extend(data2)
                    else:
                        samples.append(data2)
            
            sample_names = result.get('sample_names', [f"Sample {i+1}" for i in range(len(samples))])
        ax1.boxplot(samples, labels=sample_names, notch=True)
        ax1.set_ylabel('Value')
        ax1.set_title('Box Plots')
        mean_ranks = result.get('mean_ranks', [])
        if len(mean_ranks) > 0:
            x = np.arange(len(mean_ranks))
            ax2.bar(x, mean_ranks, alpha=0.7)
            ax2.set_xticks(x)
            ax2.set_xticklabels(sample_names, rotation=45, ha='right')
            ax2.set_ylabel('Mean Rank')
            ax2.set_title('Mean Ranks by Sample')
    
    else:  # General case
        fig, ax = plt.subplots(figsize=figsize)
        if data2 is not None:
            ax.boxplot([data1, data2], labels=['Sample 1', 'Sample 2'], notch=True)
        else:
            ax.boxplot([data1], labels=['Sample 1'], notch=True)
        
        ax.set_ylabel('Value')
        ax.set_title('Box Plot of Data')
    test_result_text = (
        f"{test_name}\n"
        f"Statistic: {result.get('statistic', 'N/A'):.4f}\n"
        f"p-value: {result.get('p_value', 'N/A'):.4f}\n"
        f"Conclusion: {result.get('conclusion', 'N/A')}"
    )
    
    if 'effect_size_r' in result and not np.isnan(result['effect_size_r']):
        test_result_text += f"\nEffect size (r): {result['effect_size_r']:.4f} ({result.get('effect_size_interpretation', 'N/A')})"
    
    plt.figtext(0.5, 0.01, test_result_text, ha='center', bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 5})
    
    fig.tight_layout(rect=[0, 0.1, 1, 0.95])
    fig.suptitle(test_name, fontsize=14, y=0.98)
    
    return fig


def dunn_posthoc_test(samples: List[np.ndarray], p_adjust: str = 'bonferroni') -> pd.DataFrame:
    """Perform Dunn's post-hoc test after Kruskal-Wallis
    
    Parameters:
    -----------
    samples : list of array-like
        List of samples to compare
    p_adjust : str, optional
        Method for p-value adjustment for multiple comparisons:
        'bonferroni', 'sidak', 'holm', 'fdr_bh', etc. Default is 'bonferroni'.
        
    Returns:
    --------
    pandas.DataFrame with pairwise comparisons
    """
    from statsmodels.stats.multicomp import pairwise_tukeyhsd
    from scipy.stats.distributions import norm
    from statsmodels.stats.multitest import multipletests
    samples = [np.asarray(sample) for sample in samples]
    all_data = np.concatenate(samples)
    all_ranks = stats.rankdata(all_data)
    n_samples = len(samples)
    sample_sizes = [len(sample) for sample in samples]
    total_size = sum(sample_sizes)
    start_idx = 0
    sample_ranks = []
    mean_ranks = []
    for n in sample_sizes:
        ranks = all_ranks[start_idx:start_idx+n]
        sample_ranks.append(ranks)
        mean_ranks.append(np.mean(ranks))
        start_idx += n
    pairwise_data = []
    
    for i in range(n_samples):
        for j in range(i+1, n_samples):
            mean_rank_diff = mean_ranks[i] - mean_ranks[j]
            se = np.sqrt((total_size * (total_size + 1) / 12) * 
                         (1 / sample_sizes[i] + 1 / sample_sizes[j]))
            z_score = mean_rank_diff / se
            p_value = 2 * (1 - norm.cdf(abs(z_score)))
            
            pairwise_data.append({
                'group1': f"Sample {i+1}",
                'group2': f"Sample {j+1}",
                'mean_rank1': mean_ranks[i],
                'mean_rank2': mean_ranks[j],
                'mean_rank_diff': mean_rank_diff,
                'z_score': z_score,
                'p_value': p_value,
                'significant': False  # Will be updated after adjustment
            })
    posthoc_df = pd.DataFrame(pairwise_data)
    if n_samples > 2:  # Only adjust if there are more than 2 groups
        adjusted_p = multipletests(posthoc_df['p_value'].values, method=p_adjust)[1]
        posthoc_df['p_adj'] = adjusted_p
        posthoc_df['significant'] = posthoc_df['p_adj'] < 0.05
    else:
        posthoc_df['p_adj'] = posthoc_df['p_value']
        posthoc_df['significant'] = posthoc_df['p_value'] < 0.05
    
    return posthoc_df


def jonckheere_trend_test(samples: List[np.ndarray]) -> Dict[str, Any]:
    """Perform Jonckheere-Terpstra test for ordered alternatives
    
    Parameters:
    -----------
    samples : list of array-like
        List of samples in hypothesized order
        
    Returns:
    --------
    dict with test results
    """
    samples = [np.asarray(sample) for sample in samples]
    n_samples = len(samples)
    j_stat = 0
    
    for i in range(n_samples):
        for j in range(i+1, n_samples):
            count = 0
            for xi in samples[i]:
                for xj in samples[j]:
                    if xi < xj:
                        count += 1
            j_stat += count
    sample_sizes = [len(sample) for sample in samples]
    n_total = sum(sample_sizes)
    mean_j = 0
    for i in range(n_samples):
        for j in range(i+1, n_samples):
            mean_j += sample_sizes[i] * sample_sizes[j] / 2
    
    var_j = 0
    N = sum(sample_sizes)
    for i in range(n_samples):
        for j in range(i+1, n_samples):
            var_j += sample_sizes[i] * sample_sizes[j] * (sample_sizes[i] + sample_sizes[j] + 1) / 12
    z = (j_stat - mean_j) / np.sqrt(var_j)
    p_value = 1 - stats.norm.cdf(z)
    result = {
        'test': "Jonckheere-Terpstra Trend Test",
        'statistic': j_stat,
        'mean_j': mean_j,
        'var_j': var_j,
        'z_statistic': z,
        'p_value': p_value,
        'n_samples': n_samples,
        'sample_sizes': sample_sizes,
        'reject_null': p_value < 0.05,
        'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} the null hypothesis at α = 0.05."
    }
    
    return result