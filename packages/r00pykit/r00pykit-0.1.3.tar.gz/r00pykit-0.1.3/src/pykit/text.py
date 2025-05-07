import re
from typing import List


def is_ipv4_addres(text) -> bool:
    """
    Проверяет, является ли строка IPv4-адресом.

    :param text: строка для проверки
    :return:
    """
    match = re.search(r'\b(?:(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.){3}(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\b', text)
    if match:
        return True
    return False

def find_ipv4_addresses(text: str) -> List[str]:
    """
    Находит все IPv4-адреса в тексте.

    :param text: текст для поиска
    :return: список IPv4-адресов
    """
    pattern = r'(?:(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.){3}' \
              r'(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})'
    return re.findall(pattern, text)


if __name__ == "__main__":
    print(find_ipv4_addresses("ff01f41192.168.0.1113fff"))
