import hashlib
import random
from typing import Tuple

def sha3_256(input_string: str) -> str:
    """
    使用 SHA3-256 算法加密字符串。
    :param input_string: 待加密的字符串
    :return: 加密后的十六进制字符串
    """
    sha3_256_hash = hashlib.sha3_256(input_string.encode()).hexdigest()
    return sha3_256_hash

def sha3_512(input_string: str) -> str:
    """
    使用 SHA3-512 算法加密字符串。
    :param input_string: 待加密的字符串
    :return: 加密后的十六进制字符串
    """
    sha3_512_hash = hashlib.sha3_512(input_string.encode()).hexdigest()
    return sha3_512_hash


def sha256(input_string: str) -> str:
    """
    使用 SHA-256 算法加密字符串。
    :param input_string: 待加密的字符串
    :return: 加密后的十六进制字符串
    """
    sha256_hash = hashlib.sha256(input_string.encode()).hexdigest()
    return sha256_hash


def gcd(*nums: int) -> int:
    """优化后：移除冗余操作"""
    from math import gcd as _gcd  # 模块级导入（关键）
    current_gcd = nums[0]
    for num in nums[1:]:
        current_gcd = _gcd(current_gcd, num)
        if current_gcd == 1:
            break
    return current_gcd  # 移除 abs（math.gcd 已返回非负数）

def lcm(*nums: int) -> int:
    """优化后：恢复 `0 in nums` 检查"""
    if 0 in nums:  # 更高效的零检查
        return 0
    current_lcm = 1
    for num in nums:
        current_lcm = current_lcm * num // gcd(current_lcm, num)
    return current_lcm

def is_prime(n):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    w = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += w
        w = 6 - w  # 在2和4之间切换，实现步长6的检查
    return True

def comb(n: int, k: int) -> int:
    """计算组合数 C(n, k)"""
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    # 使用动态规划优化组合数计算
    dp = [0] * (k + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for j in range(min(i, k), 0, -1):
            dp[j] += dp[j - 1]
    return dp[k]

def pow(x, y):
    """
    快速计算 x 的 y 次幂。
    :param x: 底数，可以是整数或浮点数
    :param y: 指数，可以是正数、负数或零
    :return: 计算结果
    """
    if y == 0:
        return 1  # 任何数的0次幂为1
    if y < 0:
        x = 1 / x  # 处理负指数
        y = -y
    result = 1
    while y > 0:
        if y % 2 == 1:  # 如果指数为奇数
            result *= x
        x *= x  # 底数平方
        y //= 2  # 指数减半
    return result

def fib_list(n: int) -> list:
    """
    生成包含前 N 项的斐波那契数列。
    :param n: 数列的项数（必须为正整数）
    :return: 包含前 N 项斐波那契数列的列表
    """
    if n <= 0:
        raise ValueError("输入必须为正整数")
    sequence = [0, 1]
    for _ in range(2, n):
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]

def fib(n: int) -> int:
    """
    返回第 N 项的斐波那契数。
    :param n: 第 N 项（必须为正整数）
    :return: 第 N 项的斐波那契数
    """
    if n <= 0:
        raise ValueError("输入必须为正整数")
    a, b = 0, 1
    for _ in range(1, n):
        a, b = b, a + b
    return a

def pell_list(n: int) -> list:
    """
    生成包含前 N 项的佩尔数列。
    :param n: 数列的项数（必须为正整数）
    :return: 包含前 N 项佩尔数列的列表
    """
    if n <= 0:
        raise ValueError("输入必须为正整数")
    sequence = [0, 1]
    for _ in range(2, n):
        sequence.append(2 * sequence[-1] + sequence[-2])
    return sequence[:n]

def pell(n: int) -> int:
    """
    返回第 N 项的佩尔数。
    :param n: 第 N 项（必须为正整数）
    :return: 第 N 项的佩尔数
    """
    if n <= 0:
        raise ValueError("输入必须为正整数")
    a, b = 0, 1
    for _ in range(1, n):
        a, b = b, 2 * b + a
    return a

def factor(n: int) -> list:
    """
    分解整数 n 的质因数。
    :param n: 待分解的整数（必须为正整数）
    :return: 包含所有质因数的列表
    """
    if n <= 0:
        raise ValueError("输入必须为正整数")
    factors = []
    # 处理2的因子
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    # 处理奇数因子
    i = 3
    while i * i <= n:
        while n % i == 0:
            factors.append(i)
            n //= i
        i += 2
    # 如果剩余的 n 是质数
    if n > 1:
        factors.append(n)
    return factors

def manhattan_d(point1, point2):
    """
    计算两个点之间的曼哈顿距离。
    :param point1: 第一个点的坐标 (list 或 tuple)
    :param point2: 第二个点的坐标 (list 或 tuple)
    :return: 曼哈顿距离
    """
    if len(point1) != len(point2):
        raise ValueError("两个点的维度必须相同")
    return sum(abs(a - b) for a, b in zip(point1, point2))

