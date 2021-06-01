# -*- coding: utf-8 -*-
"""Drugi deo zadatka.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AH6zcYk_soc6vfVdTfaLgM-PP-PvxZEU
"""

from google.colab import drive
drive.mount('/content/drive')

!pip install cryptocmd

from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Embedding
from keras.layers import SimpleRNN, LSTM, GRU
from keras.datasets import imdb
import numpy as np
import math
from matplotlib import pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from cryptocmd import CmcScraper
from tensorflow.keras.preprocessing.text import Tokenizer

# Pomocna funkcija za ciscenje podataka
def remove_null(val):
    if val != 'null':
        return val
    pass

# Uz pomoc biblioteke cryptocmd skidamo podatke za kriptovalute iz liste coins
coins = ['BTC', 'ETH', 'USDT', 'ADA', 'BNB', 'XRP', 'DOGE', 'USDC', 'BCH', 'LINK', 'LTC', 'MATIC', 'XLM', 'VET', 'THETA', 'EOS', 'TRX', 'FIL', 'DAI', 'XMR', 'NEO']
dict_coins = {} # Dictionary koji sadrzi sve podatke o odredjenoj valuti iz close kolone
dict_coins_scaled = {} # dict_coins skaliran izmedju 0 i 1
dict_coins_train = {} # Dictionary koji sadrzi podatke za training o odredjenoj valuti iz close kolone
y_train_map = {} # Targeti za trainig
dict_coins_test = {} # Dictionary koji sadrzi podatke za test o odredjenoj valuti iz close kolone
x_train_map = {} # np array spreman za prosledjivanje u neuralnu mrezu
x_test_map = {} # np array za testiranje

embedding_size = 4 # broj outputa koji embedding vraca

# Spremanje liste coins za embedding
tokenizer = Tokenizer()
tokenizer.fit_on_texts(coins)
vocab_size = len(coins)

# Inicijalizujemo embedding model 
model_enb = Sequential()
model_enb.add(Embedding(vocab_size, embedding_size, input_length=1))
model_enb.compile(optimizer='adam', loss='binary_crossentropy')

# Pretvaranje stringa u listu brojeva za embedding
input_array = tokenizer.texts_to_sequences(coins)

for i, coin in enumerate(coins):
  if i == 20:
    continue
  # Skidanje podataka
  scraper = CmcScraper(coin, "01-01-2018", "01-01-2021")
  scraper.export("csv", name=coin)
  dict_coins[coin] = np.loadtxt(f'/content/{coin}.csv', usecols=(4), skiprows=1, delimiter=',', dtype=np.str)

  # Ciscenje (null vrednosti) i konverzija u float za train set
  dict_coins[coin] = list(map(remove_null, dict_coins[coin]))
  dict_coins[coin] = np.array(dict_coins[coin])
  dict_coins[coin] = dict_coins[coin].astype(np.float)
  dict_coins[coin] = dict_coins[coin][np.logical_not(np.isnan(dict_coins[coin]))]
  dict_coins[coin] = np.reshape(dict_coins[coin], (dict_coins[coin].shape[0], 1))

  # Skaliranje podataka izmedju 0 i 1
  scaler = MinMaxScaler(feature_range=(0,1))
  dict_coins_scaled[coin] = scaler.fit_transform(dict_coins[coin])

  # print(dict_coins_scaled[coin].shape, coin)

  percent = 0.85
  nb_of_train = np.round(percent * dict_coins_scaled[coin].shape[0])
  
  # Delimo podatke na trening i test skup
  for j in range(dict_coins_scaled[coin].shape[0]):
    if j == 0:
      dict_coins_train[coin] = []
      dict_coins_test[coin] = []
    if j <= nb_of_train:
      dict_coins_train[coin].append(dict_coins_scaled[coin][j])
    else:
      dict_coins_test[coin].append(dict_coins_scaled[coin][j])

  
