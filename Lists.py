# Creating and modifying lists

# Initializing a list with integer values
my_list = [1,2,3]

# Reassigning the list with mixed data types (integer, string, float)
my_list = [100,"BREAD",23.2]

# Creating another list with string elements
mylist = ["one","two","three"]

# Slicing the list from index 1 onwards (excluding index 0)
print(mylist[1:])

# Creating another list with string elements
another_list = ["four","five"]

# Printing the newly created list
print(another_list)

# Concatenating two lists and printing the result
print(mylist + another_list)

# Storing the concatenated list in a new variable
new_list = mylist + another_list
print(new_list)

# Modifying an element in the list (changing first element to uppercase)
new_list[0] = "ONE"
print(new_list)

# Appending new elements to the list
new_list.append("six")
print(new_list)
new_list.append("seven")

# Removing the first element (index 0) from the list
new_list.pop(0)

# Removing the last element from the list
new_list.pop()
print(new_list)

# Sorting lists

# Initializing a list with unsorted string elements
new_list = ["a","e","x","b","q","l","r","c","d"]

# Initializing a list with unsorted numeric values (integers and floats)
num_list = [23,32.23,32.22,0.123,0.1,0.0,12,1,5,9,2,6,3]

# Printing the unsorted lists
print("\nUnsorted")
print(new_list)
print(num_list)

# Sorting both lists in ascending order
new_list.sort()
num_list.sort()

# Printing the sorted lists
print("\nSorted")
print(new_list)
print(num_list)

# Reversing the order of the sorted lists
print("\nReversed + Sorted")
new_list.reverse()
num_list.reverse()

# Printing the reversed lists
print(new_list)
print(num_list)

# Back to normal + doubling
num_list.reverse()
print("""\n----- Here we have put the list of numbers back together & printed it twice ontop of itself. -----
      Doubling is not permanent""")
print(num_list*2)
print("""\n----- Printing num_list again we can see it will only print once and not twice -----""")
print(num_list)

# ========== Nesting ==========
lst_1=[1,2,3]
lst_2=[4,5,6]
lst_3=[7,8,9]

# Make a list of lists to form a matrix
matrix = [lst_1,lst_2,lst_3]

# Show
print ("\n===== Matrix =====")
print(matrix)
# Grab each item in matrix
print ("\n===== Grab each item in matrix =====")
print (matrix[0])
print (matrix[1])
print (matrix[2])

# Grab first second & third item of the first item in the matrix object
print ("\n===== Grab first second & third item of the first item in the matrix object =====")
print (matrix[0][0])
print (matrix[0][1])
print (matrix[0][2])