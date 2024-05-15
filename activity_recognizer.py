# this program recognizes activities
import matplotlib
from matplotlib import pyplot as plt
from sklearn import svm
import seaborn as sns # for nice visualizations
import pandas as pd # for loading the data from csv
import numpy as np
from sklearn.preprocessing import scale, StandardScaler, MinMaxScaler, OrdinalEncoder
from sklearn.model_selection import train_test_split

scaler = MinMaxScaler()
classifier = svm.SVC(kernel='rbf')


def train_model():
    # load the data
    rowing1 = pd.read_csv('data/data_resampled/emma-rowing-1.csv')
    rowing2 = pd.read_csv('data/data_resampled/emma-rowing-2.csv')
    rowing3 = pd.read_csv('data/data_resampled/emma-rowing-3.csv')
    rowing4 = pd.read_csv('data/data_resampled/emma-rowing-4.csv')
    rowing5 = pd.read_csv('data/data_resampled/emma-rowing-5.csv')

    rowing_full = pd.concat([rowing1, rowing2, rowing3, rowing4, rowing5])

    lifting1 = pd.read_csv('data/data_resampled/emma-lifting-1.csv')
    lifting2 = pd.read_csv('data/data_resampled/emma-lifting-2.csv')
    lifting3 = pd.read_csv('data/data_resampled/emma-lifting-3.csv')
    lifting4 = pd.read_csv('data/data_resampled/emma-lifting-4.csv')
    lifting5 = pd.read_csv('data/data_resampled/emma-lifting-5.csv')

    lifting_full = pd.concat([lifting1, lifting2, lifting3, lifting4, lifting5])

    running1 = pd.read_csv('data/data_resampled/emma-running-1.csv')
    running2 = pd.read_csv('data/data_resampled/emma-running-2.csv')
    running3 = pd.read_csv('data/data_resampled/emma-running-3.csv')
    running4 = pd.read_csv('data/data_resampled/emma-running-4.csv')
    running5 = pd.read_csv('data/data_resampled/emma-running-5.csv')

    running_full = pd.concat([running1, running2, running3, running4, running5])

    jumpingjacks1 = pd.read_csv('data/data_resampled/emma-jumpingjacks-1.csv')
    jumpingjacks2 = pd.read_csv('data/data_resampled/emma-jumpingjacks-2.csv')
    jumpingjacks3 = pd.read_csv('data/data_resampled/emma-jumpingjacks-3.csv')
    jumpingjacks4 = pd.read_csv('data/data_resampled/emma-jumpingjacks-4.csv')
    jumpingjacks5 = pd.read_csv('data/data_resampled/emma-jumpingjacks-5.csv')

    jumpingjacks_full = pd.concat([jumpingjacks1, jumpingjacks2, jumpingjacks3, jumpingjacks4, jumpingjacks5])

    # drop rows with missing values due to resampling
    rowing_full = rowing_full.dropna()
    lifting_full = lifting_full.dropna()
    running_full = running_full.dropna()
    jumpingjacks_full = jumpingjacks_full.dropna()


    # add a column with the activity-type
    rowing_full['activity'] = '0'
    lifting_full['activity'] = '1'
    running_full['activity'] = '2'
    jumpingjacks_full['activity'] = '3'


    # combine data
    data = pd.concat([rowing_full, lifting_full, running_full, jumpingjacks_full])
    #drop id and timestamp
    data = data.drop(columns=['id', 'timestamp'])
    data = data.reset_index(drop=True)

    print(data)

    #data['activity'] = OrdinalEncoder().fit_transform(data[['activity']])

    print(data)
    # fit scaler to data
    scaler.fit(data[['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']])

    # scale data
    data[['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']] = scaler.transform(data[['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']])

    x_train, x_test, y_train, y_test = train_test_split(data[['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']], data['activity'], test_size=0.2)


    classifier.fit(x_train, y_train)
    return classifier

def predict_activity(acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z):
    currdata = pd.DataFrame(columns=['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z'], data=[[acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z]])
    currdata[['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']] = scaler.transform(currdata[['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']])

    return classifier.predict(currdata)[0]
