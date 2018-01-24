import socket
import datetime
from threading import Thread

#создаем сокет
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = '127.0.0.1'
PORT = 9090

#связываем сокет с нужным адресом
sock.bind((HOST, PORT))
#устанавливаем максимальное количество клиентов
sock.listen(10)


def handle_request(connection):
	''' функция для обработки входных данных конкретного соединения'''
	while True:
		data = connection.recv(1024)
		if not data:
			break
		data = data.decode("utf-8")
		print(data, datetime.datetime.now())
	connection.close()

while True:
	#ждем новых соединений
	conn, addr = sock.accept()
	#обрабатываем новое соединение в отдельном потоке
	conn_thread = Thread(target = handle_request, args = (conn,))
	conn_thread.start()
	
	
