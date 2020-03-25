import requests, time
from bs4 import BeautifulSoup
import os
from random import choice, shuffle
from multiprocessing import Process
import sqlite3
import random


def request_proxy(url):
	"""
	Функция для запроса через прокси сервер
	На вход получаем url ссылки для запроса

	"""

	def get_proxy_list():
		""" Функция для получения прокси адреса """

		# Подключаемся к локальной базе данных
		conn = sqlite3.connect("res/proxy.db")

		res = conn.cursor().execute(f"""SELECT adress FROM proxy_table WHERE status = '1' """).fetchall()

		# Закрытие соединения
		conn.close()

		if res:
			return [item[0] for item in res]
		else:
			False

	proxy_list = get_proxy_list()

	while True:
		if proxy_list:
			proxy = random.choice(proxy_list)
			try:
				response = requests.get(url, proxies={'https': 'https://' + proxy}, timeout=2)
				return response
			except:
				proxy_list = get_proxy_list()
				# change_status_proxy(proxy, status=0)
		else:
			print("Proxy кончились. Ждем новых proxy адресов... Пауза 20 секунд\n", end="")
			print('\r', end='')
			time.sleep(20)


def get_my_ip(proxy=False):
	"""
	Функция для получания IP адреса
	
	На вход принимает не обязательный аргемент proxy_ - прокси адрес,

	По умолчанию принимает значение False
	Если proxy_ = False - трафик не проксируется
	"""
	try:
		if proxy:
			response = requests.get('https://whoer.net/ru', proxies={'http': 'http://' + proxy, 'https': 'https://' + proxy}, timeout=2)
		else:
			requests.get('https://whoer.net/ru', timeout=1)

	except:
		return False

	if response.status_code == 200:
		return BeautifulSoup(response.text, "lxml").find('strong', attrs={'data-clipboard-target': '.your-ip'}).get_text().strip()
	else:
		return False


def get_start_proxy_list():
	"""	Функция для получения списка прокси адрестов из файла """

	error_response_text = "Your link is expired already, you can get a new one here: https://awmproxy.net/freeproxy.php"
	
	while True:
		# Читаем из файла ссылку с прокис адресами
		with open("res/url.txt", "r") as f:
			poxy_url = f.read()

		# Делаем запрос и получаем получаем страницу proxy адресов
		response = requests.get(poxy_url)


		if response.status_code == 200 and response.text != error_response_text:
			# Если ответ получен успешно - разбиваем ответ на список proxy адресов и возвращаем
			# [print(item) for item in response.text.split('\n')]
			return response.text.split('\n')
		else:
			# Если ответ веренулся с ошибкой, то поднимаем исключение
			print("Обновите ссылку прокси: https://awmproxy.com/freeproxy.php")
			poxy_url = input("Введите новую ссылку для прокси: ")

			with open("res/url.txt", "w") as f:
				f.write(poxy_url)


def proxy_list_to_db(proxy_list):
	""" Сохраняем все proxy в базу данных """

	# Подключаемся к локальной базе данных
	conn = sqlite3.connect("res/proxy.db") # или :memory: чтобы сохранить в RAM
	cursor = conn.cursor()

	# Перебиравем все адреса и проверяем есть ли они в базе,
	# если адреса в базе нет, добалвяем его
	for proxy in proxy_list:
		sql_request = f"""
						INSERT INTO proxy_table (adress)
						SELECT '{proxy}'
						WHERE NOT EXISTS (SELECT 1 FROM proxy_table WHERE adress = '{proxy}');"""
		cursor.execute(sql_request)

	# Применение изменений
	conn.commit()
	# Закрытие соединения
	conn.close()


def get_check_proxy_list():
	""" Функция для прроверки получения списка proxy адресов для проверки """

	# Подключаемся к локальной базе данных
	conn = sqlite3.connect("res/proxy.db") # или :memory: чтобы сохранить в RAM
	cursor = conn.cursor()

	res = cursor.execute(f"""SELECT adress FROM proxy_table WHERE status is Null or status = 1;""").fetchall()

	# Закрытие соединения
	conn.close()

	# Возвращаем список proxy адресов для проверки
	return [item[0] for item in res]


def change_status_proxy(proxy, status=1):
	""" Функция для изменения статуса прокси адреса """

	# Подключаемся к локальной базе данных
	conn = sqlite3.connect("res/proxy.db") # или :memory: чтобы сохранить в RAM

	conn.cursor().execute(f"""UPDATE proxy_table SET status = '{status}' WHERE adress = '{proxy}' """)

	# Применение изменений
	conn.commit()
	# Закрытие соединения
	conn.close()


def update_proxy(log=False):
	# Выгрузка всех прокси с сайта
	if log: print("\nВыгрузка всех прокси с сайта...")
	proxy_list = get_start_proxy_list()
	if log: print("Выгрузка всех прокси с сайта завершена\n")

	# Сохранение прокси в базу данных
	if log: print("Сохранение прокси в базу данных...")
	proxy_list_to_db(proxy_list)
	if log: print("Сохранение прокси в базу данных завершен\n")

	# Получение списка прокси для проверки
	if log: print("Получение списка прокси для проверки...")
	check_proxy_list = get_check_proxy_list()
	if log: print("Получение списка прокси для проверки завершено\n")


	if log: print(f"{len(check_proxy_list)} найдено адресов для проверки")

	# print("***** PROXY *****")

	if log: print("Начиенаю проверку прокси адресов\n")

	for proxy in check_proxy_list:
		res_check = get_my_ip(proxy)
		if res_check != False:
			if log: print(f"GOOD IP >>> {res_check}")
			change_status_proxy(proxy, status=1)
		else:
			# print(f"BEAD IP >>> {proxy}")
			change_status_proxy(proxy, status=0)


def get_proxy():
	""" Функция для получения прокси адреса """

	# Подключаемся к локальной базе данных
	conn = sqlite3.connect("res/proxy.db") # или :memory: чтобы сохранить в RAM

	res = conn.cursor().execute(f"""SELECT adress FROM proxy_table WHERE status = '1' """).fetchall()

	# Закрытие соединения
	conn.close()

	if res:
		return [item[0] for item in res]
	else:
		False


def main():
	start_time = time.time()

	update_proxy(log=True)

	print(f"Время выполнения скрипта: {round(time.time() - start_time, 2)} сек.")


if __name__ == '__main__':
	main()