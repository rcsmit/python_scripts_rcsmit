import random
import matplotlib.pyplot as plt
from plotly.graph_objs import Bar, Layout
from plotly import offline


results = []
x = []


for n in range (1,100):
    results.append(random.randint(0,8))

    #results.append ( int((norm.rvs(size=1,loc=1,scale=0.15)[0]*7).round(0)))
    x.append(n)

# fig, ax = plt.subplots()
# plt.plot(x,results, label='Cummulative actual cases total')


# #plt.show()


frequencies = []
    # print (results)
m = max(results)+1
for value in range(1,m):
    freq = results.count(value)
    frequencies.append(freq)
#print (frequencies)
cumm=[]
t=0

# calculate cummulative values
for freq in frequencies:
    t+=freq
    cumm.append(t)

#visualize in the browser
x_values = list (range(1,m))
data = [Bar (x=x_values, y = frequencies)]

x_axis_config = {'title':'Result'}
y_axis_config = {'title':'Frequency'}
TITLE = "x"
my_layout = Layout (title=TITLE,
                    xaxis = x_axis_config, yaxis=y_axis_config)
offline.plot ({'data':data, 'layout': my_layout})



# plot on the console
plt.xlabel("# of dice thrown ")
plt.ylabel("frequencies")
plt.bar(x_values, frequencies)
plt.show
