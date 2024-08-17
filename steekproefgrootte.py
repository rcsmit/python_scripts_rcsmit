# Define the sample size formula
# https://nl.surveymonkey.com/mp/sample-size-calculator/



# https://nl.checkmarket.com/blog/de-steekproefgrootte-bepalen-van-je-enquete/
# https://www.checkmarket.com/wp-content/uploads/2015/06/betrouwbaarheidsniveau.gif
z= 1.96 #  z = z-score
p = 0.95 # p = betrouwbaarheidsniveau
e = 0.05 # e = foutmarge (percentage in decimale vorm) 
N=6000000 # N = populatieomvang 

print (f"z^2 = {z**2}")
print (f"p * (1 - p) = {p * (1 - p)}")
print (f"e^2 = {e**2}")
sample_size = (z**2 * p * (1 - p) / e**2) / (1 + (z**2 * p * (1 - p) / (e**2 * N)))
print (int(sample_size))

# https://www.qualtrics.com/experience-management/research/determine-sample-size/
cochran_large_populations =  (z**2 * p * (1 - p) / e**2) 
print (f"{cochran_large_populations=}")


cochran2 = (z**2 * N*p * (1-p)) / (e**2 + z**2 * p * (1-p))
print (f"{cochran2=}")


yamane = N/ (1+(N*e*e)) # https://www.linkedin.com/pulse/how-calculate-sample-size-oualid-soula/
print (f"{yamane=}")
