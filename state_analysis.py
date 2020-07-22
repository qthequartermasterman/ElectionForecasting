import numpy as np
import numpy.linalg as linalg
import sklearn.decomposition
from electoral_votes import *
import matplotlib.pyplot as plt
import PollingData

list_of_states = ['National']+list(electoral_votes.keys())

#state_data = np.genfromtxt('data/StateVectors.csv', delimiter=',', skip_header=True, usecols=range(1, 29))
state_data_standardized = np.genfromtxt('data/StandardizedDemographics.csv', delimiter=',', skip_header=True,
                                        usecols=range(1, 29))

number_of_PCA_dimensions = 4
pca_instance = sklearn.decomposition.PCA(number_of_PCA_dimensions)
pca_instance.fit(state_data_standardized)

transformed_data = pca_instance.transform(state_data_standardized)
labeled_transformed_data = np.hstack((np.array(list_of_states)[:, np.newaxis], transformed_data))
header_row = ', '.join(['State'] + [f'PCA Dim {i}' for i in range(number_of_PCA_dimensions)])
np.savetxt('data/StateEncodedVectors.csv', labeled_transformed_data, delimiter=', ',
           fmt='%s', header=header_row, comments='')


for i in range(len(list_of_states)):
    for j in range(len(list_of_states)):
        dis = linalg.norm(transformed_data[j]-transformed_data[i])
        print(list_of_states[j], list_of_states[i], dis)

# Create plot
polling_data = PollingData.PollingData()
results_2016 = polling_data.fill_2016_results()

fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
ax = fig.add_subplot(111)

for i in range(len(transformed_data)):
    row = transformed_data[i]
    x = row[0]
    y = row[1]
    z = row[2]
    state_results_2016 = results_2016[list_of_states[i]]
    if state_results_2016['D'] > state_results_2016['R']:
        color = 'blue'
    else:
        color = 'red'
    ax.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30)
    #ax.scatter(x,y,z, marker='o', c=color)

plt.title('PCA Dim 1 v. PCA Dim 2 (standardized)')
plt.legend(loc=2)
plt.show()
