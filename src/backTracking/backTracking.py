import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.helperFunctions.readFromCSV import read_dataset
data = read_dataset('small')


print(data)