import os
import socket		
import threading



BUFFER_SIZE = 1024
REQUEST = "o"
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

	# print('Got connection from', addr) 


	# client.send('Thank you for connecting') 


	# client.close() 


def reliable_recv(client,size):
	u = client.recv(size)

	while(not len(u)==size):
		recv_bytes = client.recv(size-len(u))
		if(len(recv_bytes)==0):
			print("socket closed")
			return
		u = u + recv_bytes

	print("recieved :",u)
	return u


# def reliable_send(client,data):
# 	sent_bytes = client.send(data)
# 	while(len(data)!=sent_bytes):
# 		sent_bytes = sent_bytes+ client.send(data[sent_bytes:])




def send_file(name,client,number_of_socket=4):
	size  = os.path.getsize(name)

	name_size = len(name)

	file_size = os.path.getsize(name)


	client.sendall(bytes(REQUEST,"utf-8"))
	#int
	client.sendall(name_size.to_bytes(4, byteorder='big'))
	#str
	client.sendall(bytes(name,"utf-8"))

	#long long
	client.sendall(file_size.to_bytes(8, byteorder='big'))
	#id
	client.sendall(int(5).to_bytes(4, byteorder='big'))
	#number of sockets
	client.sendall((number_of_socket).to_bytes(4, byteorder='big'))

def typing():
	while(True):
		y = input()
		send_file("hand.webp",permanent_socket)





def id_to_file(data_id):
	name = file_id_mappings[data_id]
	if(not os.path.exists(name)):

		y = open(name,"ab+")
		print("opening\n\n\n\n\n\n\n\n\n.....")
		y.close()

	print("opening {}\n\n\n\n\n\n........".format(name))
	y= open(name, "rb+")
	return y



def handle_data_reciving(client):

	print("Entered_handle_data_recieving")


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
		print("loop")
		data_bytes = client.recv(BUFFER_SIZE)
		bytes_recived = bytes_recived +len(data_bytes)
		file.write(data_bytes)


	file.close()
	print("closing {}\n\n\n\n\n\n........".format(data_id))

	client.close()

	print("Exited_handle_data_recieving")

def handle_data_sending(client):

	print("Entered_handle_data_sending")


	data_id_bytes = reliable_recv(client,4)
	print("recieved id")

	data_id = int.from_bytes(data_id_bytes, byteorder='big')
	starting_point_bytes = reliable_recv(client,8)
	starting_point = int.from_bytes(starting_point_bytes, byteorder='big')
	file_size_bytes = reliable_recv(client, 8)
	file_size = int.from_bytes(file_size_bytes,byteorder='big')

	name = to_send_mappings[data_id]
	file = open(name,"rb+")
	file.seek(starting_point)

	client.sendall(data_id_bytes)
	client.sendall(starting_point_bytes)
	client.sendall(file_size_bytes)


	bytes_sent = 0
	while(bytes_sent!=file_size):
		sending_size = BUFFER_SIZE
		if(sending_size>file_size-bytes_sent):
			sending_size = file_size-bytes_sent
		read = file.read(sending_size)
		client.sendall(read)
		bytes_sent = bytes_sent +len(read)
		
	file.close()
	client.close()


	print("Exited_handle_data_sending")



def handle_temporary_client(client):

	print("Entered_handle_temporary_client")


	r = reliable_recv(client,1)

	r= r.decode("utf-8")
	if(r==DATA_FROM_CLIENT):
		threading.Thread(target=handle_data_reciving, args=(client,)).start()

	elif(r==DATA_FROM_SERVER):
		threading.Thread(target=handle_data_sending, args=(client,)).start()

	else:
		print("unkonwn type of non permanent connection \n closing it")
		client.close()

	print("Exited_handle_temporary_client")







def handle_response(client):

	print("Entered_handle_response")


	global to_send_mappings
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

	to_send_mappings[data_id] = name

	print("Exited_handle_response")





def handle_request(client,number_of_socket=4):

	print("Entered_handle_request")


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

	file_size_bytes = reliable_recv(client,8)
	data_id_bytes = reliable_recv(client,4)
	socket_numbers_bytes = reliable_recv(client,4)

	print("request came",name,file_size_bytes)
	#send the pakket
	#char
	client.sendall(bytes(RESPONSE,"utf-8"))
	#int
	client.sendall(name_size_bytes)
	#str
	client.sendall(name_bytes)

	#long long
	client.sendall(file_size_bytes)
	#id
	client.sendall((id_count-1).to_bytes(4, byteorder='big'))
	#number of sockets
	client.sendall((number_of_socket).to_bytes(4, byteorder='big'))

	print("Exited_handle_request")



def start_permanent_reciver(client):

	print("Entered_permanet_reciver")

	try:

		u = reliable_recv(client,1)
		while(u):
			
			type_of_message = u.decode("utf-8")
			if(type_of_message==REQUEST):
				handle_request(client)			
			elif(type_of_message==RESPONSE):
				handle_response(client)			
				
			else:

				print("unknown type of message : ",type_of_message)

			u = reliable_recv(client,1)

	except ConnectionResetError:
		client.close()

	print("Exited_permanet_reciver")



#first message to this funciton 
def handle_connection(client):
	print("Entered handle_connection")


	global permanent_socket
	u = reliable_recv(client,1)
	type_of_client = u.decode("utf-8")	

	if(type_of_client==PERMANENT):
		permanent_socket = client
		threading.Thread(target=start_permanent_reciver, args=(client,)).start()
		

	elif(type_of_client==TEMPORARY):
		threading.Thread(target=handle_temporary_client, args=(client,)).start()
	else:
		print("unkonwn type of connection disconnecting")
		client.close()


	print("Exited handle_connection")



while True: 

	print("while loop ")
	client, addr = s.accept()	 
	print("accepted")
	threading.Thread(target=typing,).start()

	handle_connection(client)

	# threading.Thread(target=handle_connection, args=(client,)).start()
