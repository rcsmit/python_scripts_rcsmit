import math 

pi = math.pi

diameters = [22.5,29,37,42.5]

oppervlaktes = []

for i,d in enumerate(diameters):
    oppervlakte = ((d/2)**2)*pi 
    #print (f"{oppervlakte} - {oppervlakte/(i+1)} - {round(oppervlakte*250/1075.2100856911068,0)}")
    print (f"{oppervlakte} - {oppervlakte/(i+1)} - {round(oppervlakte*100/397.60782021995817,0)}  - {round(oppervlakte*100/397.60782021995817,0)/(i+1)}")
