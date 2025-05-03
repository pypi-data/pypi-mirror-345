
from statistics import *
from math import *
from random import *

import numpy as np
import pandas as pd
pd.set_option('display.max_columns', None)

import matplotlib
# Default-img size
matplotlib.rcParams['figure.figsize'] = (6,6)

import matplotlib.pyplot as plt
import seaborn as sns
import sys

print("Packages Succesfully Imported")
print("np", np.__version__)
print("pd", pd.__version__)
print("plt", matplotlib.__version__)
print("sns", sns.__version__)
print("py", sys.version[:7])

__all__ = ['np', 'pd', 'plt', 'sns']
