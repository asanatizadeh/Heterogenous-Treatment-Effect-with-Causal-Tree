# -*- coding: utf-8 -*-
"""HonestTree_Synthetics.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ixEbLyoJl8fKlBugi6HHoJFqEREFhwIE
"""

from google.colab import drive
drive.mount('/content/drive')

!pip install causal_tree_learn

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/MyDrive/ColabPractice/causal

import pandas as pd
import matplotlib.pyplot as plt

from CTL.causal_tree_learn import CausalTree
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
import scipy
import sklearn
import cython
import seaborn as sns

def binary(x):
  list= []
  for i in range(x):  
    temp = np.random.randint(0, 1)
    list.append(temp)
          
  return list

n= 10000
np.random.seed(0)

x = np.random.randn(n, 10)
x.shape
x[0]

y = binary(n)
np.unique(y)

y = np.random.randint(2, size= n)
treatment = np.random.randint(2, size= n)

x_train, x_test, y_train, y_test, treat_train, treat_test = train_test_split(x, y, treatment,
                                                                             test_size=0.5, random_state=42)

variable_names = []
for i in range(x.shape[1]):
    variable_names.append(f"Column {i}")

# honest CT (Athey and Imbens, PNAS 2016)
ct_honest = CausalTree(honest=True, weight=0.0, split_size=0.0)
ct_honest.fit(x_train, y_train, treat_train)
ct_honest.prune()
ct_honest_predict = ct_honest.predict(x_test)

ct_honest.plot_tree(features=variable_names, filename="synthetic_output/causal_tree_honest", show_effect=True)

# CTL (CT- L)
ctl = CausalTree(magnitude=False)
ctl.fit(x_train, y_train, treat_train)
ctl.prune()
ctl_predict = ctl.predict(x_test)

ctl.plot_tree(features=variable_names, filename="synthetic_output/bin_tree", show_effect=True)

# honest CTL (CT-HL)
cthl = CausalTree(honest=True,)
cthl.fit(x_train, y_train, treat_train)
cthl.prune()
cthl_predict = cthl.predict(x_test)

cthl.plot_tree(features=variable_names, filename="synthetic_output/bin=_tree_honest_learn", show_effect=True)

# val honest CTL (CT-HV)
cthv = CausalTree(val_honest=True)
cthv.fit(x_train, y_train, treat_train)
cthv.prune()
cthv_predict = cthv.predict(x_test)

cthv.plot_tree(features=variable_names, filename="synthetic_output/bin_tree_honest_validation", show_effect=True)