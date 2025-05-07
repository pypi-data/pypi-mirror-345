# 扩展摩尔斯电码映射表
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 
    'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', 
    '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..', 
    '9': '----.', '0': '-----', ',': '--..--', '.': '.-.-.-', '?': '..--..', 
    "'": '.----.', '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-', 
    '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-', '+': '.-.-.', 
    '-': '-....-', '_': '..--.-', '"': '.-..-.', '$': '...-..-', '@': '.--.-.',
    'Ä': '.-.-', 'Á': '.--.-', 'Å': '.--.-', 'Ch': '----', 'É': '..-..', 
    'Ñ': '--.--', 'Ö': '---.', 'Ü': '..--'
}

# 反向映射表
REVERSE_MORSE_CODE_DICT = {value: key for key, value in MORSE_CODE_DICT.items()}

def morse(input_string: str) -> str:
    """
    将字符串转换为摩尔斯电码。
    :param input_string: 输入的字符串
    :return: 转换后的摩尔斯电码（单词间用'/'分隔）
    """
    words = input_string.upper().split()
    morse_words = []
    for word in words:
        morse_word = ' '.join(MORSE_CODE_DICT[char] for char in word if char in MORSE_CODE_DICT)
        morse_words.append(morse_word)
    return '/'.join(morse_words)

def unmorse(morse_code: str) -> str:
    """
    将摩尔斯电码转换为字符串。
    :param morse_code: 输入的摩尔斯电码（单词间用'/'分隔）
    :return: 转换后的字符串
    """
    morse_words = morse_code.split('/')
    plain_words = []
    for morse_word in morse_words:
        plain_word = ''.join(REVERSE_MORSE_CODE_DICT[code] for code in morse_word.split() if code in REVERSE_MORSE_CODE_DICT)
        plain_words.append(plain_word)
    return ' '.join(plain_words)

# 新增：摩尔斯电码帮助函数
def morse_help():
    """
    打印摩尔斯电码的使用帮助信息。
    """
    print("以下是支持的字符及其对应的摩尔斯电码：")
    for char, code in MORSE_CODE_DICT.items():
        print(f"{char}: {code}")
    print("以下是可以使用的函数：")
    print("- morse(input_string): 将字符串转换为摩尔斯电码")
    print("- unmorse(morse_code): 将摩尔斯电码转换为字符串")
    print("- morse_help(): 打印摩尔斯电码的使用帮助信息")
