# Assign an integer value to 'a'
a = 5

print (f"a = {a}")

a = 10

print (f"a has changed to {a}")

print (f"a + a = {a + a}")

a += a  # More Pythonic than 'a = a + a'

print (f"a has changed to {a}")

# Checking class of variable
print (f"a is {type(a)}, and its value is {a}")

# Changed to float
a = 30.43

print (f"a has changed to {a}")

print (f"a is now {type(a)}, and its value is {a}")

print ("------------------------------------------------")
# Tax example

my_income = 1874

tax_rate = 0.1

my_taxes = my_income * tax_rate



# Formatting numbers in f-strings:
# The syntax {value:.Nf} controls decimal places in floats.
# - N represents the number of decimal places.
# - 'f' stands for fixed-point notation (standard decimal format).
# Examples:
#   {3.14159:.2f} → '3.14' (rounded to 2 decimal places)
#   {123.456789:.1f} → '123.5' (rounded to 1 decimal place)
#   {100.987:.0f} → '101' (no decimals, rounded)

print(f"My tax is ${my_taxes:.4f}")