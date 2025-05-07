from random import randint, uniform, sample, shuffle, getrandbits

def randint(a, b):
    """
    返回[a,b]之间的随机整数
    a <= return <= b
    """
    return randint(a, b)  # 使用标准库实现

def randfloat(a, b):
    """
    返回[a,b]之间的随机浮点数
    a <= return <= b
    """
    # 使用标准random生成浮点数
    return a + (b - a) * (getrandbits(32) / (2**32 - 1))  # 替换randbits方法

def randlst(a, b, n):
    """
    返回[a,b]之间的n个随机整数
    """
    return [randint(a, b) for _ in range(n)]  # 使用标准randint

def randls_float(a, b, n):
    """
    返回[a,b]之间的n个随机浮点数
    """
    step = (b - a) / 1000  
    float_values = [a + i * step for i in range(1000)]
    # 使用标准shuffle
    shuffle(float_values)  # 替换SystemRandom().shuffle
    return float_values[:n]

def randint_notsame(a, b):
    """
    返回[a,b]之间的不重复随机整数
    a <= return <= b
    """
    try:
        return randint(a, b)  # 替换randbelow为randint
    except Exception as e:
        return f"Error: {str(e)}"

def randfloat_notsame(a, b):
    """
    返回[a,b]之间的不重复随机浮点数
    a <= return <= b
    """
    try:
        # 替换_secrets相关实现
        return uniform(a, b)  # 直接使用标准库uniform
    except ValueError:
        return "Error: Insufficient elements to generate unique random float."

def randlst_notsame(a, b, n):
    """
    返回[a,b]之间的n个不重复随机整数
    """
    try:
        population = list(range(a, b + 1))
        # 使用标准sample方法
        return sample(population, min(n, len(population)))  # 替换pop+randbelow逻辑
    except Exception as e:
        return f"Error: {str(e)}"

def randls_float_notsame(a, b, n):
    """
    返回[a,b]之间的n个不重复随机浮点数
    """
    # 简化实现
    if n > 1000:
        return f"Error: Cannot generate more than 1000 unique floats between {a} and {b}"
    
    # 使用标准库生成并打乱
    step = (b - a) / 1000  
    float_values = [a + i * step for i in range(1000)]
    shuffle(float_values)  # 替换_secrets shuffle
    return float_values[:n]

def random_help():
    """提供模块帮助信息"""
    print("以下是可用的函数:")
    print("- randint(a, b): 返回[a,b]之间的随机整数")
    print("- randfloat(a, b): 返回[a,b]之间的随机浮点数")
    print("- randlst(a, b, n): 返回[a,b]之间的n个随机整数")
    print("- randls_float(a, b, n): 返回[a,b]之间的n个随机浮点数")
    print("- randint_notsame(a, b): 返回[a,b]之间的不重复随机整数")
    print("- randfloat_notsame(a, b): 返回[a,b]之间的不重复随机浮点数")
    print("- randlst_notsame(a, b, n): 返回[a,b]之间的n个不重复随机整数")
    print("- randls_float_notsame(a, b, n): 返回[a,b]之间的n个不重复随机浮点数")
    print("- random_help(): 显示帮助信息")