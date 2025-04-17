# # pee from the heart
# n = 16.75*10**23
# p = 0.23*10**-22
# q = p/n
# r = 0


# Julias Ceasar air
# n = 10**44  #aantal moleculen lucht
# q = 2 * 10**22 # aantal moleculen ademhaling
# p = q  / n
# print (p)

# Julias last glas of water
# http://www.sakano.co.uk/ja/node/1420#strategy-a
# n= 10**46
# q=10**25
# p = q  / n

# Atoms in the body 
n = 7*10**27 # number of atoms in the body
q = 1.3*10**50 #number of atoms on earth
p = n/q
print (p)
r = 0

print (paste("Prob zero molecules = ", (1-p)*q))


print(dbinom(r, size = n, prob = p))  # P(X = k)
print(pbinom(r, size = n, prob = p)) # P(X <= k)

probabilities <- dbinom(x = c(0:100), size =n, prob = p)

plot(0:100, probabilities, type = "l")
plot(0:100, pbinom(0:100, size = n, prob = p), type = "l")

# https://gist.github.com/evantravers/1791956
x = (-p)*q
y = exp(x)
z = 1-y
print (paste("Prob. Zero molecules =" , y))
print(paste("Prob. At least 1 molecule = ", z))