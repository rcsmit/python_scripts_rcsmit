# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 15:25:34 2020

@author: rcxsm
"""
#https://scipython.com/book/chapter-6-numpy/additional-problems/analysing-snakes-and-ladders-as-a-markov-chain/
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns



#ladders = [(3,19), (15,37), (22,42), (25,64), (41,73),
#           (53,74), (63,86), (76,91), (84,98)]
#snakes = [(11,7), (18,13), (28,12), (36,34), (77,16),
#          (47,26), (83,39), (92,75), (99,70)]
#trans = ladders + snakes


ladders = [(9,22),(16,68),(19,31),( 
    
    21,59),( 
    26,40),( 
    27,49),( 
    
    44,66),( 
    36,65),( 
    45,61),( 
    53,67)]
        
snakes = [(62,1),( 
    54,2),( 
    15,3),( 
    
    28,5),( 
    23,6),( 
    11,7),( 
    
    43,8),( 
    51,34),( 
    72,51)]
trans = ladders + snakes

# Set up the transition matrix
T = np.zeros((73, 73))
for i in range(1,73):
    T[i-1,i:i+6] = 1/6

for (i1,i2) in trans:
    iw = np.where(T[:,i1] > 0)
    T[:,i1] = 0
    T[iw,i2] += 1/6

# House rules: you don't need to land on 100, just reach it.
T[67:72,72] += np.linspace(1/6, 5/6, 5)
for snake in snakes:
    T[snake,72] = 0

# The player starts at position 0.
v = np.zeros(73)
v[0] = 1

n, P = 0, []
cumulative_prob = 0
# Update the state vector v until the cumulative probability of winning
# is "effectively" 1
while cumulative_prob < 0.99999:
    n += 1
    v = v.dot(T)
    P.append(v[72])
    cumulative_prob += P[-1]
mode = np.argmax(P)+1
print('modal number of moves:', mode)

# Plot the probability of winning as a function of the number of moves
fig, ax = plt.subplots()
ax.plot(np.linspace(1,n,n), P, 'g-', lw=2, alpha=0.6, label='Markov')
ax.set_xlabel('Number of moves')
ax.set_ylabel('Probability of winning')

plt.show()
