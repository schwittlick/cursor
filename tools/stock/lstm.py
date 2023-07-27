import math

import numpy as np
import pandas as pd
from keras import Sequential
from keras.layers import LSTM, Dense
from matplotlib import pyplot as plt

from datetime import datetime as dt

from sklearn.preprocessing import MinMaxScaler


# defining function the that turn the timestamp to the date
def calculate_time(timestamp):
    """
    This function turns the timestamp to the date
    :param timestamp: given timestamp
    :return: date according to given timestamp
    """
    return dt.fromtimestamp(timestamp/1000)

if __name__ == '__main__':
    headers = ["Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time", "QAV", "NAT", "TBBAV", "TBQAV",
               "Ignore"]
    data = pd.read_csv("BTCUSDT.csv", names=headers)
    data.head()

    # Turn "Open Time" and "Close Time" columns to Date
    open_date = []
    for i in data["Open Time"]:
        open_date.append(calculate_time(i))
    data["Open Time"] = open_date

    close_date = []
    for i in data["Close Time"]:
        close_date.append(calculate_time(i))
    data["Close Time"] = close_date

    # Visualize the close price history
    #plt.figure(figsize=(16, 8))
    #plt.title("Bitcoin Price History")
    #plt.plot(data["Close Time"], data["Close"])
    #plt.xlabel("Time", fontsize=14, )
    #plt.ylabel("USDT", fontsize=14)
    #plt.show()

    # Create new data with only the "Close" column
    close = data.filter(["Close"])
    # Convert the dataframe to a np array
    close_array = close.values
    # See the train data len
    train_close_len = math.ceil(len(close_array) * 0.8)

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(close_array)

    train_data = scaled_data[0: train_close_len, :]
    # Create X_train and y_train
    X_train = []
    y_train = []
    for i in range(60, len(train_data)):
        X_train.append(train_data[i - 60: i, 0])
        y_train.append(train_data[i, 0])
        #if i <= 60:
        #    print(X_train)
        #    print(y_train)

    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    test_data = scaled_data[train_close_len - 60:, :]
    # create X_test and y_test
    X_test = []
    y_test = data.iloc[train_close_len:, :]
    for i in range(60, len(test_data)):
        X_test.append(test_data[i - 60: i, 0])

    X_test = np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    model = Sequential()

    model.add(LSTM(units=512, return_sequences=True, activation='relu', input_shape=(X_train.shape[1], 1)))

    model.add(LSTM(units=256, activation='relu', return_sequences=False))

    model.add(Dense(units=1))
    model.compile(optimizer="Adam", loss="mean_squared_error", metrics=['mae'])
    model.fit(X_train, y_train,
              epochs=3,
              batch_size=100,
              verbose=1)
    #model.save("btc_hourly_230725.model")
    predictions = model.predict(X_test)
    # here put the entire history and predict a next step
    # maybe use daily data only and just get next step
    predictions = scaler.inverse_transform(predictions)
    train = close[:train_close_len]
    valid = close[train_close_len:]
    valid["Predictions"] = predictions
    # visualize the data
    plt.figure(figsize=(16, 8))
    plt.title("LSTM Model")
    plt.xlabel("Time", fontsize=14)
    plt.ylabel("USDT", fontsize=14)
    plt.plot(data["Close Time"][:train_close_len], train["Close"])
    plt.plot(data["Close Time"][train_close_len:], valid[["Close", "Predictions"]])
    plt.legend(["Train", "Validation", "Predictions"], loc="lower right")
    plt.show()