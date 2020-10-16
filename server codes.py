import os
import socket			 

BUFFER_SIZE = 1024
REQUEST = "s"
RESPONSE = "r"
PERMANENT = "p"
TEMPORARY = "t"
DATA_FROM_SERVER= "s"
DATA_FROM_CLIENT = "c"


HOSTING_IP = "localhost"
HOSTING_PORT = 8080


file_id_mappings = {}

to_send_mappings = {} 


id_count = 0


s = socket.socket()		 
print( "Socket successfully created")
s.bind((HOSTING_IP, HOSTING_PORT))		 
print( "socket binded to %s" %(HOSTING_PORT) )
s.listen(5)	 

permanent_socket = None

print ("socket is listening")
while True: 
	client, addr = s.accept()	 
	print('Got connection from', addr) 


	client.send('Thank you for connecting') 


	client.close() 


def reliable_recv(client,size):
	u = client.recv(size)

	while(not len(u)==size):
		recv_bytes = client.recv(size-len(u))
		if(len(recv_bytes)==0):
			print("socket closed")
			return
		u = u + recv_bytes

	return u


# def reliable_send(client,data):
# 	sent_bytes = client.send(data)
# 	while(len(data)!=sent_bytes):
# 		sent_bytes = sent_bytes+ client.send(data[sent_bytes:])




def start_permanent_reciver(client):
	u = reliable_recv(client,1)
	while(u):
		
		type_of_message = u.decode("utf-8")
		if(type_of_message==REQUEST):
			handle_request(client)
		elif(type_of_message==RESPONSE):
			handle_response(client)
		else:
			print("unknown type of message")

		u = reliable_recv(client,1)


def handle_response(client):
	global file_id_mappings,id_count
	name_size_bytes = reliable_recv(client,4)
	name_size= int.from_bytes(name_size_bytes, byteorder='big')
	name_bytes = reliable_recv(client,name_size)
	name = name_bytes.decode("utf-8")
	# while (os.path.exists(name)):
	# 	lis = name.split(".")
	# 	name = lis[0]+"1." + ".".join(lis[1:])

	# file_id_mappings[id_count] = name
	# id_count= id_count+1

	file_size_bytes = reliable_recv(client,8)
	data_id_bytes = reliable_recv(client,4)
	socket_numbers_bytes = reliable_recv(client,4)

	file_size= int.from_bytes(file_size_bytes, byteorder='big')
	data_id = int.from_bytes(data_id_bytes, byteorder='big')
	number_of_sockets = int.from_bytes(socket_numbers_bytes, byteorder='big')

	to_send_mappings[data_id] = (name,file_size,number_of_sockets)




def handle_request(client,number_of_socket=4):
	global file_id_mappings,id_count
	name_size_bytes = reliable_recv(client,4)
	name_size= int.from_bytes(name_size_bytes, byteorder='big')
	name_bytes = reliable_recv(client,name_size)
	name = name_bytes.decode("utf-8")
	while (os.path.exists(name)):
		lis = name.split(".")
		name = lis[0]+"1." + ".".join(lis[1:])

	file_id_mappings[id_count] = name
	id_count= id_count+1

	file_size = reliable_recv(client,8)
	data_id = reliable_recv(client,4)
	socket_numbers = reliable_recv(client,4)


	#send the pakket
	#char
	client.sendall(RESPONSE)
	#int
	client.sendall(name_size_bytes)
	#str
	client.sendall(name_bytes)

	#long long
	client.sendall(file_size)
	#id
	client.sendall((id_count-1).to_bytes(4, byteorder='big', signed=signed))
	#number of sockets
	client.sendall((number_of_socket).to_bytes(4, byteorder='big', signed=signed))




#first message to this funciton 
def handle_connection(client):
	global permanent_socket
	u = reliable_recv(client)
	type_of_client = u.decode("utf-8")	

	if(type_of_client==PERMANENT):
		permanent_socket = client
		start_permanent_reciver(client)

	elif(type_of_client==TEMPORARY):
		handle_temporary_client(client)

	else:
		print("unkonwn type of connection disconnecting")
		client.close()



def handle_temporary_client(client):
	r = reliable_recv(client,1)
	if(r==DATA_FROM_CLIENT):
		handle_data_reciving(client)

	elif(r==DATA_FROM_SERVER):
		handle_data_sending(client)

	else:
		print("unkonwn type of non permanent connection \n closing it")
		client.close()


def id_to_file(data_id):
	name = file_id_mappings[data_id]
	y= open(name, rb+)
	return y



def handle_data_reciving(client):
	data_id = reliable_recv(client,4)
	data_id  = int.from_bytes(data_id, byteorder='big')
	file = id_to_file(data_id)
	starting_point = reliable_recv(client,8)
	starting_point = int.from_bytes(starting_point, byteorder='big')
	print("stating point ",starting_point)
	file_size = reliable_recv(client, 8)
	file_size = int.from_bytes(file_size,byteorder='big')


	file.seek(starting_point)
	bytes_recived = 0

	while(bytes_recived!=file_size):
		data_bytes = client.recv(BUFFER_SIZE)
		bytes_recived = bytes_recived +len(data_bytes)
		file.write(data_bytes)

	client.close()


def handle_data_sending(client):
	data_id_bytes = reliable_recv(client,4)
	data_id = int.from_bytes(data_id_bytes, byteorder='big')
	starting_point_bytes = reliable_recv(client,8)
	starting_point = int.from_bytes(starting_point_bytes, byteorder='big')
	file_size_bytes = reliable_recv(client, 8)
	file_size = int.from_bytes(file_size_bytes,byteorder='big')

	name = to_send_mappings(id)[0]
	y = open(name,rb+)
	y.seek(starting_point)

	client.sendall(data_id_bytes)
	client.sendall(starting_point_bytes)
	client.sendall(file_size_bytes)


	bytes_sent = 0
	while(bytes_sent!=file_size):
		read = file.read(BUFFER_SIZE)

		client.sendall(read)
		bytes_sent = bytes_sent +len(read)
		

	client.close()

