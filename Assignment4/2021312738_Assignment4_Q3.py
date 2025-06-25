def isPrime(n):
    if n == 1:
        return False
    for i in range(2, int(n**(1/2))+1):
        if n%i == 0:
            return False
    return True

rank = int(input("What is the prime number at rank: "))
count = 0
digit = 0
while (count < rank):
    digit += 1
    if isPrime(digit):
        count += 1
print("The prime number is", digit)