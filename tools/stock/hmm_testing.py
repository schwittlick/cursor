import os

import numpy as np
import pandas as pd
import requests
from hmmlearn import hmm

os.environ['LOKY_MAX_CPU_COUNT'] = '8'

num_hours = 1500


def calc_1h_pepe():
    df = do_load_price_history("PEPEUSDT", "1h")
    print(f"data points: {len(df)}")
    observed_features = df['Close'].values.reshape(-1, 1)
    num_hidden_states = 20  # Increase the number of hidden states for more granularity
    model = hmm.GaussianHMM(n_components=num_hidden_states, n_iter=50000, verbose=False, tol=1e-6, min_covar=1e-1)
    model.fit(observed_features)
    num_future_hours = 5
    predicted_hidden_states = model.predict(observed_features[-num_future_hours:])
    for hour, state in enumerate(predicted_hidden_states):
        close_str = "{:.10f}".format(float(np.mean(model.means_[state])))
        print(close_str)


def calc_4h_btc():
    df = do_load_price_history("BTCUSDT", "4h")
    print(f"data points: {len(df)}")
    observed_features = df['Close'].values.reshape(-1, 1)
    num_hidden_states = 20  # Increase the number of hidden states for more granularity
    model = hmm.GaussianHMM(n_components=num_hidden_states, n_iter=50000, verbose=False, tol=1e-6, min_covar=1e-1)
    model.fit(observed_features)
    num_future_hours = 5
    predicted_hidden_states = model.predict(observed_features[-num_future_hours:])
    for hour, state in enumerate(predicted_hidden_states):
        close_str = "{:.10f}".format(float(np.mean(model.means_[state])))
        print(close_str)

def calc_big_btc():
    #df = do_load_price_history("BTCUSDT", "4h")
    headers = ["Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time", "QAV", "NAT", "TBBAV", "TBQAV",
               "Ignore"]
    df = pd.read_csv("BTCUSDT.csv", names=headers)

    print(f"data points: {len(df)}")
    observed_features = df['Close'].values.reshape(-1, 1)
    num_hidden_states = 10  # Increase the number of hidden states for more granularity
    model = hmm.GaussianHMM(n_components=num_hidden_states, n_iter=500, verbose=True)
    model.fit(observed_features)
    num_future_hours = 5
    predicted_hidden_states = model.predict(observed_features[-num_future_hours:])
    for hour, state in enumerate(predicted_hidden_states):
        close_str = "{:.10f}".format(float(np.mean(model.means_[state])))
        print(close_str)

def do_load_price_history(symbol, interval):
    url = 'https://www.binance.com/api/v3/klines?symbol=%s&interval=%s&limit=%s' % (symbol, interval, num_hours)
    print('loading binance %s %s' % (symbol, interval))
    d = requests.get(url).json()
    df = pd.DataFrame(d, columns='Time Open High Low Close Volume a b c d e f'.split())
    df = df.astype(
        {'Time': 'datetime64[ms]', 'Open': float, 'High': float, 'Low': float, 'Close': float, 'Volume': float})
    return df.set_index('Time')


if __name__ == '__main__':
    calc_4h_btc()
    calc_1h_pepe()
    calc_big_btc()
