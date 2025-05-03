# Core Libraries
import math
import statistics as stats
import random
import sys

# NumPy
import numpy as np

# Pandas
import pandas as pd
pd.set_option('display.max_columns', None)

# Plotting
import matplotlib
matplotlib.rcParams['figure.figsize'] = (6, 6)

import matplotlib.pyplot as plt
import seaborn as sns
# sns.set(style="whitegrid", palette="muted")

# Confirmation
print(f"Packages Successfully Imported:\n"
      f"  Imported NumPy as np: {np.__version__}\n"
      f"  Imported Pandas as pd: {pd.__version__}\n"
      f"  Imported Matplotlib.pylab as plt: {matplotlib.__version__}\n"
      f"  Imported Seaborn as sns : {sns.__version__}\n"
      f"  Your Py version : {sys.version[:7]}\n")
