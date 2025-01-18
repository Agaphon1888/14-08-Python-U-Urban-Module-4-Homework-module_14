# Домашнее задание по теме "Создание БД, добавление, выбор и удаление элементов."
# Задача "Первые пользователи".

import sqlite3
import random  # Импортируем модуль random

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

# Очистка таблицы Users
cursor.execute('DELETE FROM Users')

# Заполнение таблицы 10 записями с использованием цикла
for i in range(1, 11):
    username = f'User{i}'
    email = f'example{i}@gmail.com'
    age = random.randint(20, 99)  # Случайный возраст от 20 до 99
    balance = 1000
    cursor.execute('''
    INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)
    ''', (username, email, age, balance))

# Обновление balance у каждой 2-ой записи, включая первую
cursor.execute('UPDATE Users SET balance = 500 WHERE id % 2 = 1')

# Удаление каждой 3-ей записи, включая 1-ю
cursor.execute('DELETE FROM Users WHERE (id - 1) % 3 = 0')

# Выборка всех записей, где возраст не равен 60
cursor.execute('SELECT username, email, age, balance FROM Users WHERE age != 60')
results = cursor.fetchall()

# Вывод данных в нужном формате
for username, email, age, balance in results:
    print(f'Имя: {username} | Почта: {email} | Возраст: {age} | Баланс: {balance}')

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()