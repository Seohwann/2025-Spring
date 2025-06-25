def recursivesum(n):
    if n == 1:
        return 0
    else:
        return n-1 + recursivesum(n-1)

inp = input("Insert a number n or \"Exit\": ")
if inp.isdigit():
    n = int(inp)
    result = recursivesum(n)
    print("the sum will be :", result)