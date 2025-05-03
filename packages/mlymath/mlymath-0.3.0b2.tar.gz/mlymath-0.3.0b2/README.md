#### 由mly创建的与数学有关的工具库
##### 附属模块：
- mlymath.math 数学模块
    - gcd(*nums: int) -> int: 计算多个整数的最大公约数
    - lcm(*nums: int) -> int: 计算多个整数的最小公倍数
    - is_prime(n) -> bool: 判断一个整数是否为素数
    - comb(n: int, k: int) -> int: 计算组合数 C(n, k)
    - pow(x, y): 快速计算 x 的 y 次幂
    - sha256(input_string: str) -> str: 使用 SHA-256 算法加密字符串
    - sha3_256(input_string: str) -> str: 使用 SHA3-256 算法加密字符串
    - sha3_512(input_string: str) -> str: 使用 SHA3-512 算法加密字符串
    - fib_list(n) -> list: 生成包含前 N 项的斐波那契数列
    - fib(n) -> int: 返回第 N 项的斐波那契数
    - pell_list(n) -> list: 生成包含前 N 项的佩尔数列
    - pell(n) -> int: 返回第 N 项的佩尔数
    - factor(n: int) -> list: 分解整数 n 的质因数
    - manhattan_d(point1, point2): 计算两个点之间的曼哈顿距离
    - euclidean_d(point1, point2, precision=None): 计算两个点之间的欧几里得距离，可指定小数位数
    - matrix_add(matrix1, matrix2): 计算两个矩阵的加法
    - matrix_sub(matrix1, matrix2): 计算两个矩阵的减法
    - matrix_mu(matrix1, matrix2): 计算两个矩阵的乘法
    - matrix_transpose(matrix): 计算矩阵的转置
    - matrix_scalar_mul(matrix, scalar): 计算矩阵与标量的乘法
    - list_max(nums, n): 找到数组中第 N 大的数
    - max(\*nums, n): 找到多个数中第 N 大的数, 输入n时请注意使用n = [num]
    - list_max_index(nums, n): 找到数组中第 N 大的数的索引
    - max_index(\*nums, n): 找到多个数中第 N 大的数的索引, 输入n时请注意使用n = [num]
    - list_min(nums, n): 找到数组中第 N 小的数
    - min(\*nums, n): 找到多个数中第 N 小的数, 输入n时请注意使用n = [num]
    - list_min_index(nums, n): 找到数组中第 N 小的数的索引
    - min_index(\*nums, n): 找到多个数中第 N 小的数的索引, 输入n时请注意使用n = [num]
    - math_help() -> None: 显示math帮助信息
- mlymath.RSA RSA
    - get_rsa_keys(p: int, q: int) -> Tuple[Tuple[int, int], Tuple[int, int]]: 生成 RSA 公钥和私钥
    - rsa_encrypt(public_key: Tuple[int, int], plaintext: int) -> int: 使用 RSA 公钥加密数据
    - rsa_decrypt(private_key: Tuple[int, int], ciphertext: int) -> int: 使用 RSA 私钥解密数据
    - RSA_help(): 显示帮助信息
    
- mlymath.sort 排序模块
    - quick_sort: 使用快速排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）
    - shell_sort: 使用希尔排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）
    - heap_sort: 使用堆排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）
    - bucket_sort: 使用桶排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）
    - insertion_sort: 使用插入排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）
    - bubble_sort: 使用冒泡排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）
    - merge_sort: 使用归并排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）
    - selection_sort: 使用选择排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）
    - counting_sort: 使用计数排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）
    - radix_sort: 使用基数排序算法对数组进行排序。可通过 reverse 参数控制排序顺序（默认正序）
    - sort_help: 显示可用的排序算法列表
- mlymath.morse 摩斯电码模块
	- morse(input_string): 将字符串转换为摩尔斯电码
	- unmorse(morse_code): 将摩尔斯电码转换为字符串
	- morse_help(): 打印摩尔斯电码的使用帮助信息
- mlymath.puzzle puzzle求解模块
	- solve_24_num_puzzle(board):函数用于求解 5x5 数字华容道问题
		- 参数:
			- board: 初始 5x5 矩阵，格式为二维元组，例如 ((1, 2, 3, 4, 5), (6, 7, 8, 9, 10), ...)。
		- 返回值：
			- 如果有解，则返回解决方案路径（字符串形式），例如 'UURDL'。
			- 如果无解，则返回空字符串。
	- puzzle_help: puzzle_help函数用于打印可用函数的帮助信息。
- mlymath.mod 整除特征模块
	-  mod2(n): 判断 n 是否能被 2 整除。
	- mod3(n): 判断 n 是否能被 3 整除。
	- mod4(n): 判断 n 是否能被 4 整除。
	- mod5(n): 判断 n 是否能被 5 整除。
	- mod6(n): 判断 n 是否能被 6 整除。
	- mod7(n): 判断 n 是否能被 7 整除。
	- mod8(n): 判断 n 是否能被 8 整除。
	- mod9(n): 判断 n 是否能被 9 整除。
#### mly万岁！！！🎉
#### mly万岁！！！🎉
#### mly万岁！！！🎉


