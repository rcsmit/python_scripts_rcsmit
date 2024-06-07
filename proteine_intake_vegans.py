import pandas as pd
import matplotlib.pyplot as plt

# Create a DataFrame with the data
# Create a DataFrame with the data
data = {
    'Omnivore': [1, 0.8, 1.2],
    'Flexitarian': [1, 0.8, 1.2],
    'Vega': [0.9, 0.7, 1.1],
    'Vegan': [0.8, 0.7, 1.0]
}
df = pd.DataFrame(data)

# Create a boxplot for each group
# df.boxplot()
# plt.xlabel('Group')
# plt.ylabel('Protein Intake')
# plt.title('Protein Intake by Group')
# plt.show()

# <!-- 
# This code will generate a boxplot with three boxes: one for the 'Value' column and one for each of the confidence interval columns ('Low CI' and 'High CI'). Each box represents the distribution of the respective data column, and the whiskers indicate the range of the data. You can customize the plot as needed by modifying the labels, axes, and title.

# Make sure you have the pandas and matplotlib libraries installed in your Python environment before running this code. -->

from scipy.stats import ttest_ind

# Define the protein intake values for each group
omnivore = [1] * 57
flexitarian = [1] * 47
vega = [0.9] * 36
vegan = [0.8] * 18

print (omnivore)
list = [["omnivore", omnivore],
        ["flexitarian", flexitarian],
        ["vega", vega],
        ["vegan", vegan]]



for x in range(len(list)):
    for y in range(len(list)):
                
        # Perform the independent samples t-test between Omnivore and Flexitarian groups
        a = list[x][1]
        b = list[y][1]
        statistic, p_value = ttest_ind(a,b)
        print(f'P-value  t-test {list[x][0]} - {list[y][0]}: {round(p_value,3)}')

from scipy.stats import f_oneway

# Combine all the protein intake values into one list
protein_intake = [omnivore, flexitarian, vega, vegan]

# Perform the ANOVA test



statistic, p_value = f_oneway(*protein_intake)

print('P-value anova:', p_value)
############
from scipy.stats import ttest_ind_from_stats
from tabulate import tabulate

# Define the sample sizes for each group
sample_sizes = [57, 47, 36, 18]

# Define the averages, lower CIs, and upper CIs for each group
averages = [1, 1, 0.9, 0.8]
low_cis = [0.8, 0.8, 0.7, 0.7]
high_cis = [1.2, 1.2, 1.1, 1.0]

# Calculate the standard deviations for each group based on CIs
stds = [(high_ci - low_ci) / (2 * 1.96) for low_ci, high_ci in zip(low_cis, high_cis)]

# Define the group names
group_names = ['Omnivore', 'Flexitarian', 'Vega', 'Vegan']

# Perform the t-tests for all combinations of groups and store the results
results = []
for i in range(len(sample_sizes)):
    for j in range(i + 1, len(sample_sizes)):
        statistic, p_value = ttest_ind_from_stats(averages[i], stds[i], sample_sizes[i],
                                                 averages[j], stds[j], sample_sizes[j])
        result = [group_names[i], group_names[j], p_value]
        results.append(result)

# Format the results into a table
table_headers = ['Group 1', 'Group 2', 'P-value']
table = tabulate(results, headers=table_headers, floatfmt=".3f")

# Print the table
print(table)


# Perform the one-way ANOVA test
f_statistic, p_value = f_oneway(*[avg * size for avg, size in zip(averages, sample_sizes)])

# Format the overall results into a table
results = list(zip(group_names, averages, sample_sizes))
table_headers = ['Group', 'Average', 'Sample Size']
table = tabulate(results, headers=table_headers, floatfmt=".2f")

# Print the table
print(table)
print(f'\nP-value ANOVA: {p_value:.3f}')