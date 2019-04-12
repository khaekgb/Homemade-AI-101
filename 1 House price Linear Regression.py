
# coding: utf-8

# In[1]:


# Part 1 - Data Preprocessing

# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Importing the dataset
dataset = pd.read_csv('house price.csv')
X = dataset.iloc[:,[-1]].values
y = dataset.iloc[:, [1]].values
dataset


# In[2]:


# Feature Scaling
# from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
sc_X = MinMaxScaler()
X = sc_X.fit_transform(X)
sc_y = MinMaxScaler()
y = sc_y.fit_transform(y)


# In[3]:


# Fitting Simple Linear Regression to the Training set
from sklearn.linear_model import LinearRegression
regressor = LinearRegression()    # Create linear regression object
regressor.fit(X, y)   # Train the model using the training sets


# In[4]:


regressor.coef_


# In[5]:


regressor.intercept_ 


# In[6]:


from sklearn.metrics import r2_score
y_true = y
y_pred = regressor.predict(X)

print(r2_score(y_true, y_pred) )
print(sc_X.inverse_transform(X))
print()
print(sc_y.inverse_transform(y_pred).round(0))

# In[7]:


import matplotlib.pyplot as plt
plt.scatter(sc_X.inverse_transform(X),sc_y.inverse_transform(y_pred))
plt.scatter(sc_X.inverse_transform(X),sc_y.inverse_transform(y))
