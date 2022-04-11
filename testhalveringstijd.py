import math
R = [0.7, 0.8, 0.9, 0.95,1.05,1.1,1.2,1.3]
R = [0.9,1.3]
D = [15.0,30.0,44.0]
Hv = []
cases = []
DAYS = 43
X= 4
#Halveringstijd = (math.log(2) /  (1 - (t**(1/5))))
ht1 = X * math.log(0.5) / math.log(0.9) 
ht2 = X * math.log(0.5) / math.log(1.3) 

for d in D:
    a = (10 * (0.5**(d/ht2)))
    b = (90 * (0.5**(d/ht1)))
    c= a+b
    print (a)
    print (b)
    print (c)

