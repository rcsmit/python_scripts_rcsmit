"""
This script calculates the probability of inhaling or ingesting a specific number of molecules 
from a given source, based on the binomial probability mass function (PMF). 

It is inspired by the concept of "Caesar's Last Breath," which explores the idea that molecules 
from historical events or sources (e.g., Caesar's last breath, a molecule of urine in the ocean) 
can eventually be distributed throughout the Earth's atmosphere or water bodies.

The script uses the `scipy.stats.binom` module to compute:
1.  The probability of inhaling exactly `r` molecules.
2.  The probability of inhaling more than `r` molecules. (So if r is 0, 
    the probability of inhaling at least 1 molecule.)

Example Scenarios:
- The chance of inhaling molecules from Caesar's last breath.
- The chance of ingesting a molecule of urine from the ocean after a long time.

Tested at # https://github.com/scipy/scipy/issues/17809#issuecomment-1386534307
Author: [Your Name]
Date: [Current Date]
"""

from scipy.stats import binom
import matplotlib.pyplot as plt
import numpy as np

def calculate(name,n, m, r, mixing_efficiency=1.0):
    """
    Calculate and print probabilities using the binomial distribution.

    Args:
        n (float): Total number of trials (e.g., total molecules in the sample).
        p (float): Probability of success for each trial (e.g., probability of a molecule being from the source).
        r (int): Number of successes (e.g., number of molecules inhaled or ingested).
        mixing_efficiency (float): Factor from 0 to 1 for how well mixed the system is.
                            Atmosphere after many years → mixing_efficiency = 0.95
                            Surface ocean after a few months → mixing_efficiency = 0.1
                            Deep ocean short term → mixing_efficiency = 0.0001
    Returns:
        None
    """
    p_base=n/m
    adjusted_p = p_base * mixing_efficiency
    print()
    print(f"Scenario: {name}, {mixing_efficiency=}")
    print(f"{n=}, {p_base=}, {adjusted_p=}, {r=}")
    print(f"The probability of inhaling exactly {r} molecules: {binom.pmf(r, n, adjusted_p):.10e}")
    print(f"The probability of inhaling more than {r} molecules: {1 - binom.cdf(r, n, adjusted_p):.3}")

   
    make_plot_mix_eff(n, r, p_base)
    find_mixing_efficiency(n, p_base, r)

def make_plot_mix_eff(n, r, p_base):
    """
    Generate a plot showing the probability of inhaling at least one molecule 
    as a function of mixing efficiency.
        n (int): The total number of trials or events.
        r (int): The number of successes or events of interest.
        p_base (float): The base probability of success for a single trial.
    Returns:
        None: This function generates and displays a plot but does not return any value.
    
    """    
    mixing_efficiencies = np.linspace(0.0001, 1, 500)
    probabilities = [1 - binom.cdf(r, n, p_base * me) for me in mixing_efficiencies]

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(mixing_efficiencies, probabilities, linewidth=2)
    plt.xlabel("Mixing Efficiency")
    plt.ylabel("P(X > 0)")
    plt.title("Probability of Inhaling at Least One Molecule vs Mixing Efficiency")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def find_mixing_efficiency(n, p_base, r, threshold=0.999):
    """
    Find the mixing efficiency where the probability of inhaling more than r molecules exceeds a threshold.
    """

    # Find the mixing efficiency where probability first exceeds the threshold
    mixing_efficiencies = np.linspace(0.0001, 1, 500)
    probabilities = [1 - binom.cdf(r, n, p_base * me) for me in mixing_efficiencies]
 
    threshold = 0.99
    mixing_efficiency_99 = next(
        (me for me, prob in zip(mixing_efficiencies, probabilities) if prob >= threshold),
        None
    )

    if mixing_efficiency_99 is not None:
        print(f"Mixing efficiency where probability first exceeds {threshold}: {mixing_efficiency_99}")
    else:
        print(f"No mixing efficiency found where probability exceeds {threshold}")

def main():
    """
    Main function to calculate probabilities for specific scenarios.

    Scenarios:
    1. The chance of ingesting a molecule of urine from the ocean after a long time.

    Returns:
        None
    """
   
    scenarios = [
        {

            # Scenario: If someone pees in the ocean, what is the chance you swallow a molecule of pee after a long time?

            "name": "Pee in the ocean",
            "n": 1.01 * 10**25,  # Number of molecules in 300 ml of urine
            "m": 4.47 * 10**47,  # Total number of molecules in the ocean
            "r": 0,
            "mixing_efficiency": 0.0001
        },
        {
            # https://www.theguardian.com/books/2017/jul/16/caesars-last-breath-sam-kean-review-decoding-the-secrets-of-the-air-around-us

            "name": "Caesar's last breath",
            "n": 25.0 * 10**21,  # Number of molecules in Caesar's last breath
            "m": 2.5 * 10**43,   # Total number of molecules in the atmosphere
            "r": 0,
            #"mixing_efficiency": 0.95
            "mixing_efficiency": 0.001
        },
        {
            # https://en.wikipedia.org/wiki/Water_distribution_on_Earth#:~:text=The%20total%20volume%20of%20water,liquid%20form%20on%20the%20surface.

            "name": "Glass of water",
            "n": 8.36 * 10**24,  # Number of molecules in 250 ml of water
            "m": 4.632 * 10**46, # Total number of water molecules on Earth
            "r": 0,
            "mixing_efficiency": 0.1
        }
    ]

    # Iterate over scenarios and calculate probabilities
    #for scenario in scenarios:
    scenario = scenarios[1]
    calculate(
        name=scenario["name"],
        n=scenario["n"],
        m=scenario["m"],
        r=scenario["r"],
        mixing_efficiency=scenario["mixing_efficiency"]
    )
       

   
if __name__ == "__main__":
    main()

