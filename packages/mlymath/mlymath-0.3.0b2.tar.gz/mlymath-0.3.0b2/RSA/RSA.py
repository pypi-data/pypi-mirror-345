import hashlib
import random
from typing import Tuple

def get_rsa_key(p: int, q: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    生成 RSA 公钥和私钥。
    :param p: 第一个大素数
    :param q: 第二个大素数
    :return: 公钥 (e, n) 和私钥 (d, n)
    """
    n = p * q
    phi = (p - 1) * (q - 1)

    def multiplicative_inverse(e: int, phi: int) -> int:
        d = 0
        x1 = 0
        x2 = 1
        y1 = 1
        temp_phi = phi
        
        while e > 0:
            temp1 = temp_phi // e
            temp2 = temp_phi - temp1 * e
            temp_phi = e
            e = temp2
            
            x = x2 - temp1 * x1
            y = d - temp1 * y1
            
            x2 = x1
            x1 = x
            d = y1
            y1 = y
        
        if temp_phi == 1:
            return d + phi

    e = random.randint(1, phi)
    while gcd(e, phi) != 1:  # 直接调用模块级 gcd 函数
        e = random.randint(1, phi)
    
    d = multiplicative_inverse(e, phi)
    return (e, n), (d, n)

def rsa_encrypt(public_key: Tuple[int, int], plaintext: int) -> int:
    """
    使用 RSA 公钥加密数据。
    :param public_key: 公钥 (e, n)
    :param plaintext: 明文数据
    :return: 密文数据
    """
    e, n = public_key
    return pow(plaintext, e, n)

def rsa_decrypt(private_key: Tuple[int, int], ciphertext: int) -> int:
    """
    使用 RSA 私钥解密数据。
    :param private_key: 私钥 (d, n)
    :param ciphertext: 密文数据
    :return: 明文数据
    """
    d, n = private_key
    return pow(ciphertext, d, n)

def RSA_help():
    """提供模块帮助信息"""
    print("以下是可用的函数:")
    print("- get_rsa_keys(p: int, q: int) -> Tuple[Tuple[int, int], Tuple[int, int]]: 生成 RSA 公钥和私钥")
    print("- rsa_encrypt(public_key: Tuple[int, int], plaintext: int) -> int: 使用 RSA 公钥加密数据")
    print("- rsa_decrypt(private_key: Tuple[int, int], ciphertext: int) -> int: 使用 RSA 私钥解密数据")
    print("- RSA_help() -> None: 显示帮助信息")

