# Basic print examples
print('Brown')
print("Toast")

# Using escape sequences
print('this is how \tit goes')  # \t adds a tab space
print("I'm going to sit \nand eat")  # \n creates a new line

# String length calculation
print(len("My dog's favourite food is fish and chips.\nI'm not a fan."))  # Fixed typo in "chisp"

# ----- String Indexing & Slicing -----

# Assign hw as a string
hw = "Hello World, today is the day"

# Checking & Printing
print(hw)

# Show the 1st element (H)
print(hw[0])

# Show the 19th element (i)
print(hw[19])

# Grab everything from index 13 to the end
print(hw[13:])

# Grab everything up to index 4 (excluding index 4)
print(hw[:4])

# Print everything
print(hw[:])

# Print last character using negative indexing
print(hw[-1])

# Grab everything except the last 4 characters
print(hw[:-4])

# Print every 2nd character (step slicing)
print(hw[::2])

# Reverse the string
print(hw[::-1])

# New string example
hw = 'abcdefghijk'

# Grab characters from index 3 to 5 (excluding index 6)
print(hw[3:6])

# ----- String Properties & Methods -----

# String concatenation
name = "Sam"
ll = name[1:]  # Extract everything except first character
print('P' + ll)  # Replacing 'S' with 'P' → "Pam"

# String modification
x = 'hello world'
x = x + " it is beautiful outside!"  # Fixed spelling

print(x)

# Repeating a character multiple times
letter = "z"
print(letter * 10)  # Prints "zzzzzzzzzz"

# String methods
print(x.upper()[::-1])  # Converts to uppercase and reverses
print(x.upper())  # Converts to uppercase
print(x.lower()[::-1])  # Converts to lowercase and reverses
print(x.lower())  # Converts to lowercase

# Splitting a string
print(x.split())  # Splits by spaces into a list of words
print(x.split('i'))  # Splits by letter 'i'




# ----- Print Formatting with Strings -----

# ----- .format() method -----
print ('This is a string {}'.format('INSERTED'))
print ('The {2} {1} {0}'.format('fox','brown','quick'))
print ('The {q} {b} {f}'.format(f='fox',b='brown',q='quick')) 

# Float formatting
result = 100/777
print ("The Result was {r:1.2f}".format(r=result))

# f-strings
name = "Jose"
print (f"Hi, his name is {name}")

name = "Zack"
age = 16
print (f"{name} is {age} years old.")





