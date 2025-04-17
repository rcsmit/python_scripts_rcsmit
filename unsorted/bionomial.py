
# https://www.geeksforgeeks.org/python-binomial-distribution/

# It sounds unlikely, though Kean is convinced. Consider the arithmetic, he argues.
#  Caesar’s final breath – exhaled as he was stabbed to death in the senate – would
#  have contained about a litre of air made up of about 25 thousand million million
#  million molecules. At the same time, a litre of air represents 0.000000000000000000001% 
# of all the air on Earth. When you crunch these numbers, says Kean, you will find that roughly 
# one particle of the last air that was breathed out by Caesar more than 2,000 years ago will 
# appear in your next breath. “Across all that distance of time and space, a few of the
#  molecules that danced inside his lungs are dancing inside yours right now.”

from scipy.stats import binom

import sys, scipy, numpy; print(scipy.__version__, numpy.__version__, sys.version_info)



def calculate(n, p, r):

    """_summary_
    n : number of independent trials
    r : number of successes
    p : probability of success at each trial
    What is the probability of r successes and n-r fails out of n independent trials, 
    if the probability of success at each trial is p and failure is 1-p ?

    """    
    print (f"{n=} {p=} {r=}")
    # print  (f"PMF  The chance that you inhale {r} molecules {binom.pmf(r, n, p)}") 
    print  (f"CDF The chance that you inhale {r} molecules {binom.cdf(r, n, p)}")
    if r == 0 :
        print  (f"CDF The chance that you inhale at least 1 molecule {1-binom.cdf(r, n, p)}")    

    print ()

#https://github.com/scipy/scipy/issues/17388
print(binom.ppf(q = 0.0, n = 4, p = 0.5)) # prints -1.0 (but should be 0.0?)
print(binom.ppf(q = 0.3, n = 4, p = 1.0)) # prints 0.0 (but should be 4.0?)


n = 25.0*10**21 # number of molecules of a liter of air
p = 1.0*10**-21 #At the same time, a litre of air represents 0.000000000000000000001%  # of all the air on Earth
r = 0
calculate(n, p, r) 

print ("Atoms in the body")
n = 7.0*10**27 # number of atoms in the body
n2=1.3*10**50 #number of atoms in the world

p = n / n2
# print (p)
r = 1.0

calculate(n, p, r) 


# Pee from the heart
# values calculated at https://docs.google.com/document/d/1WM_d2mYAUOBW68i7ucnc3rOK0EtgAXHEtTat3p1ZmrY/edit?usp=sharing
print ("Pee from the heart")
n = 16.75*10**23
p = 0.23*10**-22
r = 0
calculate(n, p, r) 

def knikkertest():

    # Uit een vaas met 4 rode en 6 witte knikkers worden, aselect en met teruglegging,
    # 0 drie knikkers getrokken. De stochast X is het aantal rode knikkers.
    n = 3
    p = 0.4
    r = 0
    calculate(n, p, r) 
    j = 0
    for i in range(11):
        y = binom.cdf(i, n, p)
        z= binom.pmf(i, n, p)
        j +=z
        print(f"{i} - {z} - // {y} {j} ")
