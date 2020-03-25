import requests
import time
import random 
import requests
import proxy
import asinc_requests
from multiprocessing import Process

def get_url_list(n=10):
	"""
	Функция для генерации списка ссылок страниц, котороые необходимо загрузить
	На взод полчаем n - количество элементов в целевом списке 
	"""

	with open ("res/syte.txt", "r") as file:
		url_list_start = file.read().split("\n")
		return [random.choice(url_list_start) for i in range(n)]


def parallel_req(url_list, fl_proxy=False):
	""" Параллельное выполнение запросов чрезе asinc_request """

	result_list = []

	if fl_proxy:
		# Проксированный трафик
		try:
			asinc_requests.parallel_request_proxy(url_list, result_list)
		except Exception as e:
			print(f"Error: {e}")
	else:
		# Не проксированные трафик
		try:
			asinc_requests.parallel_request(url_list, result_list)
		except Exception as e:
			print(f"Error: {e}")

	for item in result_list:
		print(f"{item['response']} >>> {item['url']}")

	

def linear(url_list, fl_proxy=False):
	""" Последовательное выполнение запросов чере requests """
	if fl_proxy:
		[print(f"{index + 1}) {url} >>> {proxy.request_proxy(url).status_code}") for index, url in enumerate(url_list)]
		# [print(index + 1, ')', url, '->', proxy.request_proxy(url).status_code) for index, url in enumerate(url_list)]
	else:
		[print(f"{index + 1}) {url} >>> {requests.get(url).status_code}") for index, url in enumerate(url_list)]
		# [print(index + 1, ')', url, '->', requests.get(url).status_code) for index, url in enumerate(url_list)]


def main():
	""" Main функция для сравнения времи выполнения последовательных и параллельных запросов """

	# Получаем список ссылок для запроса
	url_list = get_url_list(3)

	start_time_linear = time.time()
	
	# Не проксирвоанный трафик
	# linear(url_list)

	# Проксирвоанный трафик
	linear(url_list, fl_proxy=True)

	end_time_linear = time.time()

	print('_______________________________________________')

	start_time_asinc = time.time()
	
	# Не проксирвоанный трафик
	# parallel_req(url_list)

	# Проксирвоанный трафик
	parallel_req(url_list, fl_proxy=True)

	end_time_asinc = time.time()

	print('Время линейного выполнения: ', end_time_linear - start_time_linear)
	print('Время параллельного выполнения: ', end_time_asinc - start_time_asinc)


if __name__ == '__main__':
	# Инициализируем процесс обновления прокси адресов
	update_proxy_p = Process(target=proxy.update_proxy, args=())
	# Инициализируем процесс проерки прокси скрипта
	main_p = Process(target=main, args=())

	# Запускаем процессы
	update_proxy_p.start()
	main_p.start()

	# Ждем завершения main_p процесса
	main_p.join()

	# Останавливаем процессы
	update_proxy_p.terminate()
	main_p.terminate()