import json
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import yfinance as yf

from scipy import stats
from scipy.optimize import minimize
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller

from pprint import pprint
from tqdm import tqdm

def WhiteNoise(sigma, T):
    e = np.array([0]) + np.random.normal(0, sigma, size=T)
    e[0] = 0
    return e

def WienerP(t):
    W = [0]
    for i in range(1, t):
        W.append(W[i-1] + np.random.normal(0, 1))
    return W

def S(t, S0, mu, sigma):
    return S0 * np.exp((mu - sigma**2/2) * t + sigma * np.array(WienerP(t)))

class CorrelatedBrownianMotion:
    def __init__(self, T, steps, rho):
        self.T = T
        self.steps = steps
        self.dt = T / steps
        self.rho = rho
        self.W1 = [0]
        self.W2 = [0]

    def generate_correlated_brownian_motions(self):
        for i in range(1, self.steps + 1):
            Z1 = np.random.normal(0, np.sqrt(self.dt))
            Z2 = np.random.normal(0, np.sqrt(self.dt))
            W1_incr = Z1
            W2_incr = self.rho * Z1 + np.sqrt(1 - self.rho**2) * Z2
            self.W1.append(self.W1[-1] + W1_incr)
            self.W2.append(self.W2[-1] + W2_incr)

        return self.W1, self.W2

class StockModel:
    def __init__(self, T, steps, S1_0, S2_0, mu1, mu2, sigma1, sigma2, rho):
        self.T = T
        self.steps = steps
        self.S1_0 = S1_0
        self.S2_0 = S2_0
        self.mu1 = mu1
        self.mu2 = mu2
        self.sigma1 = sigma1
        self.sigma2 = sigma2
        self.dt = T / steps
        self.cbm = CorrelatedBrownianMotion(T, steps, rho)
        self.W1, self.W2 = self.cbm.generate_correlated_brownian_motions()

        self.S1_path = []
        self.S2_path = []

    def generate_stock_paths(self):
        S1 = [self.S1_0]
        S2 = [self.S2_0]

        for i in range(1, self.steps + 1):
            S1_t = S1[-1] * np.exp((self.mu1 - 0.5 * self.sigma1**2) * self.dt + self.sigma1 * (self.W1[i] - self.W1[i-1]))
            S2_t = S2[-1] * np.exp((self.mu2 - 0.5 * self.sigma2**2) * self.dt + self.sigma2 * (self.W2[i] - self.W2[i-1]))
            S1.append(S1_t)
            S2.append(S2_t)

        self.S1_path = S1
        self.S2_path = S2

        return S1, S2

    def get_stock_paths(self):
        if not self.S1_path or not self.S2_path:
            self.generate_stock_paths()
        return self.S1_path, self.S2_path

    def plot_stock_paths(self):
        S1, S2 = self.get_stock_paths()
        plt.figure(figsize=(12, 6))
        plt.plot(np.linspace(0, self.T, self.steps + 1), S1, label='Stock 1')
        plt.plot(np.linspace(0, self.T, self.steps + 1), S2, label='Stock 2')
        plt.xlabel('Time')
        plt.ylabel('Stock Price')
        plt.legend()
        plt.title(f'Stock Price Paths with Correlation rho = {self.cbm.rho}')
        plt.show()

def OU_Process(mu, theta, sigma, T, Dt, X0=0):
    if X0 == 0:
        X0 = mu

    N = int(T/Dt)
    R = np.random.normal(0, 1, N)
    t = np.linspace(0, T, N)
    X = [X0]
    W = WienerP(N)

    for i in range(1, N):
        X.append(X[i-1] + theta*(mu-X[i-1])*Dt + sigma*np.sqrt(Dt)*R[i-1])

    return X

def stat_test(x):
    p = adfuller(x, maxlag=1, autolag="AIC")[1]
    if p < 0.05:
        print("Stationary with p value = ", p)
        return True
    else:
        print("Not Stationary with p value = ", p)
        return False

def speed_of_reversion(X):
    m = np.mean(X)
    Dt = 0.05
    times = []
    for t in range(len(X)-1):
        if (X[t] == m) or (X[t-1] < m and X[t+1] > m):
            times.append(t*Dt)

    sr = [times[i+1] - times[i] for i in range(len(times)-1)]
    return [np.mean(sr), np.std(sr)]

def Theta(X, l=True):
    if l == True:
        x = speed_of_reversion(X)[0]
    else:
        x = X

    a = 0.04250897984735255
    b = -0.28072224998134393
    c = 0.6570017336905689

    return np.exp((-np.sqrt(b**2 + 4*a*x - 4*a*c) - b) / (2*a))

def adf_cost_function(betas, time_series, n):
    if len(time_series) != n:
        raise ValueError(f"time_series must have {n} elements.")
    if len(betas) != n - 1:
        raise ValueError(f"betas must have {n-1} elements.")

    u = time_series[0] + sum(betas[i] * time_series[i + 1] for i in range(n - 1))
    adf_result = adfuller(u, maxlag=1, autolag="AIC")

    return adf_result[1]

