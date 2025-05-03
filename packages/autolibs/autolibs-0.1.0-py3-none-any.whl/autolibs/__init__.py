
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import sys

print("[autolibs] Imported libraries and their versions:")
print(f" - numpy: {np.__version__}")
print(f" - pandas: {pd.__version__}")
print(f" - matplotlib: {matplotlib.__version__}")
print(f" - seaborn: {sns.__version__}")
print(f" - Python version: {sys.version[:7]}")



__all__ = ['np', 'pd', 'plt', 'sns']
