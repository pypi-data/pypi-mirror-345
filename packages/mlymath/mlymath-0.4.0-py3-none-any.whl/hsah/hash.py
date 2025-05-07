import hashlib

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

def hash_help():
    """提供模块帮助信息"""
    print("以下是可用的函数:")
    print("- sha256(input_string: str) -> str: 使用 SHA-256 算法加密字符串")
    print("- sha3_256(input_string: str) -> str: 使用 SHA3-256 算法加密字符串")
    print("- sha3_512(input_string: str) -> str: 使用 SHA3-512 算法加密字符串")
    print("- hash_help(): 提供模块帮助信息")