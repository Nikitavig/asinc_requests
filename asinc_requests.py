import requests
from threading import Thread, BoundedSemaphore, Event
import proxy
import random
import time

# **********************
# ***** Без PROXY ******
# **********************

class ParallelParser(Thread):
	"""docstring for ParallelParser"""
	def __init__(self, url, list_):
		Thread.__init__(self)
		self.url = url
		self.list_ = list_

	def print_information(self, response):
		print(self.url, '->', response.status_code)

	def run(self):
		# response = requests.get(self.url)
		response = requests.get(self.url)
		self.list_.append({"url": self.url, "response": response})
		self.print_information(response)

		
def parallel_request(url_list, list_):
	try:
		tread_list = []
		if type(url_list) == list():

			for url in url_list:
				tread_list.append(ParallelParser(url, list_))
			
			for thread in tread_list:
				thread.start()

			for thread in tread_list:
				thread.join()
		
		else:
			raise (f"На вход должен подаваться список. Ваш тип данных: {type(url_list)}")
	except Exception as e:
		print(f"ParallelRequestExceptionError: {e}")

# *****************
# ***** PROXY *****
# *****************

class ParallelParserProxy(Thread):
	"""docstring for ParallelParser"""
	def __init__(self, url, list_):
		Thread.__init__(self)
		self.url = url
		self.list_ = list_

	def print_information(self, response):
		print(self.url, '->', response.status_code)

	def run(self):
		# response = requests.get(self.url)
		response = proxy.request_proxy(self.url)
		self.list_.append({"url": self.url, "response": response})
		self.print_information(response)


def parallel_request_proxy(url_list, list_):
	try:
		tread_list = []
		if type(url_list) == list():

			for url in url_list:
				tread_list.append(ParallelParserProxy(url, list_))
			
			for thread in tread_list:
				thread.start()

			for thread in tread_list:
				thread.join()
		
		else:
			raise (f"На вход должен подаваться список. Ваш тип данных: {type(url_list)}")
	except Exception as e:
		print(f"ParallelRequestProxyExceptionErroe: {e}")


def main():
	pass


if __name__ == '__main__':
	main()
	