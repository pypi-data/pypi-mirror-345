import pyperclip
import itertools


def product_words():
    """Копирует код для генерации всех возможных комбинаций слов"""
    code = """
import itertools

alphabet = "АКРУ"  
length = 5  

combinations = [''.join(comb) for comb in itertools.product(alphabet, repeat=length)]

result = [comb for comb in combinations if 'АА' not in comb and 'У' not in comb]

for comb in result:
    print(comb)
"""
    pyperclip.copy(code)



def address_of_mask():
    """Копирует код для вычисления адреса сети и номера узла"""
    code = """
def get_network_and_host(ip_address, subnet_mask):
    # Преобразование IP-адреса и маски сети в двоичный формат
    ip_binary = ''.join([format(int(octet), '08b') for octet in ip_address.split('.')])
    subnet_binary = ''.join([format(int(octet), '08b') for octet in subnet_mask.split('.')])

    # Поразрядная конъюнкция для получения адреса сети
    network_binary = ''.join('1' if ip == '1' and subnet == '1' else '0' for ip, subnet in zip(ip_binary, subnet_binary))

    # Преобразование адреса сети обратно в десятичный формат
    network_address = '.'.join([str(int(network_binary[i:i+8], 2)) for i in range(0, 32, 8)])

    # Инвертирование маски сети
    inverted_subnet_binary = ''.join('1' if bit == '0' else '0' for bit in subnet_binary)

    # Поразрядная дизъюнкция для получения номера узла
    host_binary = ''.join('1' if ip == '1' and inverted_subnet == '1' else '0' for ip, inverted_subnet in zip(ip_binary, inverted_subnet_binary))

    # Преобразование номера узла обратно в десятичный формат
    host_address = int(host_binary, 2)

    return network_address, host_address

# Пример использования
ip_address = "192.168.108.100"
subnet_mask = "255.255.255.192"
network_address, host_address = get_network_and_host(ip_address, subnet_mask)
print(f"Адрес сети: {network_address}")
print(f"Номер узла: {host_address}")
"""
    pyperclip.copy(code)



def x_in_numbers():
    """Копирует код для нахождения x и вычисления частного"""
    code = """
def convert_to_decimal(number_str, base):
    # Переводим строку в список символов и разворачиваем его
    digits = list(number_str)
    decimal_value = 0
    power = 0

    # Проходим по символам с конца к началу
    for digit in reversed(digits):
        if digit.isdigit():
            value = int(digit)
        else:
            value = ord(digit.upper()) - ord('A') + 10

        decimal_value += value * (base ** power)
        power += 1

    return decimal_value

def find_x_and_calculate_quotient(base):
    alphabet = list(range(base))  # Цифры от 0 до base-1

    for x in alphabet:
        # Переводим числа в десятичную систему
        number1 = convert_to_decimal(f"154{x}3", base)
        number2 = convert_to_decimal(f"1{x}365", base)

        # Вычисляем сумму
        total_sum = number1 + number2

        # Проверяем делимость на 13
        if total_sum % 13 == 0:
            quotient = total_sum // 13
            return x, quotient

    return None, None

# Пример использования с base = 12
base = 12
x_value, quotient = find_x_and_calculate_quotient(base)

if x_value is not None:
    print(f"Значение x: {x_value}")
    print(f"Частное: {quotient}")
else:
    print("Не найдено значение x, при котором сумма делится на 13.")
"""
    pyperclip.copy(code)



def complement():
    """Копирует код для работы с дополнительным кодом"""
    code = """
def to_binary(number, bits):
    #Преобразует число в двоичную строку заданной разрядности.
    if number >= 0:
        return format(number, f'0{bits}b')
    else:
        return format((1 << bits) + number, f'0{bits}b')

def to_decimal(binary_str):
    #Преобразует двоичную строку в десятичное число
    return int(binary_str, 2)

def twos_complement(number, bits):
    #Вычисляет дополнительный код для заданного числа и разрядности.
    if number >= 0:
        return to_binary(number, bits)
    else:
        positive_binary = to_binary(-number, bits)
        # Инвертируем биты
        inverted_binary = ''.join('1' if bit == '0' else '0' for bit in positive_binary)
        # Прибавляем 1
        complement = to_binary(to_decimal(inverted_binary) + 1, bits)
        return complement

def add_twos_complement(num1, num2, bits):
    #Складывает два числа в дополнительном коде.
    bin1 = twos_complement(num1, bits)
    bin2 = twos_complement(num2, bits)
    result = to_binary(to_decimal(bin1) + to_decimal(bin2), bits + 1)  # +1 для учета переполнения
    # Если результат превышает разрядность, берем только младшие биты
    if result[0] == '1':
        result = result[1:]
    return result

# Примеры использования
bits = 8

# Положительное число
positive_number = 38
positive_complement = twos_complement(positive_number, bits)
print(f"Дополнительный код для {positive_number} в {bits}-битном формате: {positive_complement}")

# Отрицательное число
negative_number = -38
negative_complement = twos_complement(negative_number, bits)
print(f"Дополнительный код для {negative_number} в {bits}-битном формате: {negative_complement}")

# Сложение положительного и отрицательного числа
number1 = 7
number2 = -5
sum_result = add_twos_complement(number1, number2, bits)
print(f"Результат сложения {number1} и {number2} в {bits}-битном формате: {sum_result}")
"""
    pyperclip.copy(code)



def replacement():
    """Копирует код для замены элементов в строке"""
    code = """
s = '1' + '0' * 75
while ('10' in s) or ('1' in s):
    if '10' in s:
        s = s.replace('10', '001', 1)
    else:
        s = s.replace('1', '00', 1)
print(s.count('0'))
"""
    pyperclip.copy(code)




