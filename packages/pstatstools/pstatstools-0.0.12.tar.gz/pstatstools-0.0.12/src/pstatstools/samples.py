import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import statsmodels.stats.power as smp
import math

def sample(sample_data):
    """Factory function to create a Sample object"""
    return Sample(sample_data)

class Sample:
    def __init__(self, sample_data):
        """Initialize a Sample object with data"""
        self.data = np.array(sample_data)
    
    #-----------------------------------------------------------------
    # Basic descriptive statistics
    #-----------------------------------------------------------------
    
    def mean(self):
        """Return the mean of the sample"""
        return self.data.mean()
    
    def median(self):
        """Return the median of the sample"""
        return np.median(self.data)
        
    def mode(self):
        """Return the mode of the sample (most common value)"""
        return stats.mode(self.data, keepdims=False).mode
    
    def quantile(self, q):
        """Return the quantile of the sample
        
        Parameters:
        q : float or array-like
            Quantile or sequence of quantiles to compute, which must be between 0 and 1 inclusive.
        """
        return np.quantile(self.data, q)
    
    def quartiles(self):
        """Return the quartiles (Q1, Q2, Q3) of the sample"""
        return np.quantile(self.data, [0.25, 0.5, 0.75])
    
    def iqr(self):
        """Return the interquartile range (IQR) of the sample"""
        q75, q25 = np.quantile(self.data, [0.75, 0.25])
        return q75 - q25
    
    def std(self, ddof=1):
        """Return the standard deviation of the sample
        
        Parameters:
        ddof : int, optional
            Delta Degrees of Freedom. Default is 1 (sample std).
        """
        return self.data.std(ddof=ddof)
    
    def var(self, ddof=1):
        """Return the variance of the sample
        
        Parameters:
        ddof : int, optional
            Delta Degrees of Freedom. Default is 1 (sample variance).
        """
        return self.data.var(ddof=ddof)
    
    def sem(self):
        """Return the standard error of the mean"""
        return self.std() / math.sqrt(len(self.data))
      
    def standard_error_of_mean(self):
        """Return the standard error of the mean (same as sem())"""
        return self.sem()
    
    def skewness(self):
        """Return the skewness of the sample"""
        return stats.skew(self.data)
    
    def kurtosis(self):
        """Return the kurtosis of the sample"""
        return stats.kurtosis(self.data)
    
    def coef_variation(self):
        """Return the coefficient of variation (CV)"""
        return self.std() / self.mean() if self.mean() != 0 else None
        
    def min(self):
        """Return the minimum value in the sample"""
        return self.data.min()
        
    def max(self):
        """Return the maximum value in the sample"""
        return self.data.max()
        
    def range(self):
        """Return the range (max - min) of the sample"""
        return self.max() - self.min()
    
    #-----------------------------------------------------------------
    # Confidence intervals
    #-----------------------------------------------------------------
    
    def ci(self, confidence=0.95):
        """Return the confidence interval for the mean
        
        Parameters:
        confidence : float, optional
            Confidence level. Default is 0.95 (95% confidence).
        """
        n = len(self.data)
        mean = self.mean()
        sem = self.sem()
        t_crit = stats.t.ppf((1 + confidence) / 2, n-1)
        
        return (mean - t_crit * sem, mean + t_crit * sem)
    
    def ci_std(self, confidence=0.95):
        """Return the confidence interval for the standard deviation
        
        Parameters:
        confidence : float, optional
            Confidence level. Default is 0.95 (95% confidence).
        """
        n = len(self.data)
        s = self.std()
        alpha = 1 - confidence
        chi2_lower = stats.chi2.ppf(alpha/2, n-1)
        chi2_upper = stats.chi2.ppf(1-alpha/2, n-1)
        
        lower = np.sqrt((n-1) * s**2 / chi2_upper)
        upper = np.sqrt((n-1) * s**2 / chi2_lower)
        
        return (lower, upper)
    
    def ci_var(self, confidence=0.95):
        """Return the confidence interval for the variance
        
        Parameters:
        confidence : float, optional
            Confidence level. Default is 0.95 (95% confidence).
        """
        lower, upper = self.ci_std(confidence)
        return (lower**2, upper**2)
    
    def ci_median(self, confidence=0.95):
        """Return the confidence interval for the median
        
        Parameters:
        confidence : float, optional
            Confidence level. Default is 0.95 (95% confidence).
        """
        # Log transformation method for estimating median CI
        data_log = np.log(self.data)
        n = len(self.data)
        std_err = np.std(data_log, ddof=1) / np.sqrt(n)
        
        ci_log = stats.t.interval(confidence, df=n-1, loc=np.mean(data_log), scale=std_err)
        ci_original = (np.exp(ci_log[0]), np.exp(ci_log[1]))
        
        return ci_original
    
    #-----------------------------------------------------------------
    # Hypothesis Testing
    #-----------------------------------------------------------------
    
    def t_test(self, popmean=0, alpha=0.05, tail="two"):
        """Perform one-sample t-test
        
        Parameters:
        popmean : float, optional
            The expected population mean. Default is 0.
        alpha : float, optional
            Significance level. Default is 0.05.
        tail : str, optional
            Type of test: "two", "left", or "right". Default is "two".
            
        Returns:
        dict with test results
        """
        t_stat, p_value = stats.ttest_1samp(self.data, popmean)
        df = len(self.data) - 1
        
        # Adjust p-value for one-tailed tests
        if tail == "left":
            p_value = p_value / 2 if t_stat < 0 else 1 - p_value / 2
        elif tail == "right":
            p_value = p_value / 2 if t_stat > 0 else 1 - p_value / 2
        
        # Calculate critical values
        if tail == "two":
            t_crit = stats.t.ppf(1 - alpha/2, df)
            t_crits = (-t_crit, t_crit)
            reject = abs(t_stat) > t_crit
        elif tail == "right":
            t_crit = stats.t.ppf(1 - alpha, df)
            t_crits = (t_crit,)
            reject = t_stat > t_crit
        elif tail == "left":
            t_crit = stats.t.ppf(alpha, df)
            t_crits = (t_crit,)
            reject = t_stat < t_crit
        else:
            raise ValueError("Invalid tail type. Choose 'two', 'left', or 'right'.")
        
        # Get confidence interval
        ci = self.ci(1-alpha)
        
        return {
            'test': f"{tail}-tailed one-sample t-test",
            'null_hypothesis': f"Population mean equals {popmean}",
            't_statistic': t_stat,
            'p_value': p_value,
            'degrees_of_freedom': df,
            'critical_values': t_crits,
            'confidence_interval': ci,
            'reject_null': reject,
            'conclusion': f"{'Reject' if reject else 'Fail to reject'} the null hypothesis at α = {alpha}."
        }
    
    def welch_test(self, other_sample, alpha=0.05, tail="two"):
        """Perform Welch's t-test for two samples with unequal variances
        
        Parameters:
        other_sample : Sample or array-like
            The other sample to compare with
        alpha : float, optional
            Significance level. Default is 0.05.
        tail : str, optional
            Type of test: "two", "left", or "right". Default is "two".
            
        Returns:
        dict with test results
        """
        # Get data from other sample
        if isinstance(other_sample, Sample):
            other_data = other_sample.data
        else:
            other_data = np.array(other_sample)
        
        # Calculate sample statistics
        n1 = len(self.data)
        n2 = len(other_data)
        s1_sq = np.var(self.data, ddof=1)
        s2_sq = np.var(other_data, ddof=1)
        
        # Calculate effective degrees of freedom (Welch-Satterthwaite equation)
        df = ((s1_sq/n1 + s2_sq/n2)**2) / (
            (s1_sq/n1)**2/(n1-1) + (s2_sq/n2)**2/(n2-1)
        )
        
        # Perform the t-test
        t_stat, p_value = stats.ttest_ind(
            self.data, 
            other_data, 
            equal_var=False  # Welch's t-test
        )
        
        # Adjust p-value for one-tailed tests
        if tail == "left":
            p_value = p_value / 2 if t_stat < 0 else 1 - p_value / 2
        elif tail == "right":
            p_value = p_value / 2 if t_stat > 0 else 1 - p_value / 2
        
        # Calculate critical values
        if tail == "two":
            t_crit = stats.t.ppf(1 - alpha/2, df)
            t_crits = (-t_crit, t_crit)
            reject = abs(t_stat) > t_crit
        elif tail == "right":
            t_crit = stats.t.ppf(1 - alpha, df)
            t_crits = (t_crit,)
            reject = t_stat > t_crit
        elif tail == "left":
            t_crit = stats.t.ppf(alpha, df)
            t_crits = (t_crit,)
            reject = t_stat < t_crit
        else:
            raise ValueError("Invalid tail type. Choose 'two', 'left', or 'right'.")
        
        return {
            'test': f"{tail}-tailed Welch's t-test",
            'null_hypothesis': "The two population means are equal",
            't_statistic': t_stat,
            'p_value': p_value,
            'degrees_of_freedom': df,
            'critical_values': t_crits,
            'reject_null': reject,
            'conclusion': f"{'Reject' if reject else 'Fail to reject'} the null hypothesis at α = {alpha}."
        }
    
    def anova(self, *other_samples):
        """Perform one-way ANOVA to compare multiple samples
        Parameters:
        *other_samples : Sample objects or array-like
            The other samples to compare with
        Returns:
        dict with ANOVA results including:
            - test statistics
            - p-value
            - degrees of freedom
            - grand mean
            - group means
            - effect estimates (group mean - grand mean)
            - group sizes
        """
        # Prepare samples for analysis
        all_samples = [self.data]
        for sample in other_samples:
            if isinstance(sample, Sample):
                all_samples.append(sample.data)
            else:
                all_samples.append(np.array(sample))
        f_stat, p_value = stats.f_oneway(*all_samples)
        k = len(all_samples)  # Number of groups
        n = sum(len(sample) for sample in all_samples)  # Total observations
        df_between = k - 1
        df_within = n - k

        all_data = np.concatenate(all_samples)
        grand_mean = np.mean(all_data)
        group_means = [np.mean(sample) for sample in all_samples]

        effects = [mean - grand_mean for mean in group_means]

        ss_between = sum(len(sample) * (np.mean(sample) - grand_mean)**2 for sample in all_samples)
        ss_total = sum((all_data - grand_mean)**2)
        ss_within = ss_total - ss_between
    
        return {
            'test': "One-way ANOVA",
            'f_statistic': f_stat,
            'p_value': p_value,
            'df_between': df_between,
            'df_within': df_within,
            'reject_null': p_value < 0.05,
            'conclusion': f"{'Reject' if p_value < 0.05 else 'Fail to reject'} the null hypothesis at α = 0.05.",
            'grand_mean': grand_mean,
            'group_means': group_means,
            'effects': effects,
            'group_sizes': [len(sample) for sample in all_samples],
            'ss_between': ss_between,
            'ss_within': ss_within,
            'ss_total': ss_total
        }
    
    #-----------------------------------------------------------------
    # Correlation and Regression
    #-----------------------------------------------------------------
    
    def correlation(self, other_sample):
        """Calculate the Pearson correlation coefficient between two samples
        
        Parameters:
        other_sample : Sample or array-like
            The other sample to calculate correlation with
        """
        if isinstance(other_sample, Sample):
            other_data = other_sample.data
        else:
            other_data = np.array(other_sample)
            
        # Ensure samples have the same length
        if len(self.data) != len(other_data):
            raise ValueError("Samples must have the same length")
            
        r, p_value = stats.pearsonr(self.data, other_data)
        return {
            'r': r,
            'r_squared': r**2,
            'p_value': p_value
        }
    
    def covariance(self, other_sample):
        """Calculate the covariance between two samples
        
        Parameters:
        other_sample : Sample or array-like
            The other sample to calculate covariance with
        """
        if isinstance(other_sample, Sample):
            other_data = other_sample.data
        else:
            other_data = np.array(other_sample)
            
        # Ensure samples have the same length
        if len(self.data) != len(other_data):
            raise ValueError("Samples must have the same length")
            
        return np.cov(self.data, other_data, ddof=1)[0, 1]
    
    def correlation_matrix(self, *other_samples, labels=None):
        """Calculate correlation matrix for multiple samples
        
        Parameters:
        *other_samples : Sample objects or array-like
            Other samples to include in the correlation
        labels : list of str, optional
            Labels for each sample
            
        Returns:
        pandas DataFrame with correlation matrix
        """
        # Prepare data
        samples = [self.data]
        
        for sample in other_samples:
            if isinstance(sample, Sample):
                samples.append(sample.data)
            else:
                samples.append(np.array(sample))
                
        # Ensure all samples have the same length
        lengths = [len(s) for s in samples]
        if len(set(lengths)) > 1:
            raise ValueError("All samples must have the same length")
            
        # Create DataFrame
        if labels is None:
            labels = [f'Sample_{i}' for i in range(len(samples))]
            
        df = pd.DataFrame({labels[i]: samples[i] for i in range(len(samples))})
        
        return df.corr()
    
    def linear_regression(self, y_sample, alpha=0.05):
        """Perform simple linear regression analysis
        
        Parameters:
        y_sample : Sample or array-like
            The dependent variable (y)
        alpha : float, optional
            Significance level for confidence intervals. Default is 0.05.
            
        Returns:
        dict with regression results
        """
        # Get y data
        if isinstance(y_sample, Sample):
            y = y_sample.data
        else:
            y = np.array(y_sample)
            
        # Check lengths
        if len(self.data) != len(y):
            raise ValueError("Both samples must have the same length")
            
        # Create DataFrame for statsmodels
        data = pd.DataFrame({'x': self.data, 'y': y})
        
        # Fit the model
        model = smf.ols(formula='y ~ x', data=data).fit()
        
        # Get summary statistics
        slope = model.params['x']
        intercept = model.params['Intercept']
        r_squared = model.rsquared
        p_values = model.pvalues
        error_std = np.sqrt(model.mse_resid)
        
        return {
            'model': model,
            'summary': model.summary(),
            'equation': f"y = {intercept:.4f} + {slope:.4f}x",
            'intercept': intercept,
            'slope': slope,
            'r_squared': r_squared,
            'p_values': p_values,
            'error_std': error_std
        }
    
    def linear_prediction(self, y_sample, x_value, alpha=0.05):
        """Make prediction at x_value based on linear regression
        
        Parameters:
        y_sample : Sample or array-like
            The dependent variable (y)
        x_value : float
            The value to predict at
        alpha : float, optional
            Significance level for prediction intervals. Default is 0.05.
            
        Returns:
        dict with prediction results
        """
        # Get y data
        if isinstance(y_sample, Sample):
            y = y_sample.data
        else:
            y = np.array(y_sample)
            
        # Check lengths
        if len(self.data) != len(y):
            raise ValueError("Both samples must have the same length")
            
        # Create DataFrame for statsmodels
        data = pd.DataFrame({'x': self.data, 'y': y})
        
        # Fit the model
        model = smf.ols(formula='y ~ x', data=data).fit()
        
        # Create new data for prediction
        new_data = pd.DataFrame({'x': [x_value]})
        
        # Get prediction with intervals
        pred = model.get_prediction(new_data).summary_frame(alpha=alpha)
        
        return {
            'predicted_value': pred['mean'].values[0],
            'standard_error': pred['mean_se'].values[0],
            'confidence_interval': (pred['mean_ci_lower'].values[0], pred['mean_ci_upper'].values[0]),
            'prediction_interval': (pred['obs_ci_lower'].values[0], pred['obs_ci_upper'].values[0])
        }
    
    def multiple_regression(self, y_sample, *other_x_samples, alpha=0.05):
        """Perform multiple linear regression analysis
        
        Parameters:
        y_sample : Sample or array-like
            The dependent variable (y)
        *other_x_samples : Sample objects or array-like
            Other independent variables (x2, x3, etc.)
        alpha : float, optional
            Significance level for confidence intervals. Default is 0.05.
            
        Returns:
        dict with regression results
        """
        # Get y data
        if isinstance(y_sample, Sample):
            y = y_sample.data
        else:
            y = np.array(y_sample)
            
        # Get x data for all predictors
        x_data = {'x0': self.data}
        
        for i, sample in enumerate(other_x_samples, 1):
            if isinstance(sample, Sample):
                x_data[f'x{i}'] = sample.data
            else:
                x_data[f'x{i}'] = np.array(sample)
                
        # Check that all samples have the same length
        lengths = [len(x) for x in x_data.values()]
        if len(set(lengths)) > 1 or len(y) != lengths[0]:
            raise ValueError("All samples must have the same length")
            
        # Create DataFrame
        data = pd.DataFrame(x_data)
        data['y'] = y
        
        # Create formula for regression
        formula = 'y ~ ' + ' + '.join(x_data.keys())
        
        # Fit the model
        model = smf.ols(formula=formula, data=data).fit()
        
        # Get equation string
        equation = f"y = {model.params['Intercept']:.4f}"
        for var in x_data.keys():
            equation += f" + {model.params[var]:.4f} {var}"
        
        return {
            'model': model,
            'summary': model.summary(),
            'equation': equation,
            'coefficients': model.params,
            'r_squared': model.rsquared,
            'adjusted_r_squared': model.rsquared_adj,
            'p_values': model.pvalues,
            'error_std': np.sqrt(model.mse_resid)
        }
    
    #-----------------------------------------------------------------
    # Bootstrap Methods
    #-----------------------------------------------------------------
    
    def bootstrap(self, n_samples=1000, statistic=None):
        """Perform bootstrap resampling to estimate the distribution of a statistic
        
        Parameters:
        n_samples : int, optional
            Number of bootstrap samples. Default is 1000.
        statistic : function, optional
            The statistic to compute. Default is mean.
            
        Returns:
        Bootstrap samples of the statistic
        """
        if statistic is None:
            statistic = np.mean
            
        bootstrap_samples = np.random.choice(
            self.data, 
            size=(n_samples, len(self.data)), 
            replace=True
        )
        
        return np.array([statistic(sample) for sample in bootstrap_samples])
    
    def bootstrap_ci(self, confidence=0.95, n_samples=1000, statistic=None):
        """Compute bootstrap confidence interval
        
        Parameters:
        confidence : float, optional
            Confidence level. Default is 0.95 (95% confidence).
        n_samples : int, optional
            Number of bootstrap samples. Default is 1000.
        statistic : function, optional
            The statistic to compute. Default is mean.
            
        Returns:
        Tuple with lower and upper confidence bounds
        """
        alpha = 1 - confidence
        bootstrap_stats = self.bootstrap(n_samples, statistic)
        
        return np.quantile(bootstrap_stats, [alpha/2, 1-alpha/2])
    
    def parametric_bootstrap(self, distribution='normal', n_samples=1000, alpha=0.05):
        """Perform parametric bootstrap for confidence intervals
        
        Parameters:
        distribution : str, optional
            Distribution to use: 'normal', 'lognormal', or 'exponential'. Default is 'normal'.
        n_samples : int, optional
            Number of bootstrap samples. Default is 1000.
        alpha : float, optional
            Significance level. Default is 0.05.
            
        Returns:
        dict with bootstrap confidence intervals for mean, median, and std
        """
        # Set up distribution parameters
        if distribution == 'normal':
            dist_func = np.random.normal
            args = [self.mean(), self.std()]
        elif distribution == 'lognormal':
            dist_func = np.random.lognormal
            log_data = np.log(self.data)
            args = [np.mean(log_data), np.std(log_data, ddof=1)]
        elif distribution == 'exponential':
            dist_func = np.random.exponential
            args = [self.mean()]
        else:
            raise ValueError("Invalid distribution. Choose 'normal', 'lognormal', or 'exponential'.")
        
        # Generate bootstrap samples
        X = dist_func(*args, size=(n_samples, len(self.data)))
        
        # Calculate statistics
        Xmean = np.mean(X, axis=1)
        Xmedian = np.median(X, axis=1)
        Xstd = np.std(X, axis=1, ddof=1)
        
        # Calculate confidence intervals
        ci_mean = np.percentile(Xmean, [alpha/2*100, (1-alpha/2)*100])
        ci_median = np.percentile(Xmedian, [alpha/2*100, (1-alpha/2)*100])
        ci_std = np.percentile(Xstd, [alpha/2*100, (1-alpha/2)*100])
        
        return {
            'distribution': distribution,
            'ci_mean': ci_mean,
            'ci_median': ci_median,
            'ci_std': ci_std
        }
    
    def nonparametric_bootstrap(self, n_samples=1000, alpha=0.05):
        """Perform non-parametric bootstrap for confidence intervals
        
        Parameters:
        n_samples : int, optional
            Number of bootstrap samples. Default is 1000.
        alpha : float, optional
            Significance level. Default is 0.05.
            
        Returns:
        dict with bootstrap confidence intervals for mean, median, and std
        """
        # Generate bootstrap samples
        X = np.random.choice(self.data, (n_samples, len(self.data)), replace=True)
        
        # Calculate statistics
        Xmean = np.mean(X, axis=1)
        Xmedian = np.median(X, axis=1)
        Xstd = np.std(X, axis=1, ddof=1)
        
        # Calculate confidence intervals
        ci_mean = np.percentile(Xmean, [alpha/2*100, (1-alpha/2)*100])
        ci_median = np.percentile(Xmedian, [alpha/2*100, (1-alpha/2)*100])
        ci_std = np.percentile(Xstd, [alpha/2*100, (1-alpha/2)*100])
        
        return {
            'ci_mean': ci_mean,
            'ci_median': ci_median,
            'ci_std': ci_std
        }
    
    #-----------------------------------------------------------------
    # Power Analysis
    #-----------------------------------------------------------------
    
    def power_analysis(self, effect_size=None, alpha=0.05, power=0.8):
        """Calculate sample size based on power analysis for one-sample t-test
        
        Parameters:
        effect_size : float, optional
            Cohen's d effect size. If None, calculated from data.
        alpha : float, optional
            Significance level. Default is 0.05.
        power : float, optional
            Desired power. Default is 0.8.
            
        Returns:
        Required sample size
        """
        if effect_size is None:
            effect_size = abs(self.mean()) / self.std()
            
        return smp.TTestPower().solve_power(
            effect_size=effect_size,
            alpha=alpha,
            power=power
        )
    
    def calculate_power(self, n=None, effect_size=None, alpha=0.05, ratio=1.0):
        """Calculate statistical power for a two-sample t-test
        
        Parameters:
        n : int, optional
            Sample size for group 1. If None, uses length of current sample.
        effect_size : float, optional
            Cohen's d effect size. If None, uses 0.5 (medium effect).
        alpha : float, optional
            Significance level. Default is 0.05.
        ratio : float, optional
            Ratio of group 2 size to group 1 size. Default is 1.0.
            
        Returns:
        Calculated power
        """
        if n is None:
            n = len(self.data)
            
        if effect_size is None:
            effect_size = 0.5  # Medium effect size
        
        return smp.TTestIndPower().solve_power(
            effect_size=effect_size,
            nobs1=n,
            alpha=alpha,
            ratio=ratio
        )
    
    def calculate_sample_size(self, effect_size=None, alpha=0.05, power=0.8, ratio=1.0):
        """Calculate required sample size for a two-sample t-test
        
        Parameters:
        effect_size : float, optional
            Cohen's d effect size. If None, uses 0.5 (medium effect).
        alpha : float, optional
            Significance level. Default is 0.05.
        power : float, optional
            Desired power. Default is 0.8.
        ratio : float, optional
            Ratio of group 2 size to group 1 size. Default is 1.0.
            
        Returns:
        Tuple with required sample sizes for both groups
        """
        if effect_size is None:
            effect_size = 0.5  # Medium effect size
            
        n1 = smp.TTestIndPower().solve_power(
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            ratio=ratio
        )
        
        n2 = n1 * ratio
        
        return (n1, n2)
    
    def calculate_detectable_effect(self, n=None, alpha=0.05, power=0.8, ratio=1.0):
        """Calculate the minimum detectable effect size for a two-sample t-test
        
        Parameters:
        n : int, optional
            Sample size for group 1. If None, uses length of current sample.
        alpha : float, optional
            Significance level. Default is 0.05.
        power : float, optional
            Desired power. Default is 0.8.
        ratio : float, optional
            Ratio of group 2 size to group 1 size. Default is 1.0.
            
        Returns:
        Minimum detectable effect size (Cohen's d)
        """
        if n is None:
            n = len(self.data)
            
        return smp.TTestIndPower().solve_power(
            nobs1=n,
            alpha=alpha,
            power=power,
            ratio=ratio
        )
    
    #-----------------------------------------------------------------
    # Transformations and Data Handling
    #-----------------------------------------------------------------
    
    def z_scores(self):
        """Return the z-scores of the sample"""
        return (self.data - self.mean()) / self.std()
    
    def is_outlier(self, threshold=1.5):
        """Identify outliers using the IQR method
        
        Parameters:
        threshold : float, optional
            The multiplier for the IQR. Default is 1.5.
        
        Returns:
        Boolean array indicating whether each point is an outlier
        """
        q1, q3 = np.quantile(self.data, [0.25, 0.75])
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        
        return (self.data < lower_bound) | (self.data > upper_bound)
    
    def remove_outliers(self, threshold=1.5):
        """Return a new Sample with outliers removed
        
        Parameters:
        threshold : float, optional
            The multiplier for the IQR. Default is 1.5.
        """
        outliers = self.is_outlier(threshold)
        return Sample(self.data[~outliers])
    
    def normality_test(self, test='shapiro', alpha=0.05):
        """Test if the sample follows a normal distribution
        
        Parameters:
        test : str, optional
            Test to use: 'shapiro' (default) or 'ks' (Kolmogorov-Smirnov)
        alpha : float, optional
            Significance level. Default is 0.05.
            
        Returns:
        dict with test results
        """
        if test == 'shapiro':
            # Shapiro-Wilk test (better for smaller samples)
            statistic, p_value = stats.shapiro(self.data)
            test_name = 'Shapiro-Wilk'
        elif test == 'ks':
            # Kolmogorov-Smirnov test
            statistic, p_value = stats.kstest(self.data, 'norm', args=(self.mean(), self.std()))
            test_name = 'Kolmogorov-Smirnov'
        else:
            raise ValueError("Invalid test. Choose 'shapiro' or 'ks'.")
        
        return {
            'test': test_name,
            'statistic': statistic,
            'p_value': p_value,
            'is_normal': p_value > alpha,
            'conclusion': f"{'Data appears normal' if p_value > alpha else 'Data does not appear normal'} at α = {alpha}."
        }
    
    #-----------------------------------------------------------------
    # Visualization Methods
    #-----------------------------------------------------------------
    
    def describe(self, print_table=True, round_to=4, return_value=True):
        """Return descriptive statistics

        Parameters:
        print_table : bool, optional
            Whether to print a formatted table of statistics. Default is True.
        round_to : int, optional
            Number of decimal places to round to. Default is 4.

        Returns:
        Dictionary of statistics
        """
        stats_dict = {
            'n': len(self.data),
            'mean': self.mean(),
            'median': self.median(),
            'mode': self.mode(),
            'std': self.std(),
            'var': self.var(),
            'sem': self.sem(),
            'skewness': self.skewness(),
            'kurtosis': self.kurtosis(),
            'min': self.min(),
            'max': self.max(),
            'range': self.range(),
            'q1': self.quantile(0.25),
            'q3': self.quantile(0.75),
            'iqr': self.iqr(),
        }

        if print_table:
            # Check if running in IPython/Jupyter environment
            in_notebook = False
            try:
                from IPython import get_ipython
                if get_ipython() is not None:
                    # More robust check for notebook/qtconsole vs terminal ipython
                    if 'zmqshell' in str(type(get_ipython())).lower():
                        in_notebook = True
            except (ImportError, NameError):
                pass
            
            if in_notebook:
                try:
                    from IPython.display import display, HTML

                    ct_data = {
                        'Value': [
                            stats_dict['n'], # Keep n as int initially
                            stats_dict['mean'],
                            stats_dict['median'],
                            stats_dict['mode']
                        ]
                    }
                    central_tendency = pd.DataFrame(ct_data, index=['n', 'Mean', 'Median', 'Mode'])

                    disp_data = {
                         'Value': [
                            stats_dict['std'],
                            stats_dict['var'],
                            stats_dict['sem'],
                            stats_dict['min'],
                            stats_dict['max'],
                            stats_dict['range']
                        ]
                    }
                    dispersion = pd.DataFrame(disp_data, index=['Std Dev', 'Variance', 'SEM', 'Min', 'Max', 'Range'])

                    q_data = {
                         'Value': [
                            stats_dict['q1'],
                            stats_dict['median'], # Repeated for clarity in this table
                            stats_dict['q3'],
                            stats_dict['iqr']
                        ]
                    }
                    quartiles = pd.DataFrame(q_data, index=['Q1 (25%)', 'Median (50%)', 'Q3 (75%)', 'IQR'])

                    shape_data = {
                         'Value': [
                            stats_dict['skewness'],
                            stats_dict['kurtosis']
                        ]
                    }
                    shape = pd.DataFrame(shape_data, index=['Skewness', 'Kurtosis'])

                    # --- Format and Generate HTML for each DataFrame ---
                    # Define common style and formatting
                    float_formatter = f"{{:.{round_to}f}}".format
                    styles = [
                        {'selector': 'th', 'props': [('text-align', 'left')]},
                        {'selector': 'td', 'props': [('text-align', 'right')]}
                    ]

                    # Format 'n' as int, others as float
                    format_dict = {'Value': lambda x: f"{int(x)}" if isinstance(x, (int, np.integer)) and not pd.isna(x) else (float_formatter(x) if pd.notna(x) else 'NaN')}

                    html_central = central_tendency.style \
                        .set_caption("Central Tendency") \
                        .format(format_dict) \
                        .set_table_styles(styles) \
                        .to_html()

                    html_dispersion = dispersion.style \
                        .set_caption("Dispersion") \
                        .format(float_formatter) \
                        .set_table_styles(styles) \
                        .to_html()

                    html_quartiles = quartiles.style \
                        .set_caption("Quartiles") \
                        .format(float_formatter) \
                        .set_table_styles(styles) \
                        .to_html()

                    html_shape = shape.style \
                        .set_caption("Distribution Shape") \
                        .format(float_formatter) \
                        .set_table_styles(styles) \
                        .to_html()

                    # --- Combine HTML into a Flexbox container ---
                    combined_html = f"""
                    <h3>Descriptive Statistics</h3>
                    <div style="display: flex; flex-direction: row; flex-wrap: wrap; justify-content: flex-start; gap: 30px;">
                        <div style="flex: 0 1 auto;">{html_central}</div>
                        <div style="flex: 0 1 auto;">{html_dispersion}</div>
                        <div style="flex: 0 1 auto;">{html_quartiles}</div>
                        <div style="flex: 0 1 auto;">{html_shape}</div>
                    </div>
                    """

                    # --- Display the combined HTML ---
                    display(HTML(combined_html))

                    # --- Display Interpretation Guidelines ---
                    ci_95 = self.ci(0.95)
                    ci_text = f"({float_formatter(ci_95[0])}, {float_formatter(ci_95[1])})" if pd.notna(ci_95[0]) else "N/A"

                    display(HTML(f"""
                    <div style="margin-top: 20px;">
                        <h4>Interpretation Guidelines:</h4>
                        <ul>
                            <li>Skewness: 0 ≈ symmetric, >0 = right-skewed, <0 = left-skewed</li>
                            <li>Kurtosis (Excess): 0 ≈ normal tails, >0 = heavy-tailed (leptokurtic), <0 = light-tailed (platykurtic)</li>
                            <li>95% CI for Mean: {ci_text}</li>
                        </ul>
                    </div>
                    """))

                except Exception as e:
                    # Fall back to text table if there's any error
                    print(f"Error generating HTML table: {e}. Falling back to text table.")
                    self._print_text_table(stats_dict, round_to)
            else:
                # Use text table for non-notebook environments
                self._print_text_table(stats_dict, round_to)
        if return_value:
            return stats_dict
    
    def _print_text_table(self, stats_dict, round_to):
        """Helper method to print text-based table format"""
        print("\n=== Descriptive Statistics ===")
        print(f"{'Statistic':<15} {'Value':<15}")
        print("-" * 30)

        print(f"{'n':<15} {stats_dict['n']:<15}")

        print("\n--- Central Tendency ---")
        print(f"{'Mean':<15} {stats_dict['mean']:.{round_to}f}")
        print(f"{'Median':<15} {stats_dict['median']:.{round_to}f}")
        print(f"{'Mode':<15} {stats_dict['mode']:.{round_to}f}")

        print("\n--- Dispersion ---")
        print(f"{'Std Dev':<15} {stats_dict['std']:.{round_to}f}")
        print(f"{'Variance':<15} {stats_dict['var']:.{round_to}f}")
        print(f"{'SEM':<15} {stats_dict['sem']:.{round_to}f}")
        print(f"{'Min':<15} {stats_dict['min']:.{round_to}f}")
        print(f"{'Max':<15} {stats_dict['max']:.{round_to}f}")
        print(f"{'Range':<15} {stats_dict['range']:.{round_to}f}")

        print("\n--- Quartiles ---")
        print(f"{'Q1 (25%)':<15} {stats_dict['q1']:.{round_to}f}")
        print(f"{'Median (50%)':<15} {stats_dict['median']:.{round_to}f}")
        print(f"{'Q3 (75%)':<15} {stats_dict['q3']:.{round_to}f}")
        print(f"{'IQR':<15} {stats_dict['iqr']:.{round_to}f}")

        print("\n--- Distribution Shape ---")
        print(f"{'Skewness':<15} {stats_dict['skewness']:.{round_to}f}")
        print(f"{'Kurtosis':<15} {stats_dict['kurtosis']:.{round_to}f}")

        print("\nInterpretation Guidelines:")
        print("- Skewness: 0 = symmetric, >0 = right-skewed, <0 = left-skewed")
        print("- Kurtosis: 0 = normal, >0 = heavy-tailed, <0 = light-tailed")
        ci_95 = self.ci(0.95)
        print(f"- 95% CI for Mean: ({ci_95[0]:.{round_to}f}, {ci_95[1]:.{round_to}f})")
    
    def histogram(self, bins=10, **kwargs):
        """Plot a histogram of the sample
        
        Parameters:
        bins : int, optional
            Number of bins. Default is 10.
        **kwargs : 
            Additional keyword arguments to pass to plt.hist()
        """
        plt.figure(figsize=kwargs.pop('figsize', (8, 6)))
        plt.hist(self.data, bins=bins, **kwargs)
        plt.axvline(self.mean(), color='red', linestyle='dashed', linewidth=1, label='Mean')
        plt.axvline(self.median(), color='green', linestyle='dashed', linewidth=1, label='Median')
        plt.title(kwargs.pop('title', 'Histogram'))
        plt.xlabel(kwargs.pop('xlabel', 'Value'))
        plt.ylabel(kwargs.pop('ylabel', 'Frequency'))
        plt.legend()
        return plt
    
    def boxplot(self, **kwargs):
        """Create a box plot of the sample"""
        plt.figure(figsize=kwargs.pop('figsize', (8, 6)))
        plt.boxplot(self.data, **kwargs)
        plt.title(kwargs.pop('title', 'Box Plot'))
        plt.ylabel(kwargs.pop('ylabel', 'Value'))
        return plt
    
    def qq_plot(self):
        """Create a Q-Q plot to check normality"""
        fig = sm.qqplot(self.data, line='s')
        plt.title('Q-Q Plot')
        return plt
    
    def wally_plot(self):
        """
        Create a Wally plot to detect non-normality
        
        A Wally plot displays multiple QQ plots with one of them 
        being the actual data (highlighted in red) and the rest 
        being random normal samples.
        """
        # Random position for the actual data
        W = np.random.randint(0, 3, size=2)
        
        # Create 9 plots with QQ-plots
        n = len(self.data)
        fig, axs = plt.subplots(3, 3, figsize=(10, 10))
        
        # Create normal QQ plots for random data
        for ax in axs.flat:
            sm.qqplot(stats.norm.rvs(size=n), line="q", ax=ax)
        
        # Replace one with the actual data (standardized)
        axs[W[0], W[1]].clear()
        sm.qqplot(
            (self.data - self.mean()) / self.std(), 
            line="q", 
            ax=axs[W[0], W[1]]
        )
        
        # Highlight the actual data plot
        for spine in axs[W[0], W[1]].spines.values():
            spine.set_color("red")
        
        plt.tight_layout()
        plt.suptitle("Wally Plot: Find the real data (hint: red border)", y=1.02)
        
        return plt
      
    def scatter(self, other_sample, inverted=False, **kwargs):
        """Create a scatter plot with another sample

        Parameters:
        other_sample : Sample or array-like
            The other sample to plot against
        inverted : bool, default False
            If True, self.data is treated as the y variable and other_sample as the x variable
        **kwargs :
            Additional keyword arguments to pass to plt.scatter()
        """
        if isinstance(other_sample, Sample):
            other_data = other_sample.data
        else:
            other_data = np.array(other_sample)

        if len(self.data) != len(other_data):
            raise ValueError("Samples must have the same length")

        plt.figure(figsize=kwargs.pop('figsize', (8, 6)))

        x_data = other_data if inverted else self.data
        y_data = self.data if inverted else other_data

        plt.scatter(x_data, y_data, **kwargs)

        if kwargs.pop('add_line', True):
            slope, intercept, r_value, _, _ = stats.linregress(x_data, y_data)

            x_min, x_max = np.min(x_data), np.max(x_data)
            x_line = np.linspace(x_min, x_max, 100)
            y_line = slope * x_line + intercept

            plt.plot(x_line, y_line, 'r-', label=f'y = {slope:.2f}x + {intercept:.2f} (R² = {r_value**2:.2f})')
            plt.legend()

        plt.title(kwargs.pop('title', 'Scatter Plot'))
        plt.xlabel(kwargs.pop('xlabel', 'X'))
        plt.ylabel(kwargs.pop('ylabel', 'Y'))
        plt.grid(kwargs.pop('grid', True))
        return plt
    
    def regression_plot(self, y_sample, alpha=0.05, **kwargs):
        """
        Create a regression plot with confidence and prediction intervals
        
        Parameters:
        y_sample : Sample or array-like
            The dependent variable (y)
        alpha : float, optional
            Significance level for intervals. Default is 0.05.
        **kwargs :
            Additional keyword arguments for plot customization
        """
        # Get y data
        if isinstance(y_sample, Sample):
            y = y_sample.data
        else:
            y = np.array(y_sample)
            
        # Check lengths
        if len(self.data) != len(y):
            raise ValueError("Both samples must have the same length")
            
        # Create DataFrame for statsmodels
        data = pd.DataFrame({'x': self.data, 'y': y})
        
        # Fit the model
        fit = smf.ols(formula='y ~ x', data=data).fit()
        
        # Create prediction grid
        x_new = pd.DataFrame({'x': np.linspace(min(self.data), max(self.data), 100)})
        
        # Get predictions with confidence and prediction intervals
        prediction = fit.get_prediction(x_new).summary_frame(alpha=alpha)
        
        # Create plot
        plt.figure(figsize=kwargs.pop('figsize', (10, 6)))
        
        # Plot data points
        plt.plot(self.data, y, 'o', label='Observed data')
        
        # Plot fitted line
        plt.plot(
            x_new, 
            prediction['mean'], 
            'r-', 
            label=f"Fitted line (y = {fit.params[1]:.3f}x + {fit.params[0]:.3f}) (R² = {fit.rsquared:.3f})"
        )
        
        # Add confidence interval
        plt.fill_between(
            x_new['x'],
            prediction['mean_ci_lower'],
            prediction['mean_ci_upper'],
            color='red', 
            alpha=0.2, 
            label=f'{(1-alpha)*100}% Confidence interval'
        )
        
        # Add prediction interval
        plt.fill_between(
            x_new['x'],
            prediction['obs_ci_lower'],
            prediction['obs_ci_upper'],
            color='green', 
            alpha=0.2, 
            label=f'{(1-alpha)*100}% Prediction interval'
        )
        
        # Add labels and legend
        plt.xlabel(kwargs.pop('xlabel', 'X'))
        plt.ylabel(kwargs.pop('ylabel', 'Y'))
        plt.title(kwargs.pop('title', f'Linear Regression with {(1-alpha)*100}% Intervals'))
        plt.legend()
        plt.grid(kwargs.pop('grid', True))
        
        return plt
    
    def ecdf(self, **kwargs):
        """Plot the empirical cumulative distribution function (ECDF)"""
        x = np.sort(self.data)
        y = np.arange(1, len(x) + 1) / len(x)
        
        plt.figure(figsize=kwargs.pop('figsize', (8, 6)))
        plt.step(x, y, **kwargs)
        plt.title(kwargs.pop('title', 'Empirical Cumulative Distribution Function'))
        plt.xlabel(kwargs.pop('xlabel', 'Value'))
        plt.ylabel(kwargs.pop('ylabel', 'Cumulative Probability'))
        plt.grid(True)
        return plt
    
    def pairs_plot(self, others, labels=None):
        """Create a pairs plot (scatter plot matrix) with multiple samples
        
        Parameters:
        others : list of Sample objects or array-like
            List of other samples to include in the pairs plot
        labels : list of str, optional
            Labels for each sample
        """
        # Convert to list of arrays
        all_samples = [self.data]
        for sample in others:
            if isinstance(sample, Sample):
                all_samples.append(sample.data)
            else:
                all_samples.append(np.array(sample))
        
        # Ensure all samples have the same length
        sample_lengths = [len(s) for s in all_samples]
        if len(set(sample_lengths)) > 1:
            raise ValueError("All samples must have the same length")
        
        # Create DataFrame for easy plotting
        df = pd.DataFrame()
        if labels is None:
            labels = [f'Sample_{i}' for i in range(len(all_samples))]
        
        for i, sample in enumerate(all_samples):
            df[labels[i]] = sample
        
        pd.plotting.scatter_matrix(df, diagonal='kde')
        plt.tight_layout()
        return plt
    
    #-----------------------------------------------------------------
    # Utility Methods
    #-----------------------------------------------------------------
    
    def to_distribution(self, dist_type='normal', **kwargs):
        """Convert sample to a distribution by fitting parameters
        Parameters:
        dist_type : str, optional
            Type of distribution to fit ('normal', 'gamma', 'lognormal', etc.). Default is 'normal'.
        **kwargs : 
            Additional parameters to override the fitted parameters.

        Returns:
        Distribution object of the specified type with parameters fitted to the data

        Examples:
        >>> s = sample([1, 2, 3, 4, 5])
        >>> # Create a normal distribution with parameters estimated from sample
        >>> norm_dist = s.to_distribution('normal')
        >>> # Create an exponential distribution with scale parameter from sample
        >>> exp_dist = s.to_distribution('exponential')
        >>> # Create a normal distribution with specified sigma but fitted mu
        >>> custom_norm = s.to_distribution('normal', sigma=2.0)
        """
        # Import the distribution factory function
        from pstatstools.distributions import distribution

        if dist_type.lower() in ['normal', 'gaussian', 'norm']:
            # Fit normal distribution (mu = mean, sigma = std)
            params = {'mu': self.mean(), 'sigma': self.std()}

        elif dist_type.lower() in ['exponential', 'exp']:
            # For exponential, rate parameter is 1/mean
            # SciPy uses scale = 1/rate
            params = {'scale': self.mean(), 'loc': 0}

        elif dist_type.lower() in ['gamma']:
            # Estimate gamma parameters with method of moments
            # alpha (shape) = mean^2 / variance
            # beta (scale) = variance / mean
            mean = self.mean()
            var = self.var()
            alpha = mean**2 / var
            params = {'a': alpha, 'scale': var / mean, 'loc': 0}

        elif dist_type.lower() in ['lognormal', 'lognorm']:
            # For lognormal, work with log-transformed data
            log_data = np.log(self.data)
            mu = np.mean(log_data)
            sigma = np.std(log_data, ddof=1)
            params = {'mu': mu, 'sigma': sigma, 'loc': 0}

        elif dist_type.lower() in ['t', 'student']:
            # For t-distribution, we need to estimate degrees of freedom
            # This is complex, so default to n-1
            params = {'df': len(self.data) - 1, 'mu': self.mean(), 'sigma': self.std()}

        elif dist_type.lower() in ['poisson']:
            # Poisson parameter lambda equals the mean
            params = {'mu': self.mean(), 'loc': 0}

        elif dist_type.lower() in ['binomial', 'binom']:
            # For binomial, need n and p
            # If data is binary (0s and 1s), p is just the mean
            # Otherwise, assume n is max value and p is mean/n
            if set(np.unique(self.data)) <= {0, 1}:
                n = 1
                p = self.mean()
            else:
                n = int(self.max())
                p = self.mean() / n
            params = {'n': n, 'p': p, 'loc': 0}

        elif dist_type.lower() in ['uniform', 'unif']:
            # For uniform, use min and max of the data
            a = self.min()
            b = self.max()
            params = {'a': a, 'b': b}

        elif dist_type.lower() in ['beta']:
            # Rescale data to [0, 1] if not already
            if self.min() < 0 or self.max() > 1:
                print("Warning: Beta distribution expects data in [0, 1]. Rescaling data.")
                scaled_data = (self.data - self.min()) / (self.max() - self.min())
                scaled_sample = Sample(scaled_data)
                mean = scaled_sample.mean()
                var = scaled_sample.var()
            else:
                mean = self.mean()
                var = self.var()

            # Method of moments for beta parameters
            if var > 0 and 0 < mean < 1:
                a = mean * (mean * (1 - mean) / var - 1)
                b = (1 - mean) * (mean * (1 - mean) / var - 1)
                params = {'a': a, 'b': b, 'loc': 0, 'scale': 1}
            else:
                # Fallback if variance is too small or mean is at bounds
                params = {'a': 1, 'b': 1, 'loc': 0, 'scale': 1}

        elif dist_type.lower() in ['weibull']:
            # Weibull parameter estimation is complex
            # A simple approximation based on mean and variance
            mean = self.mean()
            var = self.var()
            # Shape parameter approximation (this is a rough estimate)
            shape_approx = (mean / np.sqrt(var))**1.086
            params = {'c': shape_approx, 'scale': mean / np.exp((1/shape_approx) * np.log(1/shape_approx + 1)), 'loc': 0}

        else:
            # For other distributions, defer to the fit method
            # Create a default distribution of requested type
            dist = distribution(dist_type)
            # Use its fit method to get parameters
            fitted_params = dist.fit(self.data)
            # This requires the distribution to have a fit method
            return distribution(dist_type, *fitted_params)

        # Override fitted parameters with any provided kwargs
        params.update(kwargs)

        # Create the distribution with the fitted/provided parameters
        try:
            dist = distribution(dist_type, **params)
            return dist
        except Exception as e:
            raise ValueError(f"Could not create {dist_type} distribution with parameters {params}: {e}")


    def get_best_distribution(self, dist_types=None, criterion='aic'):
        """Find the best-fitting distribution for the sample data

        Parameters:
        dist_types : list of str, optional
            List of distribution types to try. Default is common distributions.
        criterion : str, optional
            Criterion for selection: 'aic' (default), 'bic', or 'ks' (Kolmogorov-Smirnov).
        
        Returns:
        tuple: (best distribution object, dict with all fitted distributions and their scores)
        """
        from pstatstools.distributions import fit_distribution, compare_distributions
    
        if dist_types is None:
            # Default to common distributions
            if all(self.data >= 0):  # Non-negative data
                dist_types = ['normal', 'gamma', 'lognormal', 'weibull', 'exponential']
                # Add discrete distributions if data appears discrete
                if all(np.equal(np.mod(self.data, 1), 0)):
                    dist_types.extend(['poisson', 'negative_binomial'])
            else:  # Data with negative values
                dist_types = ['normal', 't']
    
        fitted_results = fit_distribution(self.data, dist_types)
    
        if not fitted_results:
            raise ValueError("Could not fit any distributions to the data")
    
        if criterion.lower() == 'aic':
            sorted_results = sorted(fitted_results, key=lambda x: x['aic'])
        elif criterion.lower() == 'bic':
            sorted_results = sorted(fitted_results, key=lambda x: x.get('bic', float('inf')))
        elif criterion.lower() in ['ks', 'kolmogorov']:
            sorted_results = sorted(fitted_results, key=lambda x: x['ks_stat'])
        else:
            raise ValueError(f"Unknown criterion: {criterion}. Use 'aic', 'bic', or 'ks'.")
    
        return sorted_results[0]['distribution'], sorted_results
    
    def summary(self):
        """Print a comprehensive summary of the sample"""
        desc = self.describe(print_table=False)
        ci_95 = self.ci(0.95)
        norm_test = self.normality_test()
        
        print("=== Sample Summary ===")
        print(f"Sample size: {desc['n']}")
        print(f"Mean: {desc['mean']:.4f}")
        print(f"95% Confidence Interval: ({ci_95[0]:.4f}, {ci_95[1]:.4f})")
        print(f"Median: {desc['median']:.4f}")
        print(f"Standard Deviation: {desc['std']:.4f}")
        print(f"Minimum: {desc['min']:.4f}")
        print(f"Maximum: {desc['max']:.4f}")
        print(f"Range: {desc['range']:.4f}")
        print(f"Q1 (25th percentile): {desc['q1']:.4f}")
        print(f"Q3 (75th percentile): {desc['q3']:.4f}")
        print(f"IQR: {desc['iqr']:.4f}")
        print(f"Skewness: {desc['skewness']:.4f}")
        print(f"Kurtosis: {desc['kurtosis']:.4f}")
        
        print(f"\nNormality test ({norm_test['test']}):")
        print(f"  Statistic: {norm_test['statistic']:.4f}")
        print(f"  p-value: {norm_test['p_value']:.4f}")
        print(f"  Interpretation: {norm_test['conclusion']}")
    
    def __len__(self):
        """Return the length of the sample"""
        return len(self.data)
    
    def __getitem__(self, key):
        """Enable indexing and slicing of the sample"""
        return self.data[key]
    
    def __repr__(self):
        """String representation of the sample"""
        return self.data.__repr__()