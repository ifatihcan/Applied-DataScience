# -*- coding: utf-8 -*-
"""Employee_Attrition_Prediction.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1RvIO111kbEyGyn8vnJ3rn10PJe6IFA9u

Load the data and perform EDA.

https://www.kaggle.com/pavansubhasht/ibm-hr-analytics-attrition-dataset

1. Evaluate missing values
2. Assess target class distribution
3. Assess information value of individual features (correlation analysis and pairlot).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import seaborn as sns
import matplotlib.pyplot as plt

from google.colab import files
uploaded = files.upload()

import io
dt = pd.read_csv(io.BytesIO(uploaded['WA_Fn-UseC_-HR-Employee-Attrition.csv']))

dt.head()

dt.shape

dt['OverTime'].value_counts()

dt.nunique()

dt.drop(['EmployeeNumber', 'Over18','StandardHours','EmployeeCount'], axis=1,inplace=True)

dt.describe()

dt.isnull().sum()

dt.dtypes

dt['Attrition'] = dt['Attrition'].replace({'Yes': 1, 'No': 0}).astype(int)

print('Incidence of Attrition: ', dt.Attrition.mean())

dt['Education'] = dt['Education'].astype('category')
dt['EnvironmentSatisfaction'] = dt['EnvironmentSatisfaction'].astype('category')
dt['JobInvolvement'] = dt['JobInvolvement'].astype('category')
dt['JobSatisfaction'] = dt['JobSatisfaction'].astype('category')
dt['PerformanceRating'] = dt['PerformanceRating'].astype('category')
dt['RelationshipSatisfaction'] = dt['RelationshipSatisfaction'].astype('category')
dt['WorkLifeBalance'] = dt['WorkLifeBalance'].astype('category')

dt.select_dtypes(include='category')

sns.heatmap(dt.isnull(), cbar=False)
plt.title("Missing Values Heatmap")
plt.show()

dt= pd.get_dummies(dt)

dt.info()

sns.heatmap(dt.corr(), cmap="Spectral")

pd.set_option('display.max_rows', None)

dt.corr()['Attrition'].sort_values(ascending=False)

sns.pairplot(dt[['OverTime_Yes','MaritalStatus_Single','JobInvolvement_1', 'JobRole_Sales Representative','EnvironmentSatisfaction_1','MonthlyIncome','JobLevel','YearsInCurrentRole','Age','YearsWithCurrManager','TotalWorkingYears','Attrition']],hue='Attrition')
#Employees who frequently work overtime are more likely to resign.
#There's a notable trend of employees exiting the company after 14 to 16 years of service.
#Higher job levels seem to correlate with lower attrition rates, indicating greater job retention as employees advance.
#The age group with the highest attrition rate appears to be around 40 years old.

dt['Attrition'].hist()

"""4. Pre-process the dataset
5. Split the data into training/test datasets (70/30)


"""

X = dt.drop('Attrition',axis=1).values
y = dt['Attrition'].values

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.3,random_state=1)

from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
scaler.fit(X_train)

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

"""6. Build a sequential neural network with the following parameters: 3 hidden dense layers - 100, 50, 25 nodes respectively, activation function = 'relu', dropout = 0.5 for each layer).
7. Use early stopping callback to prevent overfitting.

"""

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Activation,Dropout

#when unit=1 layer activation is sigmoid gives the best result.
model = Sequential()
model.add(Dense(units=100, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(units=50, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(units=25, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(units=1, activation='sigmoid'))

model.compile(loss='binary_crossentropy', optimizer='adam')

from tensorflow.keras.callbacks import EarlyStopping

early_stop = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=5)

model.fit(x=X_train,
          y=y_train,
          batch_size=128,
          epochs=200,
          validation_data=(X_test, y_test), verbose=1,
          callbacks=[early_stop]
          )

"""8. Plot training and validation losses versus epochs.
9. Print out model confusion matrix.
10. Print out model classification report.
11. Print out model ROC AUC.

"""

model_loss = pd.DataFrame(model.history.history)
model_loss.plot()

y_pred = (model.predict(X_test) > 0.5).astype(int)

from sklearn.metrics import confusion_matrix

print(confusion_matrix(y_test,y_pred))

from sklearn.metrics import classification_report,confusion_matrix, roc_auc_score

print(classification_report(y_test,y_pred))

# ROC AUC and ROC Curve
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
import matplotlib.pyplot as plt

roc_auc_score = roc_auc_score(y_test, model.predict(X_test))
fpr, tpr, thresholds = roc_curve(y_test, model.predict(X_test))
plt.figure()
plt.plot(fpr, tpr, label='Keras (AUC = %0.2f)' % roc_auc_score)
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.savefig('Keras_ROC')
plt.show()