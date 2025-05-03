
# Basics
from statistics import *
from math import *
from random import *
import sys

# Numpy
import numpy as np

# Pandas 
import pandas as pd
pd.set_option('display.max_columns', None)

# Plot's
import matplotlib
matplotlib.rcParams['figure.figsize'] = (6,6) # Default-img-size

import matplotlib.pyplot as plt
import seaborn as sns


# Feel Free to add any-more library if required...


print("Packages Succesfully Imported : {}".format('np', 'pd', 'plt', 'sns'))
__all__ = ['np', 'pd', 'plt', 'sns']