def euclidean_d(point1, point2, precision=None):
    """
    计算两个点之间的欧几里得距离。
    :param point1: 第一个点的坐标 (list 或 tuple)
    :param point2: 第二个点的坐标 (list 或 tuple)
    :param precision: 可选参数，指定结果保留的小数位数
    :return: 欧几里得距离
    """
    if len(point1) != len(point2):
        raise ValueError("两个点的维度必须相同")
    distance = (sum((a - b) ** 2 for a, b in zip(point1, point2))) ** 0.5
    return round(distance, precision) if precision is not None else distance

def matrix_add(matrix1, matrix2):
    """
    计算两个矩阵的加法。
    :param matrix1: 第一个矩阵 (二维列表)
    :param matrix2: 第二个矩阵 (二维列表)
    :return: 相加后的矩阵 (二维列表)
    """
    if len(matrix1) != len(matrix2) or any(len(row1) != len(row2) for row1, row2 in zip(matrix1, matrix2)):
        raise ValueError("两个矩阵的维度必须相同")
    return [[a + b for a, b in zip(row1, row2)] for row1, row2 in zip(matrix1, matrix2)]

def matrix_sub(matrix1, matrix2):
    """
    计算两个矩阵的减法。
    :param matrix1: 第一个矩阵 (二维列表)
    :param matrix2: 第二个矩阵 (二维列表)
    :return: 相减后的矩阵 (二维列表)
    """
    if len(matrix1) != len(matrix2) or any(len(row1) != len(row2) for row1, row2 in zip(matrix1, matrix2)):
        raise ValueError("两个矩阵的维度必须相同")
    return [[a - b for a, b in zip(row1, row2)] for row1, row2 in zip(matrix1, matrix2)]

def matrix_mul(matrix1, matrix2):
    """
    计算两个矩阵的乘法。
    :param matrix1: 第一个矩阵 (二维列表)
    :param matrix2: 第二个矩阵 (二维列表)
    :return: 相乘后的矩阵 (二维列表)
    """
    if len(matrix1[0]) != len(matrix2):
        raise ValueError("第一个矩阵的列数必须等于第二个矩阵的行数")
    result = [[0 for _ in range(len(matrix2[0]))] for _ in range(len(matrix1))]
    for i in range(len(matrix1)):
        for j in range(len(matrix2[0])):
            for k in range(len(matrix2)):
                result[i][j] += matrix1[i][k] * matrix2[k][j]
    return result

def matrix_transpose(matrix):
    """
    计算矩阵的转置。
    :param matrix: 输入矩阵 (二维列表)
    :return: 转置后的矩阵 (二维列表)
    """
    return [list(row) for row in zip(*matrix)]

def matrix_scalar_mul(matrix, scalar):
    """
    计算矩阵与标量的乘法。
    :param matrix: 输入矩阵 (二维列表)
    :param scalar: 标量值 (整数或浮点数)
    :return: 乘法结果矩阵 (二维列表)
    """
    return [[scalar * element for element in row] for row in matrix]

def list_max(nums, n):
    """
    找到数组中第 N 大的数。
    :param nums: 输入的数组 (list)
    :param n: 第 N 大的数 (int)
    :return: 第 N 大的数
    """
    if not (1 <= n <= len(nums)):
        raise ValueError("N 必须在 1 到数组长度之间")
    return sorted(nums, reverse=True)[n - 1]

def max(*nums, n):
    """
    找到多个数中第 N 大的数。
    :param nums: 输入的多个数
    :param n: 第 N 大的数 (int)
    :return: 第 N 大的数
    """
    # 修改：将 *nums 转换为列表以统一处理
    nums = list(nums)
    if not (1 <= n <= len(nums)):
        raise ValueError("N 必须在 1 到输入数的个数之间")
    return sorted(nums, reverse=True)[n - 1]

def list_max_index(nums, n):
    """
    找到数组中第 N 大的数的索引。
    :param nums: 输入的数组 (list)
    :param n: 第 N 大的数 (int)
    :return: 第 N 大的数的索引
    """
    if not (1 <= n <= len(nums)):
        raise ValueError("N 必须在 1 到数组长度之间")
    sorted_indices = sorted(range(len(nums)), key=lambda i: nums[i], reverse=True)
    return sorted_indices[n - 1]

def max_index(*nums, n):
    """
    找到多个数中第 N 大的数的索引。
    :param nums: 输入的多个数
    :param n: 第 N 大的数 (int)
    :return: 第 N 大的数的索引
    """
    if not (1 <= n <= len(nums)):
        raise ValueError("N 必须在 1 到输入数的个数之间")
    sorted_indices = sorted(range(len(nums)), key=lambda i: nums[i], reverse=True)
    return sorted_indices[n - 1]

