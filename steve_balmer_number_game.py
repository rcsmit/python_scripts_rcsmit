import pandas as pd
import numpy as np
import math


import numpy as np
import matplotlib.pyplot as plt

def binary_search_steps(target, max_num):
    """Simulate binary search and return number of steps needed"""
    low, high = 1, max_num
    steps = 0
    
    while low <= high:
        steps += 1
        mid = (low + high) // 2
        
        if mid == target:
            return steps
        elif mid < target:
            low = mid + 1
        else:
            high = mid - 1
            
    return steps

def calculate_average_steps(max_num):
    """Calculate average steps for all numbers from 1 to max_num"""
    total_steps = 0
    for target in range(1, max_num + 1):
        steps = binary_search_steps(target, max_num)
        total_steps += steps
    
    return total_steps / max_num

def analyze_ranges():
    """Analyze different ranges and their average steps"""
    max_numbers = [10, 20, 50, 100, 200, 500, 1000]
    averages = []
    theoretical = []
    
    for max_num in max_numbers:
        avg_steps = calculate_average_steps(max_num)
        averages.append(avg_steps)
        # Calculate theoretical maximum (log2)
        theoretical.append(np.log2(max_num))
    
    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(max_numbers, averages, 'b-', label='Average Steps')
    plt.plot(max_numbers, theoretical, 'r--', label='Theoretical Maximum (log₂n)')
    plt.xlabel('Maximum Number')
    plt.ylabel('Number of Steps')
    plt.title('Average Binary Search Steps vs Maximum Number')
    plt.legend()
    plt.grid(True)
    
    print("\nResults:")
    print("Max Number | Average Steps | Theoretical Max (log₂n)")
    print("-" * 50)
    for i in range(len(max_numbers)):
        print(f"{max_numbers[i]:<10} | {averages[i]:.2f}        | {theoretical[i]:.2f}")
    
    return averages, theoretical


def print_game_instructions():
    """
    Print the instructions for the Steve Ballmer Number Guessing Game.
    """
    print("Welcome to the Steve Ballmer Number Guessing Game!")
    print("In this game, I will try to guess the bank number guesses.")
    print("Here are the rules:")
    print("1. The bank thinks of a number between 1 and 100.")
    print("2. I will make a guess, and the bank tells me if my guess is too high, too low, or correct.")
    print("3. I will keep guessing until I get it right.")
    print("4. The amount of money won or lost changes based on the number of tries:")
    print("   - 1 guess: I win 5 euros")
    print("   - 2 guesses: I win 4 euros")
    print("   - 3 guesses: I win 3 euros")
    print("   - 4 guesses: I win 2 euros")
    print("   - 5 guesses: I win 1 euro")
    print("   - 6 guesses: No money exchanged")
    print("   - 7 guesses: The bank wins 1 euro")
    print("   - 8 guesses: The bank wins 2 euros")
    print("   - 9 guesses: The bank wins 3 euros")
    print("   - 10 guesses: The bank wins 4 euros")
    print("   - etc")
    print("Let's get started!")

import numpy as np
import random

def binary_search_steps(target, max_num=100):
    """Simulate binary search and return number of steps needed"""
    low, high = 1, max_num
    steps = 0
    
    while low <= high:
        steps += 1
        mid = (low + high) // 2
        
        if mid == target:
            return steps
        elif mid < target:
            low = mid + 1
        else:
            high = mid - 1
            
    return steps

def random_search_steps(max_num=100, trials=1000):
    """Simulate random search and return number of steps needed"""
    steps = 0
    total_steps = 0
    for _ in range(trials):
        target = random.randint(1, max_num)
        while True:
            steps += 1
            guess = random.randint(1, max_num)
            if guess == target:
                total_steps += steps
                steps = 0
                break

    return total_steps	/ trials

def calculate_average_steps(search_function, max_num=100, trials=1000):
    """Calculate average steps for all numbers from 1 to max_num"""
    total_steps = 0
    for _ in range(trials):
        target = random.randint(1, max_num)
        steps = search_function(target, max_num)
        total_steps += steps
    
    return total_steps / trials


