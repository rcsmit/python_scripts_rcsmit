from scipy.stats import binom
def calculate(n, p, r):
    print (f"{n=} {p=} {r=}")
    print  (f"PMF  The chance that you inhale {r} molecules {binom.pmf(r, n, p)}")
    print  (f"CDF The chance that you inhale {r} molecules {binom.cdf(r, n, p)}")
n = 25.0*10**21
p = 1.0*10**-21
r = 0
# right answer = 1.388794e-11
calculate(n, p, r)