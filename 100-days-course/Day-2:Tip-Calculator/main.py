print("Welcome to the tip calculator!")
totalbill = input("What was the total bill?\n")
totalbill = int(totalbill[1:])
tip = int(input("How much tip would you like to give? 10, 12, or 15 percent \n"))
people = int(input("How many people would you like to split the bill with? enter numerical value \n"))
print("Each person should pay: $" + str((totalbill + (totalbill * (tip/100))) / people))

