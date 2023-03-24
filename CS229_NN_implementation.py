# -*- coding: utf-8 -*-
"""Copy of CS230_Keras_implementation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PVvfVKx3yn2lTHQfjHf7Ic2jDkRwh_Ll

CS 230 Project work: 
This project analyzes the delta increase in electricity consumption from the extreme weather data in California. 

We will begin by importing our dataset.
"""

# Commented out IPython magic to ensure Python compatibility.
import tensorflow as tf
import pandas as pd
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.callbacks import TensorBoard
from sklearn.preprocessing import LabelEncoder
from keras.utils import np_utils
import keras
import numpy as np
import os
import seaborn as sns

# %matplotlib inline

from google.colab import drive
drive.mount('/content/drive')

dataset = pd.read_csv('/content/drive/Shareddrives/CS_229_project/Electricity_Consumption_data/dataset_final.csv', usecols = ['AWND','DAPR','DASF','EVAP','MDPR','MDSF','MNPN','MXPN','PGTM','PRCP','PSUN','SN33','SN35','SNOW','SNWD','SX32','SX33','TAVG','TMAX','TMIN','TOBS','TSUN','WDF2','WDF5','WDFG','WDMV','WESD','WESF','WSF2','WSF5','WSFG','WSFI','CLASS_2'])

dataset

#Applying Linear Discriminant Analysis
# from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

# clf = LinearDiscriminantAnalysis(solver='svd', shrinkage=None, tol = 0.0001, covariance_estimator=None)
# fit_transform(x_train_norm, y_train)
# clf.fit(x_train_norm, y_train)
# LinearDiscriminantAnalysis()

"""We now have imported our dataset. We move into creating our layers and then working through our layers. """

#split train & test dataset
train = dataset.sample(frac=0.8) #random_state=0
test = dataset.drop(train.index)
print(train.shape, test.shape)

"""One hot encoding for Train & Test dataset"""

#Create one-hot encoding for TRAIN dataset
existing_vals = np.unique(train['CLASS_2'].values)
mapping = {val: idx for idx, val in enumerate(existing_vals)}
y_train = np.array([mapping[y] for y in train['CLASS_2'].values])
y_train = np_utils.to_categorical(y_train)
print(y_train.shape)
y_train

#Create one-hot encoding for TEST dataset
existing_vals = np.unique(test['CLASS_2'].values)
mapping = {val: idx for idx, val in enumerate(existing_vals)}
y_test = np.array([mapping[x] for x in test['CLASS_2'].values])
y_test = np_utils.to_categorical(y_test)

print(y_test.shape)
y_test

#sns.pairplot(train[['CLASS_2', 'AWND', 'PRCP', 'SNWD', 'TAVG', 'TMIN', 'TMAX']], diag_kind='kde')

train.describe().transpose()

test.describe().transpose()

"""Train and test data cleaning"""

#train data normalization
train_features = train.copy()
train_labels = train_features.pop('CLASS_2')
train_labels

#test data normalization
test_features = test.copy()
test_labels = test_features.pop('CLASS_2')
test_labels

print(y_train)

# train_features.shape
x_train_clean = train_features.fillna(0).dropna()

#test feature cleaning 
x_test_clean = test_features.fillna(0).dropna()
x_test_clean

"""Normalizing our train & test clean data set"""

#normalize x_train_clean 
normalizer = tf.keras.layers.Normalization()
normalizer.adapt(x_train_clean)
x_train_norm = normalizer(x_train_clean)
x_train_norm.shape

#normalize x_test_clean
normalizer = tf.keras.layers.Normalization()
normalizer.adapt(x_test_clean)
x_test_norm = normalizer(x_test_clean)
x_test_norm.shape

"""Create model"""

#Import CLASS_2es
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense, Dropout

