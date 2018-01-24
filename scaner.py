import sys
import os
import threading
import socket
		

class FileObj:
	def __init__(self, name):
		self.name = name
		self.size = str(os.path.getsize(self.name))
		self.created = os.path.getctime(self.name)
		self.last_change = os.path.getmtime(self.name)
		
	def __str__(self):
		return self.name



class DirectoryObj:
	def __init__(self, name):
		self.name = name
		self.childs = []
		self.size = str(os.path.getsize(self.name))
		self.created = os.path.getctime(self.name)
		self.last_change = os.path.getmtime(self.name)
		self.all_files(self.name, self)
		
	def add_child(self, obj):
		self.childs.append(obj)
		
	def delete_child(self, obj):
		self.childs.remove(obj)
	
	def __str__(self):
		return self.name


	def all_files(self, path, obj):
		''' рекурсивная функция поиска всех дочерних элементов'''
		list_dir = os.listdir(path)
		for child in list_dir:
			new_path = path+'/'+child
			if os.path.isdir(new_path):
				new_obj = DirectoryObj(new_path)
				self.all_files(new_path, new_obj)
			else:
				new_obj = FileObj(new_path)
				obj.add_child(new_obj)


class MyTimer:
	def __init__(self, interval, main_folder):
		self.interval = interval
		self.path = main_folder
		self.main_folder = DirectoryObj(main_folder)
		self.changes = None
		
		
	def find_child(self, name, obj):
		''' функция поиска дочернего элемента по его имени'''
		for child in obj.childs:
			if child.name == name:
				return child
	
	def compare_changes(self, last, new):
		''' функция для сравнения старого и нового объектов'''

		#определяем список имен дочерних элементов нового объекта
		new_childs_name = [child.name for child in new.childs]
		for obj in last.childs:
			#если текущий дочерний эелемнт всё ещё существует - проверяем его, иначе возвращаем сообщение о его удалении 
			if (obj.name in new_childs_name):
				new_obj = self.find_child(obj.name, new)
				if os.path.isdir(obj.name):
					self.compare_changes(obj.name, new_obj)
				else:
					#если время последнего изменения не совпадает, отправляем сообщение об изменении
					if obj.last_change != new_obj.last_change:
						answer = "{0} - size: {1}, type change: {2}".format(new_obj.name, new_obj.size, 'modified')
						yield answer
				#удаляем текущего дочернего элемента из списка 
				new_childs_name.remove(obj.name)
				
			else:
				answer = "{0} - size: {1}, type change: {2}".format(obj.name, obj.size, 'deleted')
				yield answer
				
		#если в списке дочерних элементов ещё есть элементы, следовательно они были недавно созданы	
		if new_childs_name:
			for name in new_childs_name:
				new_obj = self.find_child(name, new)
				answer = "{0} - size: {1}, type change: {2}".format(new_obj.name, new_obj.size, 'created')
				yield answer
					
		
	
	def run(self):
		''' функция обработки изменений и передачи их на сервер'''
		new_obj = DirectoryObj(self.path)
		self.changes = list(self.compare_changes(self.main_folder, new_obj))
		if self.changes:
			sock = socket.socket()
			sock.connect(("127.0.0.1", 9090))
			for message in self.changes:
				message = message + '\n'
				sock.send(message.encode("utf-8"))
			sock.close()
		self.main_folder = new_obj
		self.start()
		
	def start(self):
		''' функция для запуска таймера'''
		timer = threading.Timer(self.interval, self.run)	
		timer.start()		

	

path = sys.argv[1]

timer = MyTimer(120, path)
timer.start()



