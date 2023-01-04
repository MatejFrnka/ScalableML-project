import json
from datetime import datetime, timedelta

import hopsworks
from keras.layers import Dropout
from sklearn.preprocessing import MaxAbsScaler
from consts import X_COLUMNS, Y_COLUMNS, X_SCALE_COLUMNS
import tensorflow
import pickle
from utils.BackTest import Games, Evaluator
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.models import Sequential
import matplotlib.pyplot as plt
from pathlib import Path
import shutil

from utils.Hopsworks import get_football_featureview

tensorflow.random.set_seed(1)


def plot_history(history, save_path=None):
    print(history.history.keys())
    # "Loss"
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'validation'], loc='upper right')
    if save_path is not None:
        plt.savefig(save_path / "training.png")
    plt.show()


def train_model(df_train, train_size=0.75, metrics_directory=None):
    # drop first 10000 rows of the training data because some calculated metrics are dependent on previous data
    # and are not accurate at the beginning
    df_train = df_train.iloc[10_000:]

    # split data to valid and train
    train_index = int(len(df_train) * train_size)
    df_valid = df_train[train_index:]
    df_train = df_train[0:train_index]

    # split data to X, y
    X_train, y_train = df_train[X_COLUMNS].copy(), df_train[Y_COLUMNS].copy()
    X_valid, y_valid = df_valid[X_COLUMNS].copy(), df_valid[Y_COLUMNS].copy()

    # scale scalable columns
    # todo: try min max scaler
    scaler = MaxAbsScaler()
    scaler.fit(X_train[X_SCALE_COLUMNS])
    X_train[X_SCALE_COLUMNS] = scaler.transform(X_train[X_SCALE_COLUMNS])
    X_valid[X_SCALE_COLUMNS] = scaler.transform(X_valid[X_SCALE_COLUMNS])

    model = Sequential()
    model.add(Dense(len(X_train.columns) + 1, input_dim=len(X_train.columns),
                    kernel_initializer='normal', activation='relu'))
    model.add(Dense(800, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(800, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(800, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(3, activation='linear'))
    model.summary()
    model.compile(loss='mse', optimizer='adam', metrics=['mse', 'mae'])
    history = model.fit(X_train, y_train, epochs=50, batch_size=400, verbose=1, validation_data=(X_valid, y_valid))
    plot_history(history, metrics_directory)
    return scaler, model


def test_performance(feature_view, evaluator, days_back):
    # first, we train model without last year and calculate performance on the last year
    # download data older than a year

    # download data from last year
    df_train = feature_view.get_batch_data(
        start_time=0,
        end_time=datetime.now() - timedelta(days=days_back),
    )

    # download data from last year
    df_test = feature_view.get_batch_data(
        start_time=datetime.now() - timedelta(days=days_back),
        end_time=datetime.now()
    )

    scaler, model = train_model(df_train, 0.75)

    # scaler, model = train_model(df_train, df_valid)
    X_test = df_test[X_COLUMNS].copy()
    X_test[X_SCALE_COLUMNS] = scaler.transform(df_test[X_SCALE_COLUMNS])

    open_percentage = Games(df_test["ho_pinnacle"].array,
                            df_test["do_pinnacle"].array,
                            df_test["ao_pinnacle"].array)

    predictions = model.predict(X_test)
    predicted_odds = Games(*predictions.T)
    buy_sig = evaluator.generate_buy_signals(open_percentage, predicted_odds)
    metrics, money_chart = Evaluator.evaluate_buy_signals(df_test["fthg"].array,
                                                          df_test["ftag"].array,
                                                          open_percentage.get_odds(),
                                                          buy_sig, df_test["date"])

    return metrics, money_chart


# delete directory if exists
dirpath = Path('tmp_output')
if dirpath.exists() and dirpath.is_dir():
    shutil.rmtree(dirpath)
# create empty
dirpath.mkdir()

# You have to set the environment variable 'HOPSWORKS_API_KEY' for login to succeed
project = hopsworks.login()
# fs is a reference to the Hopsworks Feature Store
fs = project.get_feature_store()

# get featureview
feature_view = get_football_featureview(fs)

# no labels are set in the feature view
train, _ = feature_view.training_data()
evaluator = Evaluator(0.05)

# measure performance of last year
metrics, money_chart = test_performance(feature_view, evaluator, 365)
print(metrics)
# train model on all available data
scaler, model = train_model(train, 0.75, dirpath)

# write everything to
with open(dirpath / 'scaler.pickle', 'wb') as handle:
    pickle.dump(scaler, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(dirpath / 'evaluator.pickle', 'wb') as handle:
    pickle.dump(evaluator, handle, protocol=pickle.HIGHEST_PROTOCOL)
model_dir = dirpath / 'model'
model_dir.mkdir()
model.save(model_dir)

with open(dirpath / 'metrics.json', 'w') as file:
    combined = metrics.copy()
    combined["money_chart"] = money_chart
    json.dump(combined, file)

# We will now upload our model to the Hopsworks Model Registry. First get an object for the model registry.
mr = project.get_model_registry()
# Create an entry in the model registry that includes the model's name, desc, metrics
model_football = mr.python.create_model(
    name="model_football",
    description="Football close odds predictions",
    metrics=metrics
)
metrics_football = mr.python.create_model(
    name="metrics_football",
    description="Football close odds predictions metrics",
    metrics=metrics,
)

# Upload the model to the model registry, including all files in 'model_dir'
model_football.save(dirpath)
metrics_football.save(dirpath / 'metrics.json')