def compare_binary_with_random():
    average_binary_steps = calculate_average_steps(binary_search_steps, 100)
    average_random_steps = calculate_average_steps(random_search_steps, 100)
    
    print(f"Average number of steps to guess a number between 1 and 100 using binary search: {average_binary_steps:.2f}")
    print(f"Average number of steps to guess a number between 1 and 100 using random search: {average_random_steps:.2f}")

    
def collect_results(distance_factor, tolerance):
    """
    Collect the results of the game for numbers 1 to 100.
    Args:
        distance_factor (int):  The factor to determine the distance for the normal distribution.
                                0 means the game is deterministic  / predictable / not random
    
    Returns:
        list: A list of tuples containing the number and the result.
    """
    results = []
    for n in range(1, 101):
        result, guesses,number_of_tries = give_yield_one_guess(n, distance_factor, tolerance)
        results.append((n, result, guesses,number_of_tries))
    return results

def display_results(results, verbose=True):
    """
    Display the results of the game.

    Args:
        results (list): A list of tuples containing the number and the yield.
    """
    df = pd.DataFrame(results, columns=['Number', 'Yield','Number_of_tries', 'Guesses'])	
    end_result = df['Yield'].sum()
    if verbose:
        df_sorted = df.sort_values(by='Number')
        print(df_sorted.to_string())

        frequency_table = df['Yield'].value_counts().reset_index()
        frequency_table.columns = ['Yield', 'Frequency']
        print(frequency_table)

        
        if end_result > 0:
            print(f"The player wins {end_result} euros! The bank loses.")
        elif end_result < 0:
            print(f"The bank wins {abs(end_result)} euros! The player loses.")
        else:
            print("It's a tie!")
    return end_result

def give_yield_one_guess(number, distance_factor=3, tolerance =2):
    """
    Give the yield for one guess.

    Args:
        number (int): The number to guess.
        distance_factor (int):  The factor to determine the distance for the normal distribution.
                                0 means the game is deterministic  / predictable / not random
                                The higher the distance factor, the smaller the deviation from the mean.
                tolerance (int): The tolerance range for the guess. (mean plus or minus the tolerance)
    Returns:
        int: The yield based on the number of tries.
    """
    low, high = 1, 100
    tries = 1

    if number < low or number > high:
        return "Number not in range"
    guesses = []
   
    while True:
        guess = 0
        guess_mean_ =   (low + high) / 2

        if guess_mean_ == ((low + high) // 2):
            guess_mean = guess_mean_
        else:
            
            guess_mean = math.ceil((low + high) / 2)
            #guess_mean = math.floor((low + high) / 2)
           

        if distance_factor == 0:
            distance = 0  # the game is deterministic / predictable / not random
        else:
            distance = round((high - low) / distance_factor)
      
        while guess < low or guess <= guess_mean - tolerance or guess >= guess_mean + tolerance or guess > high:
            guess = int(np.random.normal(loc=guess_mean, scale=(distance/10)))
            guesses.append(guess)
            
        if guess > number:
            high = guess - 1
        elif guess < number:
            low = guess + 1
        else:
            money_scheme = [None, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -6, -7, -8, -9, -10]
            if tries > len(money_scheme) - 1:
                return money_scheme[-1],tries, guesses
            else:
                return money_scheme[tries], tries,guesses
        tries += 1

def main():
    """
    Main function to run the game.
    """
    #print_game_instructions()
    results_various_distance_factor = []
    tolerance =2
    distance_factor=0
    simulation = False
    if not simulation:
        results = collect_results(distance_factor, tolerance) 
        end_yield = display_results(results, True)   
    else:

        for distance_factor in range(0, 21):
            
            
            end_yields=[]
            for _ in range(100):
                results = collect_results(distance_factor, tolerance) 
                end_yield = display_results(results, False)
                #print (end_yield)
                end_yields.append(end_yield)
            
            average_yield = sum(end_yields) / len(end_yields)
            print (distance_factor,average_yield)
            results_various_distance_factor.append((distance_factor, average_yield))

        print (results_various_distance_factor)


if __name__ == "__main__":
    main()
    # Run the analysis
    #analyze_ranges()
