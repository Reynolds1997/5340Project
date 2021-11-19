"""
The ML system we use to build a model
"""

import sys
import pandas as pd
import numpy as np
import re
import pickle
import random
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import Perceptron
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report




def read_csv_for_ml(csv_path, features):
    # read the csv file into a pandas dataframe
    df = pd.read_csv(csv_path, encoding = "ISO-8859-1")
    df.head()

    #train = pd.read_csv("train.csv")
    null_columns=df.columns[df.isnull().any()]
    #print(df[null_columns].isnull().sum())

    print(df[df.isnull().any(axis=1)][null_columns].head())
    # assert that there were no null entries in the csv file
    assert (df.isnull().values.any() == False), 'There are null entries in the data'
    # assert that given features are columns in the csv
    assert (set(features).issubset(set(df.columns.tolist()))), 'Some of the features selected are not columns in the input csv file' 
    
    # separating the label column from the data
    X = df.drop('LABEL', axis=1)
    X = X[features]
    #print(X)
    # getting the labels of the data 
    y = df.LABEL.values
    return X, y


def vectorize_data(train_data, test_data):
    # Initialize vectorizer
    v = DictVectorizer(sparse=False)
    # We fit_transform in featurized train data (first transform the pandas dataframe into a list of dictionaries key = column name, value = entry in row)
    X_train = v.fit_transform(train_data.to_dict('records'))
    # We use the already fitted transform to transform the test data acccoring to the train data fit. (We also convert it into a list of dictionaries)
    X_test=v.transform(test_data.to_dict('records'))
    # return vectorized train and test data
    return X_train, X_test, v


def vectorizeTestData(test_data,dictVectorizer):
    # Initialize vectorizer
    v = dictVectorizer
 
    # We use the already fitted transform to transform the test data acccoring to the train data fit. (We also convert it into a list of dictionaries)
    X_test=v.transform(test_data.to_dict('records'))

    return X_test

#def perceptron(train_data, train_labels):
#    # initializing model
#    per = Perceptron(verbose=10, n_jobs=-1, max_iter=40)
#    # fitting model with train data and train labels
#    per.fit(train_data, train_labels)#, classes)
#    # saving the model to disk
#    filename = 'perceptron_model.joblib'
#    pickle.dump(per, open(filename, 'wb'))
#    return per

def logistic(train_data, train_labels):
    # initializing model
    logistic = LogisticRegression(tol = 0.1, random_state=69, solver='sag', verbose=1, n_jobs=-1) #warm_start=True, random_state=0, max_iter=5
    # fitting model with train data and train labels
    logistic.fit(train_data, train_labels)
    # saving the model to disk
    #filename = 'logistic_regression_model.joblib'
    #pickle.dump(logistic, open(filename, 'wb'))
    # return trained model

    return logistic

def createModel(training_csv,test_csv,features_set):
    assert 'WORD' in features_set, 'WORD is a mandatory feature'
    #assert features_set.issubset({'CAP', 'ABBR', 'SUFF', 'PREF', 'WORD', 'GLOBSUFF', 'GLOBPREF', 'POS+1', 'POS-1', 'WORD-1', 'WORD+1', 'POS', 'LOC', 'GLOBCAP'}), 'There is an invalid feature name'

    #Here we put the features set!

    # reading the csv files into pandas data frames separating the instances from the labels as an numpy array
    train_df, train_labels = read_csv_for_ml(training_csv, list(features_set))
    test_df, test_labels = read_csv_for_ml(test_csv, list(features_set))

    #train_columns = train_df.columns.tolist()
    #test_columns = test_df.columns.tolist()
    #random.shuffle(columns)
    #train_df = train_df[columns]
    #test_df = test_df[columns]

    # vectorizing: fitting and transforming the train dataframe, using the tranformation to get also the vectorized test set from the test dataframe
    vec_train_data, vec_test_data, v = vectorize_data(train_df, test_df)

    #print('Classification algorithm: {}'.format(algorithm))
    # training perceptron model using the train data 
    #if algorithm == 'perceptron':
    #    model = perceptron(vec_train_data, train_labels)
    #elif algorithm == 'logistic':
    model = logistic(vec_train_data, train_labels)
    #classes = np.unique(train_labels.tolist()+test_labels.tolist())
    #print(classes)
    #classes = classes.tolist()

    return model,test_labels,vec_test_data,v
    
if __name__ == '__main__':

    trainingCSV = sys.argv[1]
    testCSV = sys.argv[2]
    #algorithm = str(sys.argv[3])
    featuresSet = set(sys.argv[3:])
    print('Running Logistic Regression classification algorithm...')

    model, test_labels, vec_test_data, v = createModel(trainingCSV,testCSV,featuresSet)

    



#Testing stuff
    classes = ['B-ACQUIRED','I-ACQUIRED','B-ACQBUS','I-ACQBUS','B-ACQLOC','I-ACQLOC','B-DLRAMT','I-DLRAMT','B-PURCHASER','I-PURCHASER','B-SELLER','I-SELLER','B-STATUS','I-STATUS','O']

    #classes = ['ACQUIRED','ACQBUS','ACQLOC','DLRAMT','PURCHASER','SELLER','STATUS']
    #classes = ['B-PER', 'I-PER', 'B-ORG', 'I-ORG', 'B-LOC', 'I-LOC', 'O'] 
    
    
    print(classification_report(y_pred=model.predict(vec_test_data), y_true=test_labels, labels=classes))
    










    
