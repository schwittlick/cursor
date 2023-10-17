import keras
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.preprocessing import MinMaxScaler

from tools.stock.data_aggr import calculate_time

if __name__ == '__main__':
    model = keras.models.load_model("btc_hourly_230725.model")

    headers = ["Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time", "QAV", "NAT", "TBBAV", "TBQAV",
               "Ignore"]
    data = pd.read_csv("BTCUSDT_newest.csv", names=headers)
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
    # plt.figure(figsize=(16, 8))
    # plt.title("Bitcoin Price History")
    # plt.plot(data["Close Time"], data["Close"])
    # plt.xlabel("Time", fontsize=14, )
    # plt.ylabel("USDT", fontsize=14)
    # plt.show()

    # Create new data with only the "Close" column
    close = data.filter(["Close"])
    # Convert the dataframe to a np array
    close_array = close.values
    # See the train data len

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(close_array)

    window = 60

    test_data = scaled_data[:, :]
    # create X_test and y_test
    X_test = []
    y_test = data.iloc[:, :]
    for i in range(window, len(test_data)):
        X_test.append(test_data[i - window:i, 0])

    X_test = np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    # get the most recent 60 btc values and put it in a array
    predictions = model.predict(X_test)

    predictions = scaler.inverse_transform(predictions)
    valid = close[window:]
    valid["Predictions"] = predictions
    # visualize the data
    plt.figure(figsize=(16, 8))
    plt.title("LSTM Model")
    plt.xlabel("Time", fontsize=14)
    plt.ylabel("USDT", fontsize=14)
    plt.plot(data["Close Time"][window:], valid[["Close", "Predictions"]])
    plt.legend(["Validation", "Predictions"], loc="lower right")
    plt.show()