def file13():
    """Копирует код для работы с файлом 13.txt"""
    code = """
def readfile(filename):
    with open(f'{filename}.txt', 'r') as f:
        return [int(line.strip()) for line in f]

# Читаем данные из файла
numbers = readfile('13')

# Находим минимальное число, не кратное 15
N = min(x for x in numbers if x % 15 != 0)

# Считаем пары, где оба элемента кратны N
count = 0
max_sum = -200001  # Минимально возможная сумма для диапазона [-100000, 100000]

for i in range(len(numbers) - 1):
    a, b = numbers[i], numbers[i+1]
    if a % N == 0 and b % N == 0:
        count += 1
        current_sum = a + b
        if current_sum > max_sum:
            max_sum = current_sum

# Выводим результат
print(count, max_sum)
"""
    pyperclip.copy(code)



# ===========================
def count_system():
    """Копирует код: калькулятор систем счисления (перевод между любыми системами 2-64)"""
    code = '''
def to_decimal(number, base):
    """Перевод числа из произвольной системы счисления в десятичную."""
    number = str(number)
    if '.' in number:
        integer_part, fractional_part = number.split('.')
    else:
        integer_part, fractional_part = number, ''

    decimal_integer = 0
    for digit in integer_part:
        if digit.isdigit():
            value = int(digit)
        elif 'A' <= digit <= 'Z':
            value = ord(digit) - ord('A') + 10
        elif 'a' <= digit <= 'z':
            value = ord(digit) - ord('a') + 36
        elif digit == '+':
            value = 62
        elif digit == '/':
            value = 63
        else:
            raise ValueError(f"Недопустимый символ: {digit}")
        decimal_integer = decimal_integer * base + value

    decimal_fraction = 0
    for i, digit in enumerate(fractional_part):
        if digit.isdigit():
            value = int(digit)
        elif 'A' <= digit <= 'Z':
            value = ord(digit) - ord('A') + 10
        elif 'a' <= digit <= 'z':
            value = ord(digit) - ord('a') + 36
        elif digit == '+':
            value = 62
        elif digit == '/':
            value = 63
        else:
            raise ValueError(f"Недопустимый символ: {digit}")
        decimal_fraction += value / (base ** (i + 1))

    return decimal_integer + decimal_fraction

def from_decimal(number, base):
    """Перевод числа из десятичной системы счисления в произвольную."""
    if number == int(number):
        integer_part = int(number)
        fractional_part = 0
    else:
        integer_part = int(number)
        fractional_part = number - integer_part

    if integer_part == 0:
        integer_str = '0'
    else:
        integer_str = ''
        while integer_part > 0:
            value = integer_part % base
            if value < 10:
                integer_str = str(value) + integer_str
            elif 10 <= value < 36:
                integer_str = chr(ord('A') + value - 10) + integer_str
            elif 36 <= value < 62:
                integer_str = chr(ord('a') + value - 36) + integer_str
            elif value == 62:
                integer_str = '+' + integer_str
            elif value == 63:
                integer_str = '/' + integer_str
            integer_part //= base

    if fractional_part == 0:
        fractional_str = ''
    else:
        fractional_str = ''
        while fractional_part > 0 and len(fractional_str) < 10:
            fractional_part *= base
            value = int(fractional_part)
            if value < 10:
                fractional_str += str(value)
            elif 10 <= value < 36:
                fractional_str += chr(ord('A') + value - 10)
            elif 36 <= value < 62:
                fractional_str += chr(ord('a') + value - 36)
            elif value == 62:
                fractional_str += '+'
            elif value == 63:
                fractional_str += '/'
            fractional_part -= value

    if fractional_str:
        return integer_str + '.' + fractional_str
    else:
        return integer_str

def convert_base(number, from_base, to_base):
    """Перевод числа из одной системы счисления в другую."""
    decimal_number = to_decimal(number, from_base)
    return from_decimal(decimal_number, to_base)

# Пример использования
print("Пример перевода 101111.011 из 2-й в 16-ю систему:")
print(convert_base("101111.011", 2, 16))
'''
    pyperclip.copy(code)



def n_and_r_numbers():
    """Копирует код: нахождение максимального N при R < 35 и минимального 4-значного числа по условию"""
    code = """
# Часть 1: Нахождение максимального N при R < 35
maxi = 0

for el in range(1, 1000):
    line = bin(el)[2:]
    if line.count('1') % 2 == 0:
        r = int('10' + line[2:] + '0', 2)
    else:
        r = int('11' + line[2:] + '1', 2)

    if r < 35:
        if r >= maxi:
            maxi = el

print(maxi)

# ===========================
# Часть 2: Поиск минимального 4-значного числа по условию
m = list()

for el in range(1000, 10_000):
    el = [int(i) for i in list(str(el))]
    n1 = el[0] + el[1]
    n2 = el[1] + el[2]
    n3 = el[2] + el[3]
    new = [n1, n2, n3]
    sorted(new)
    line = str(new[1]) + str(new[2])
    if line == '1517':
        m.append(el)

print((min(m)))
    """
    pyperclip.copy(code)



# --- Инфо ---
def info():
    """Выводит список всех функций"""
    print("Доступные функции:")
    print("- product_words(): Копирует код для генерации всех возможных комбинаций слов")
    print("- address_of_mask(): Копирует код для вычисления адреса сети и номера узла")
    print("- x_in_numbers(): Копирует код для нахождения x и вычисления частного")
    print("- complement(): Копирует код для работы с дополнительным кодом")
    print("- replacement(): Копирует код для замены элементов в строке")
    print("- file13(): Копирует код для работы с файлом 13.txt") 
    print("- count_system(): Копирует код для работы с вычислением примера 13.txt")
    print("- n_and_r_numbers(): Копирует код для работы с файлом 13.txt")

