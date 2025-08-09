import random
from colorama import Fore, Style
import time
import os

# Screen clear function
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# Generate random number between 1-1000
num = random.randint(1,1000)
tries = 0
clear_screen()
print(Fore.YELLOW+Style.BRIGHT+'\n\nWelcome to number guess 1K\n--------------------------')

# Guess till Win Loop
while True:
    # Get player's guess
    guess = int(input(Fore.LIGHTCYAN_EX+Style.NORMAL+"Guess number from 1-1000: "))
    tries += 1
    
    # Check if guess is correct
    if guess == num:
        clear_screen()
        print(f"\n\n\n-----------------------------------------")
        print(f"You win! Number was {num}. It took you {tries} tries!")
        time.sleep(5)
        break
    else:
        clear_screen()
        print(Fore.RED+'--------------------------\nTry again')
        if guess < num:
            print(Fore.WHITE+'Number is higher')
            print("-"*30)
        else:
            print(Fore.WHITE+'Number is lower')
            print("-"*30)