#Model Definition
model = Sequential()
model.add(Input(shape=(32,)))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(64,activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(64,activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(64,activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(64,activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(32,activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(5, activation='softmax'))

#Configure model training
model.compile(optimizer='adam',loss='categorical_crossentropy', metrics=['accuracy']) #

"""Model Fit"""

#train model
from keras import backend as K
K.set_value(model.optimizer.learning_rate, 0.0005)
history = model.fit(x_train_norm, y_train, validation_split=0.1, epochs=500)

print(history.history.keys())

#plot training accuracy
from matplotlib import pyplot as plt
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

"""Model predict"""

#predict on testing dataset
model.compile(optimizer='adam',loss='categorical_crossentropy', metrics=['accuracy'])
K.set_value(model.optimizer.learning_rate, 0.0008)
y_pred = model.predict(x_test_norm)
y_pred
#print('y_pred',y_pred)
y_pred.shape, y_test.shape
y_test = y_test.argmax(axis=-1)
print('y_test', y_test)
y_pred = y_pred.argmax(axis=-1)
print('y_pred',y_pred)

#Compute Recall, precision, f1_score
# from sklearn.metrics import precision_score , recall_score

from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred))

#Compute confusion matrix using accuracy_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
test_acc = accuracy_score(y_test, y_pred)

confusion_matrix(y_test, y_pred)

#SMOTE Implementation 
#Link: https://machinelearningmastery.com/multi-class-imbalanced-classification/ 

# example of oversampling a multi-class classification dataset
from pandas import read_csv
import imblearn
from imblearn.over_sampling import SMOTE
from collections import Counter
from matplotlib import pyplot
from sklearn.preprocessing import LabelEncoder

# define the dataset location
url = '/content/drive/Shareddrives/CS_229_project/Electricity_Consumption_data/dataset_final.csv'
# load the csv file as a data frame
df = read_csv(url, usecols=['AWND','DAPR','DASF','EVAP','MDPR','MDSF','MNPN','MXPN','PGTM','PRCP','PSUN','SN33','SN35','SNOW','SNWD','SX32','SX33','TAVG','TMAX','TMIN','TOBS','TSUN','WDF2','WDF5','WDFG','WDMV','WESD','WESF','WSF2','WSF5','WSFG','WSFI','CLASS_2'])
df = df.fillna(0).dropna()
data = df.values

# split into input and output elements
X, y = data[:, :-1], data[:, -1]

# label encode the target variable
y = LabelEncoder().fit_transform(y)
# transform the dataset
oversample = SMOTE()
X, y = oversample.fit_resample(X, y)
# summarize distribution
counter = Counter(y)
for k,v in counter.items():
	per = v / len(y) * 100
	print('Class=%d, n=%d (%.3f%%)' % (k, v, per))
# plot the distribution
pyplot.bar(counter.keys(), counter.values())
pyplot.show()

# summarize distribution
counter = Counter(train_labels)
for k,v in counter.items():
	per = v / len(y) * 100
	print('Class=%d, n=%d (%.3f%%)' % (k, v, per))
# plot the distribution
pyplot.bar(counter.keys(), counter.values())
pyplot.show()

#Latest X & y values
print('X',X.shape)
print('y', y.shape)
#print('X:',X)
#print('y:',y)
#type(X)
type(y)
n = X.shape[0]

#Concetanate X & y
y = np.reshape(y, (n,1))
print('y',y)
data = np.concatenate((X, y), axis=1)
print(data)

#Convert 'data' to pandas dataframe
dataset_s = pd.DataFrame(data, columns=['AWND','DAPR','DASF','EVAP','MDPR','MDSF','MNPN','MXPN','PGTM','PRCP','PSUN','SN33','SN35','SNOW','SNWD','SX32','SX33','TAVG','TMAX','TMIN','TOBS','TSUN','WDF2','WDF5','WDFG','WDMV','WESD','WESF','WSF2','WSF5','WSFG','WSFI','CLASS_2'])
dataset_s

#split train & test dataset
train_s = dataset_s.sample(frac=0.9) #random_state=0
test_s = dataset_s.drop(train_s.index)
print(train_s.shape, test_s.shape)

#Create one-hot encoding for TRAIN dataset
existing_vals = np.unique(train_s['CLASS_2'].values)
mapping = {val: idx for idx, val in enumerate(existing_vals)}
y_train_s = np.array([mapping[y] for y in train_s['CLASS_2'].values])
y_train_s = np_utils.to_categorical(y_train_s)
print(y_train_s.shape)
y_train_s

#Create one-hot encoding for TEST dataset
existing_vals = np.unique(test_s['CLASS_2'].values)
mapping = {val: idx for idx, val in enumerate(existing_vals)}
y_test_s = np.array([mapping[x] for x in test_s['CLASS_2'].values])
y_test_s = np_utils.to_categorical(y_test_s)

print(y_test_s.shape)
y_test_s

#train data normalization
train_features_s = train_s.copy()
train_labels_s = train_features_s.pop('CLASS_2')
train_labels_s

#test data normalization
test_features_s = test_s.copy()
test_labels_s = test_features_s.pop('CLASS_2')
test_labels_s

#Clean x_train_s & x_test_s
x_train_clean_s = train_features_s.fillna(0).dropna()
x_test_clean_s = test_features_s.fillna(0).dropna()
print(x_train_clean_s)
print(x_test_clean_s)

#normalize x_train_clean 
normalizer = tf.keras.layers.Normalization()
normalizer.adapt(x_train_clean_s)
x_train_norm_s = normalizer(x_train_clean_s)
x_train_norm_s.shape

#normalize x_test_clean
normalizer = tf.keras.layers.Normalization()
normalizer.adapt(x_test_clean_s)
x_test_norm_s = normalizer(x_test_clean_s)
x_test_norm_s.shape

#Import CLASS_2es
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense, Dropout
from tensorflow.keras import regularizers

#Model Definition
model = Sequential()
model.add(Input(shape=(32,)))
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(64,activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(64,activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(64,activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(64,activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(32,activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(5, activation='softmax'))

#Configure model training
model.compile(optimizer='adam',loss='categorical_crossentropy', metrics=['accuracy'])

#train model
from keras import backend as K
K.set_value(model.optimizer.learning_rate, 0.0009)
history = model.fit(x_train_norm_s, y_train_s, validation_split=0.2, epochs=500)

#plot training accuracy
from matplotlib import pyplot as plt
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

y_test_s

#predict on testing dataset
model.compile(optimizer='adam',loss='categorical_crossentropy', metrics=['accuracy'])
K.set_value(model.optimizer.learning_rate, 0.0008)
y_pred_s = model.predict(x_test_norm_s)
y_pred_s.shape, y_test_s.shape

y_test_s = y_test_s.argmax(axis=-1)
print('y_test_s', y_test_s)
y_pred_s = y_pred_s.argmax(axis=-1)
print('y_pred_s',y_pred_s)

#Compute Recall, precision, f1_score
from sklearn.metrics import classification_report
print(classification_report(y_test_s, y_pred_s))