def list_min(nums, n):
    """
    找到数组中第 N 小的数。
    :param nums: 输入的数组 (list)
    :param n: 第 N 小的数 (int)
    :return: 第 N 小的数
    """
    if not (1 <= n <= len(nums)):
        raise ValueError("N 必须在 1 到数组长度之间")
    return sorted(nums)[n - 1]

def min(*nums, n):
    """
    找到多个数中第 N 小的数。
    :param nums: 输入的多个数
    :param n: 第 N 小的数 (int)
    :return: 第 N 小的数
    """
    # 修改：将 *nums 转换为列表以统一处理
    nums = list(nums)
    if not (1 <= n <= len(nums)):
        raise ValueError("N 必须在 1 到输入数的个数之间")
    return sorted(nums)[n - 1]

def list_min_index(nums, n):
    """
    找到数组中第 N 小的数的索引。
    :param nums: 输入的数组 (list)
    :param n: 第 N 小的数 (int)
    :return: 第 N 小的数的索引
    """
    if not (1 <= n <= len(nums)):
        raise ValueError("N 必须在 1 到数组长度之间")
    sorted_indices = sorted(range(len(nums)), key=lambda i: nums[i])
    return sorted_indices[n - 1]

def min_index(*nums, n):
    """
    找到多个数中第 N 小的数的索引。
    :param nums: 输入的多个数
    :param n: 第 N 小的数 (int)
    :return: 第 N 小的数的索引
    """
    if not (1 <= n <= len(nums)):
        raise ValueError("N 必须在 1 到输入数的个数之间")
    sorted_indices = sorted(range(len(nums)), key=lambda i: nums[i])
    return sorted_indices[n - 1]

def math_help():
    """提供模块帮助信息"""
    print("以下是可用的函数:")
    print("- gcd(*nums: int) -> int: 计算多个整数的最大公约数")
    print("- lcm(*nums: int) -> int: 计算多个整数的最小公倍数")
    print("- is_prime(n) -> bool: 判断一个整数是否为素数")
    print("- comb(n: int, k: int) -> int: 计算组合数 C(n, k)")
    print("- pow(x, y): 快速计算 x 的 y 次幂")
    print("- sha256(input_string: str) -> str: 使用 SHA-256 算法加密字符串")
    print("- sha3_256(input_string: str) -> str: 使用 SHA3-256 算法加密字符串")
    print("- sha3_512(input_string: str) -> str: 使用 SHA3-512 算法加密字符串")
    print("- fib_list(n) -> list: 生成包含前 N 项的斐波那契数列")
    print("- fib(n) -> int: 返回第 N 项的斐波那契数")
    print("- pell_list(n) -> list: 生成包含前 N 项的佩尔数列")
    print("- pell(n) -> int: 返回第 N 项的佩尔数")
    print("- factor(n: int) -> list: 分解整数 n 的质因数")
    print("- manhattan_d(point1, point2): 计算两个点之间的曼哈顿距离")
    print("- euclidean_d(point1, point2, precision=None): 计算两个点之间的欧几里得距离，可指定小数位数")
    print("- matrix_add(matrix1, matrix2): 计算两个矩阵的加法")
    print("- matrix_sub(matrix1, matrix2): 计算两个矩阵的减法")
    print("- matrix_mul(matrix1, matrix2): 计算两个矩阵的乘法")
    print("- matrix_transpose(matrix): 计算矩阵的转置")
    print("- matrix_scalar_mul(matrix, scalar): 计算矩阵与标量的乘法")
    print("- list_max(nums, n): 找到数组中第 N 大的数")
    print("- max(*nums, n): 找到多个数中第 N 大的数, 输入n时请注意使用n = [num]")
    print("- list_max_index(nums, n): 找到数组中第 N 大的数的索引")
    print("- max_index(*nums, n): 找到多个数中第 N 大的数的索引, 输入n时请注意使用n = [num]")
    print("- list_min(nums, n): 找到数组中第 N 小的数")
    print("- min(*nums, n): 找到多个数中第 N 小的数, 输入n时请注意使用n = [num]")
    print("- list_min_index(nums, n): 找到数组中第 N 小的数的索引")
    print("- min_index(*nums, n): 找到多个数中第 N 小的数的索引, 输入n时请注意使用n = [num]")
    print("- get_rsa_keys(p: int, q: int) -> Tuple[Tuple[int, int], Tuple[int, int]]: 生成 RSA 公钥和私钥")
    print("- rsa_encrypt(public_key: Tuple[int, int], plaintext: int) -> int: 使用 RSA 公钥加密数据")
    print("- rsa_decrypt(private_key: Tuple[int, int], ciphertext: int) -> int: 使用 RSA 私钥解密数据")
    print("- math_help() -> None: 显示帮助信息")

