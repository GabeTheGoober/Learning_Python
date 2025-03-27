price_list = {'cheese':4.65, 'milk':7.25, 'bread':12.95}
price_search = input ("Want to check produce price of milk? ") 
if price_search == "yes":
    print ("Milk costs",price_list['milk'])
else:
    print ("oh")
    
w = {'k1':123, 'k2':[0,1,2], 'k3':{'k4':100}}
print (w['k3']['k4'])
print ("You have",w['k2'][2],"jars of milk")

d = {'key':['a', 'b', 'c']}
mylist = d['key'][2].upper()
letter = mylist
print (letter)

print (w.values())
print (d.keys())
print (w.keys())