#   output_array = model_enb.predict(input_array[i])

  # Postavljamo u trening skupu np array za 30 dana unazad
  x_train_map[coin] = []
  y_train_map[coin] = []
  for j in range(30, len(dict_coins_scaled[coin]) - len(dict_coins_test[coin])):
    x_train_map[coin].append(dict_coins_scaled[coin][j-30:j, 0])
    y_train_map[coin].append(dict_coins_scaled[coin][j, 0])
  
  
  output_array = model_enb.predict(input_array[i])
  print(output_array)
#   for j in range(len(x_train_map[coin])):
#     for k in range(len(x_train_map[coin][j])):
#       x_train_map[coin][j][k].append(output_array[0][0])
    
  

  # Pretvaramo values iz list u nparray
  x_train_map[coin] = np.array(x_train_map[coin])
  y_train_map[coin] = np.array(y_train_map[coin])
  x_train_map[coin] = np.reshape(x_train_map[coin], (x_train_map[coin].shape[0], x_train_map[coin].shape[1], 1))
  y_train_map[coin] = np.reshape(y_train_map[coin], (y_train_map[coin].shape[0], 1))


  
#   x_train_map[coin] = np.concatenate((x_train_map[coin], output_array))

  # Pretvaramo values iz list u nparray
  dict_coins_scaled[coin] = np.array(dict_coins_scaled[coin])
  dict_coins_test[coin] = np.array(dict_coins_test[coin])

  # Postavljamo u test skupu np array za 30 dana unazad
  x_test_map[coin] = []
  for i in range(dict_coins_scaled[coin].shape[0] - dict_coins_test[coin].shape[0], dict_coins_scaled[coin].shape[0]):
    x_test_map[coin].append(dict_coins_scaled[coin][i-30:i,0])
  x_test_map[coin] = np.array(x_test_map[coin])

  for i in range(dict_coins_scaled[coin].shape[0]):
    dict_coins_train[coin] = np.array(dict_coins_train[coin])
    dict_coins_train[coin] = np.reshape(dict_coins_train[coin], (dict_coins_train[coin].shape[0], dict_coins_train[coin].shape[1], 1))
    dict_coins_test[coin] = np.array(dict_coins_test[coin])
    dict_coins_test[coin] = np.reshape(dict_coins_test[coin], (dict_coins_test[coin].shape[0], dict_coins_test[coin].shape[1], 1))

  # Dodavanje embedding outputova u x_train_map
  empty = np.zeros((x_train_map['BTC'].shape[0], x_train_map['BTC'].shape[1], 1 + embedding_size))

  for i in range(x_train_map['BTC'].shape[0]):
    for j in range(x_train_map['BTC'].shape[1]):
      for k in range(embedding_size):
        empty[i][j][k] = output_array[0][0][k]

  for i in range(x_train_map['BTC'].shape[0]):
    for j in range(x_train_map['BTC'].shape[1]):
      empty[i][j][4] = x_train_map['BTC'][i][j][0]

  x_train_map[coin] = empty

# print(x_train_map.shape)

print()

#   x_train_map['BTC'] = np.reshape(x_train_map, (x_train_map['BTC'].shape[0], x_train_map['BTC'].shape[1], 5))
#   x_train_map['BTC'][2] = np.concatenate((x_train_map['BTC'][2], output_array[2]))
#   print(x_train_map[coin].shape[2])
# x_train_map['BTC'] = np.reshape(x_train_map['BTC'], (x_train_map['BTC'].shape[0], x_train_map['BTC'].shape[1], 5))
# print(output_array[0][0][1])
# empty = np.zeros((x_train_map['BTC'].shape[0], x_train_map['BTC'].shape[1], 1 + embedding_size))

# for i in range(x_train_map['BTC'].shape[0]):
#     for j in range(x_train_map['BTC'].shape[1]):
#         for k in range(embedding_size):
#             empty[i][j][k] = output_array[0][0][k]

# for i in range(x_train_map['BTC'].shape[0]):
#     for j in range(x_train_map['BTC'].shape[1]):
#         empty[i][j][4] = x_train_map['BTC'][i][j][0]

