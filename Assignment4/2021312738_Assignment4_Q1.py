import random

number = []
for i in range(200):
    x = random.randint(1,100)
    number.append(x)
number.sort()

arrupto20 = []
arrupto40 = []
arrupto60 = []
arrupto80 = []
arrupto100 = []
for i in range(len(number)):
    if number[i] >= 1 and number[i] <= 20:
        arrupto20.append('*')
    elif number[i] >= 21 and number[i] <= 40:
        arrupto40.append('*')
    elif number[i] >= 41 and number[i] <= 60:
        arrupto60.append('*')
    elif number[i] >= 61 and number[i] <= 80:
        arrupto80.append('*')
    elif number[i] >= 81 and number[i] <= 100:
        arrupto100.append('*')
str20 = ''.join(arrupto20)
str40 = ''.join(arrupto40)
str60 = ''.join(arrupto60)
str80 = ''.join(arrupto80)
str100 = ''.join(arrupto100)

for i in range(len(number)):
    print(f"{number[i]:4}", end="")
    if (i+1)%20 == 0:
        print() 
print("-"*80)
print(" 1 -  20: ", str20, "  ", len(arrupto20))
print("21 -  40: ", str40, "  ", len(arrupto40))
print("41 -  60: ", str60, "  ", len(arrupto60))
print("61 -  80: ", str80, "  ", len(arrupto80))
print("81 - 100: ", str100, "  ", len(arrupto100))