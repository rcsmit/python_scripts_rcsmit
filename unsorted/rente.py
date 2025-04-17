import matplotlib.pyplot as plt

var = [[2007,2.66],
    [2008,2.92],
    [2009,2.61],
    [2010,2.00],
    [2011,2.20],
    [2012,2.24],
    [2013,1.68],
    [2014,1.36],
    [2015,1.05],
    [2016,0.65],
    [2017,0.33],
    [2018,0.20],
    [2019,0.13],
    [2020,0.06],
    [2021,0.05],
    [2022,0.13],
    [2023,1.28]]
s = 1000
s_values = []  # Store s values for plotting
a_values = []
for i, v in enumerate(var):
    x = ((100 + v[1]) / 100)
    s = x * s
    s_values.append(s)
    print(f"{i} - {v[0]} - {s}")

# Calculate average 'a'
i = len(var)
a = (((s / 1000) ** (1 / i)) - 1) * 100
print (f"{a=}")
print (((a+100)/100))
s2 = 1000
for ix in range(i):
    s2 = s2*((a+100)/100)
    a_values.append(s2)
# Create a list of years
years = [v[0] for v in var]
print (a_values)
# Plot 's' values
plt.figure(figsize=(10, 6))
plt.plot(years, s_values, marker='o', label='s')
plt.plot(years, a_values, marker='x', label='a')
plt.xlabel('Year')
plt.ylabel('s Value')
plt.title('s Values Over Time')
plt.legend()



# Show legend
plt.legend()

# Show the plot
plt.grid()
plt.show()
