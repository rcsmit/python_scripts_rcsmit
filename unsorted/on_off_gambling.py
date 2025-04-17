# https://www.facebook.com/groups/412253431572909/posts/412438721554380
# simulation of a game. Players choose ON (here A or B) or OFF. If the arrow ends on ON, the stake is doubled
# if the arrow ends on OFF, the bank gets the stake

# Easy to calculate even without coding:
# Bank always wins even without cheating. 
# Expected value for the player when bettting 1 euro: (1/4*2) + (3/4*-1) = -1/4*1 = -0.25
    
import random
import matplotlib.pyplot as plt

def roll_dice(outcomes):
    return random.choice(outcomes)

def play_game(bet_amount, multiplier):
    choice = roll_dice(['A', 'B'])
    outcome = roll_dice(['A', 'B', 'OFF', 'OFF'])
    
    if (outcome == 'OFF') and (choice == 'OFF'):
        return 'OFF', +bet_amount
    elif choice == outcome:
        return outcome, -bet_amount * multiplier
    else:
        return outcome, +bet_amount

def show_results(number_of_simulations, bank_balance, start_bank_balance, outcome_count):
    print("Outcome counts:", outcome_count)
    print (f"Bankbalance at end {bank_balance}")
    print (f"Profit = {bank_balance - start_bank_balance} ")
    print (f"Profit per game = {(bank_balance - start_bank_balance)/number_of_simulations} ")

def make_plot(number_of_simulations, balance_history):
    plt.plot(range(number_of_simulations+1), balance_history)
    plt.xlabel('Number of games played')
    plt.ylabel('Bank balance ($)')
    plt.title(f'Bank balance over  {number_of_simulations}  games')
    plt.grid(True)
    plt.show()

def main():
    number_of_simulations = 10000
    bank_balance = 1000
    start_bank_balance = bank_balance 
    multiplier = 2
    bet_amount = 100 
    balance_history = [bank_balance]
    outcome_count = {'A': 0, 'B': 0, 'OFF': 0}

    for _ in range(number_of_simulations):
        outcome, result = play_game(bet_amount, multiplier)
        bank_balance += result
        balance_history.append(bank_balance)
        outcome_count[outcome] += 1

    show_results(number_of_simulations, bank_balance, start_bank_balance, outcome_count)

    make_plot(number_of_simulations, balance_history)


if __name__ == "__main__":
    main()