# print(empty)

#   x_train_map[]

print(x_train_map['BTC'].shape)

batch_size = 30
num_epochs = 50

# **********************SimpleRNN****************************
model = Sequential()
# Prvi sloj
model.add(SimpleRNN(units=50, dropout=0.2, recurrent_dropout=0.2, return_sequences=True, input_shape=(X_train.shape[1],1)))

# Drugi sloj
model.add(SimpleRNN(units=50, dropout=0.2, recurrent_dropout=0.2, return_sequences=True))

# Treci sloj
model.add(SimpleRNN(units=50, dropout=0.2, recurrent_dropout=0.2, return_sequences=True))

# Cetvrti sloj
model.add(SimpleRNN(units=50, dropout=0.2, recurrent_dropout=0.2))

# Izlazni sloj
model.add(Dense(units=1))

# **********************GRU****************************
model = Sequential()
# Prvi sloj
model.add(GRU(units=50, dropout=0.2, recurrent_dropout=0.2, return_sequences=True, input_shape=(X_train.shape[1],1)))

# Drugi sloj
model.add(GRU(units=50, dropout=0.2, recurrent_dropout=0.2, return_sequences=True))

# Treci sloj
model.add(GRU(units=50, dropout=0.2, recurrent_dropout=0.2, return_sequences=True))

# Cetvrti sloj
model.add(GRU(units=50, dropout=0.2, recurrent_dropout=0.2))

# Izlazni sloj
model.add(Dense(units=1))

# **********************LSTM****************************
model = Sequential()

# Prvi sloj
model.add(LSTM(units=50, dropout=0.2, recurrent_dropout=0.2, return_sequences=True, input_shape=(x_train_map['BTC'].shape[1], 5)))

# Drugi sloj
model.add(LSTM(units=50, dropout=0.2, recurrent_dropout=0.2, return_sequences=True))

# Treci sloj
model.add(LSTM(units=50, dropout=0.2, recurrent_dropout=0.2, return_sequences=True))

# Cetvrti sloj
model.add(LSTM(units=50, dropout=0.2, recurrent_dropout=0.2))

# Izlazni sloj
model.add(Dense(units=1))

# Standardan binarni crossentropy loss i adam optimizacija
model.compile(loss='mean_squared_error',
              optimizer='adam')

model.fit(x_train_map['BTC'], y_train_map['BTC'],
          batch_size=batch_size,
          epochs=num_epochs)

# _, acc = model.evaluate(X_test, Y_test,
#                         batch_size=batch_size)

# print('Accuracy na test skupu:', acc)

def plot_predictions(test,predicted):
    plt.plot(test, color='red',label='Real Bitcoin Price')
    plt.plot(predicted, color='blue',label='Predicted Bitcoin Price')
    plt.title('Bitcoin Price Prediction')
    plt.xlabel('Time')
    plt.ylabel('Bitcoin Price')
    plt.legend()
    plt.show()

x_train = []
for i in range(0, train_v.shape[0]):
  x_train.append(i)
plt.plot(x_train,train_v, color = 'blue', label = 'Train')
x_test = []
for i in range(0, test_v.shape[0]):
  x_test.append(train_v.shape[0] + i)
plt.plot(x_test, test_v, color = 'red', label = 'Test')
plt.legend()
plt.show()

print(x_test_map['BTC'].shape)
x_test_map['BTC'] = np.reshape(x_test_map['BTC'], (x_test_map['BTC'].shape[0], x_test_map['BTC'].shape[1], 1))
predicted_bitcoin_price = model.predict(x_test_map['BTC'])
predicted_bitcoin_price = scaler.inverse_transform(predicted_bitcoin_price)

plot_predictions(dict_coins_test['BTC'], predicted_bitcoin_price)

from sklearn.metrics import mean_squared_error
def return_rmse(test,predicted):
    rmse = math.sqrt(mean_squared_error(test, predicted))
    print("The root mean squared error is {}.".format(rmse))
return_rmse(test_v,predicted_price)