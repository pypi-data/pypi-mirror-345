def mod2(n):
    return n % 10 in {0, 2, 4, 6, 8}

def mod3(n):
    return sum(int(digit) for digit in str(n)) % 3 == 0

def mod4(n):
    return n % 100 % 4 == 0

def mod5(n):
    return n % 10 in {0, 5}

def mod6(n):
    return mod2(n) and mod3(n)

def mod7(n):
    while n > 999:
        n = (n // 10) - (n % 10 * 2)
    return n % 7 == 0

def mod8(n):
    return mod2(n) and mod4(n)

def mod9(n):
    return sum(int(digit) for digit in str(n)) % 9 == 0

def mod_help():
    print("以下是可用的函数：")
    print("- mod2(n): 判断 n 是否能被 2 整除。")
    print("- mod3(n): 判断 n 是否能被 3 整除。")
    print("- mod4(n): 判断 n 是否能被 4 整除。")
    print("- mod5(n): 判断 n 是否能被 5 整除。")
    print("- mod6(n): 判断 n 是否能被 6 整除。")
    print("- mod7(n): 判断 n 是否能被 7 整除。")
    print("- mod8(n): 判断 n 是否能被 8 整除。")
    print("- mod9(n): 判断 n 是否能被 9 整除。")