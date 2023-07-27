import os

import numpy as np
import pandas as pd
import requests
from hmmlearn import hmm

os.environ['LOKY_MAX_CPU_COUNT'] = '6'

num_hours = 1500


def do_load_price_history(symbol, interval):
    url = 'https://www.binance.com/api/v3/klines?symbol=%s&interval=%s&limit=%s' % (symbol, interval, num_hours)
    print('loading binance %s %s' % (symbol, interval))
    d = requests.get(url).json()
    df = pd.DataFrame(d, columns='Time Open High Low Close Volume a b c d e f'.split())
    df = df.astype(
        {'Time': 'datetime64[ms]', 'Open': float, 'High': float, 'Low': float, 'Close': float, 'Volume': float})
    return df.set_index('Time')

df = do_load_price_history("PEPEUSDT", "30m")
print(f"data points: {len(df)}")

for last in df['Close'].tail():
    last_value = float(last)
    last_value_str = "{:.10f}".format(last_value)
    print(last_value_str)
# df = pd.DataFrame(data)

# Select features for HMM training (using the 'house_price')
observed_features = df['Close'].values.reshape(-1, 1)

# Choose the number of hidden states (you can experiment with this number)
num_hidden_states = 20  # Increase the number of hidden states for more granularity

# Initialize and train the Hidden Markov Model
model = hmm.GaussianHMM(n_components=num_hidden_states, n_iter=50000, verbose=True, tol=1e-6, min_covar=1e-1)
model.fit(observed_features)

num_future_hours = 10

predicted_hidden_states = model.predict(observed_features[-num_future_hours:])

# Use the predicted hidden states to estimate future house prices
print("new")
for hour, state in enumerate(predicted_hidden_states):
    v = float(np.mean(model.means_[state]))
    close_str = "{:.10f}".format(v)
    print(close_str)

