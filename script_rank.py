#%%
import numpy as np

import matplotlib.pyplot as plt


H = np.loadtxt('H_acdc.csv', delimiter=',')
var = np.loadtxt('var_acdc.csv', delimiter=',', dtype=str)
z = np.loadtxt('z_acdc.csv', delimiter=',', dtype=str)
rank_H = np.linalg.matrix_rank(H)

var = [v.replace("var_", "") for v in var]
print("Rank of H:", rank_H)

plt.figure(figsize=(12, 8))
plt.spy(H)
plt.xlabel('Variables')
plt.ylabel('Z')
plt.axhline(y=26 - 0.5, color='red', linestyle='--')
plt.axhline(y=42 - 0.5, color='red', linestyle='--')


# Draw vertical lines between variable types
# Example: suppose variable types change at indices 10 and 20
# Replace these indices with the actual split points for your data
variable_type_splits = [10, 14, 24, 28]  # update as needed
for idx in variable_type_splits:
    plt.axvline(x=idx - 0.5, color='blue', linestyle='--')

plt.xticks(ticks=np.arange(len(var)), labels=var, rotation=90)
plt.yticks(ticks=np.arange(len(z)), labels=z)
plt.title('Spy plot of H')
plt.show()
# %%