def Cointegration_Vector(initial_betas, time_series, n):
    result = minimize(adf_cost_function, initial_betas, args=(time_series, n,))
    optimal_betas = result.x

    u = time_series[0] + sum(optimal_betas[i] * time_series[i + 1] for i in range(n - 1))

    print(f"Optimal coefficients: {optimal_betas}")
    stat_test(u)

    return result.fun, optimal_betas, u



def lagged_corr(x, y, lag):
    
    if lag > 0:
        x_adj = x[:-lag]
        y_adj = y[lag:]
    elif lag < 0:
        x_adj = x[-lag:]
        y_adj = y[:lag]
    else:
        x_adj = x
        y_adj = y
    x_adj = np.asarray(x_adj)
    y_adj = np.asarray(y_adj)
    if len(x_adj) == 0 or len(y_adj) == 0:
        return np.nan
    
    return np.corrcoef(x_adj, y_adj)[0, 1]





def find_optimal_lag(x, y, max_lag=50,sparsity=300,min_lag=0,mM = False):

    if mM == True:
        min_lag = -max_lag
    
    lags = np.arange(min_lag, max_lag + 1,sparsity)

    correlations = []
    for lag in lags:
        corr = lagged_corr(x, y, lag)
        correlations.append(corr)
    
    correlations_arr = np.array(correlations)
    if np.all(np.isnan(correlations_arr)):
        optimal_lag = np.nan
        optimal_corr = np.nan
    else:
        safe_corrs = np.nan_to_num(correlations_arr, nan=0.0)
        optimal_index = np.argmax(np.abs(safe_corrs))
        optimal_lag = lags[optimal_index]
        optimal_corr = correlations_arr[optimal_index]
    return {
        'lags': lags,
        'correlations': correlations,
        'optimal_lag': optimal_lag,
        'optimal_corr': optimal_corr
    }


def optimal_lag_with_stability(x, y, max_lag=50, n_subsets=10):
    
    full_result = find_optimal_lag(x, y, max_lag=max_lag)
    
    n = len(x)
    subset_size = n // n_subsets
    subset_optimal_lags = []
    subset_optimal_corrs = []
    
    for i in range(n_subsets):
        start = i * subset_size
        end = n if i == n_subsets - 1 else (i + 1) * subset_size
        x_subset = x[start:end]
        y_subset = y[start:end]
        
        if len(x_subset) < max_lag or len(y_subset) < max_lag:
            continue
        
        subset_result = find_optimal_lag(x_subset, y_subset, max_lag=max_lag)
        subset_optimal_lags.append(subset_result['optimal_lag'])
        subset_optimal_corrs.append(subset_result['optimal_corr'])
    
    lag_stability = np.std(subset_optimal_lags) if subset_optimal_lags else np.nan
    return {
        'full_result': full_result,
        'subset_optimal_lags': subset_optimal_lags,
        'subset_optimal_corrs': subset_optimal_corrs,
        'lag_stability': lag_stability
    }



def plot_correlation_vs_lag(lags, correlations, asset1, asset2, optimal_lag, optimal_corr):
 
    plt.figure(figsize=(10, 5))
    plt.plot(lags, correlations, marker='o')
    plt.xlabel('Time Lag')
    plt.ylabel('Correlation')
    plt.title(f'Lagged Correlation between {asset1} and {asset2}\nOptimal Lag = {optimal_lag}, Corr = {optimal_corr:.3f}')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_time_series_comparison(x, y, optimal_lag, asset1, asset2):


    x_norm = (x - np.mean(x)) / np.std(x)
    y_norm = (y - np.mean(y)) / np.std(y)
    

    if optimal_lag >= 0:
        x_aligned = x_norm[:-optimal_lag] if optimal_lag > 0 else x_norm
        y_aligned = y_norm[optimal_lag:]
    else:
        x_aligned = x_norm[-optimal_lag:]
        y_aligned = y_norm[:len(y_norm)+optimal_lag]
        
    time_idx_full = np.arange(len(x_norm))
    time_idx_aligned = np.arange(len(x_aligned))
    
    plt.figure(figsize=(14, 8))

    plt.plot(time_idx_aligned, x_aligned, label=f'{asset1} (normalized)', alpha=0.8)
    plt.plot(time_idx_aligned, y_aligned, label=f'{asset2} shifted by {optimal_lag}', alpha=0.8)
    plt.xlabel('Time Index (Aligned)')
    plt.title(f'Aligned Time Series: {asset2} shifted by {optimal_lag}')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

def plot_subset_optimal_lags(subset_optimal_lags):
    """
    Plots the optimal lag computed for each subset as a bar plot.
    """
    n_subsets = len(subset_optimal_lags)
    subsets = np.arange(n_subsets)
    plt.figure(figsize=(8, 4))
    plt.bar(subsets, subset_optimal_lags, color='skyblue', edgecolor='black')
    plt.xlabel('Subset Index')
    plt.ylabel('Optimal Lag')
    plt.title('Optimal Lag in Each Subset')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(subsets)
    plt.tight_layout()
    plt.show()


