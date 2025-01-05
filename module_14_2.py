# Домашнее задание по теме "Выбор элементов и функции в SQL запросах".
# Задача "Средний баланс пользователя".

import sqlite3

# Подключение к базе данных (создание базы данных not_telegram.db)
conn = sqlite3.connect('not_telegram.db')
cursor = conn.cursor()

# Создание таблицы Users, если она еще не создана
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER,
    balance INTEGER NOT NULL
)
''')

# Заполнение таблицы 10 записями, если таблица пуста
cursor.execute('SELECT COUNT(*) FROM Users')
if cursor.fetchone()[0] == 0:
    users = [
        ('User1', 'example1@gmail.com', 10, 1000),
        ('User2', 'example2@gmail.com', 20, 1000),
        ('User3', 'example3@gmail.com', 30, 1000),
        ('User4', 'example4@gmail.com', 40, 1000),
        ('User5', 'example5@gmail.com', 50, 1000),
        ('User6', 'example6@gmail.com', 60, 1000),
        ('User7', 'example7@gmail.com', 70, 1000),
        ('User8', 'example8@gmail.com', 80, 1000),
        ('User9', 'example9@gmail.com', 90, 1000),
        ('User10', 'example10@gmail.com', 100, 1000)
    ]

    cursor.executemany('''
    INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)
    ''', users)

# Обновление balance у каждой 2-ой записи начиная с 1-ой на 500
cursor.execute('UPDATE Users SET balance = 500 WHERE id IN (1, 3, 5, 7, 9)')

# Удаление каждой 3-ей записи начиная с 1-ой
cursor.execute('DELETE FROM Users WHERE id IN (1, 4, 7, 10)')

# Удаление пользователя с id=6
cursor.execute('DELETE FROM Users WHERE id = 6')

# Подсчет общего количества записей
cursor.execute('SELECT COUNT(*) FROM Users')
total_users = cursor.fetchone()[0]

# Подсчет суммы всех балансов
cursor.execute('SELECT SUM(balance) FROM Users')
all_balances = cursor.fetchone()[0] or 0  # Защита от None

# Вывод среднего баланса с округлением до двух знаков после запятой
if total_users > 0:
    average_balance = round(all_balances / total_users, 2)
else:
    average_balance = 0.00

print(average_balance)

# Закрытие соединения
conn.close()