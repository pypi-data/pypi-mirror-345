def prime_check(num):
    if num <= 1:
        print(f"{num} is not a prime number because prime numbers are greater than 1.")
        return
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            print(f"{num} is not a prime number because it is divisible by {i}.")
            return
    print(f"{num} is a prime number because it is only divisible by 1 and itself.")

def generate_fibonacci(n):
    if n <= 0:
        print("Please enter a positive integer for Fibonacci sequence.")
        return
    fib_seq = [0, 1]
    while len(fib_seq) < n:
        fib_seq.append(fib_seq[-1] + fib_seq[-2])
    print(f"The first {n} numbers of the Fibonacci sequence are: {fib_seq[:n]}")
    print("Each number is the sum of the two preceding ones, starting from 0 and 1.")

def factorial_calcu(n):
    if n < 0:
        print("Factorial is not defined for negative numbers.")
        return
    result = 1
    for i in range(2, n + 1):
        result *= i
    print(f"The factorial of {n} is {result}.")
    print(f"Factorial means multiplying all whole numbers from {n} down to 1.")

def gcd_calcu(a, b):
    original_a, original_b = a, b
    while b:
        a, b = b, a % b
    print(f"The GCD (Greatest Common Divisor) of {original_a} and {original_b} is {a}.")

def lcm_calcu(a, b):
    def gcd(x, y):
        while y:
            x, y = y, x % y
        return x

    gcd_result = gcd(a, b)
    result = abs(a * b) // gcd_result
    print(f"The LCM (Least Common Multiple) of {a} and {b} is {result}.")
    print(f"Because LCM is calculated using the formula: |{a} × {b}| / GCD({a}, {b}) = {result}")