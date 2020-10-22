import os,time
import socket		
import threading



BUFFER_SIZE = 1024000
REQUEST = "o"
RESPONSE = "r"
PERMANENT = "p"
TEMPORARY = "t"
NUMBER_OF_SOCKETS = 4
PACKET_FROM_SERVER= "s"
PACKET_FROM_CLIENT = "c"


HOSTING_IP = "192.168.43.204"
HOSTING_PORT = 8080


id_to_file_to_be_wrote = {}

id_to_file_to_be_read = {} 


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




def send_file(name,client,number_of_socket=NUMBER_OF_SOCKETS):
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
		y = int(input())
		send_file("file.mp4",permanent_socket,y)





def get_file_handler_to_write(data_id):
	name = id_to_file_to_be_wrote[data_id]
	if(not os.path.exists(name)):

		y = open(name,"ab+")
		print("opening\n\n\n\n\n\n\n\n\n.....")
		y.close()

	print("opening {}\n\n\n\n\n\n........".format(name))
	y= open(name, "rb+")
	return y



def handle_packet_recieving(client):

	print("Entered_handle_data_recieving")

	#recive header
	data_id = reliable_recv(client,4)
	starting_point = reliable_recv(client,8)
	file_size = reliable_recv(client, 8)




	#decode them
	data_id  = int.from_bytes(data_id, byteorder='big')
	file = get_file_handler_to_write(data_id)
	starting_point = int.from_bytes(starting_point, byteorder='big')
	print("stating point ",starting_point)
	file_size = int.from_bytes(file_size,byteorder='big')


	file.seek(starting_point)
	bytes_recived = 0

	start = time.time()
	while(bytes_recived<file_size):

		# print(bytes_recived,file_size)
		data_bytes = client.recv(BUFFER_SIZE)
		bytes_recived = bytes_recived +len(data_bytes)
		file.write(data_bytes)

	file.close()
	end = time.time()
	# print("closing {}\n\n\n\n\n\n........".format(data_id))

	client.close()

	print("time take is : ", end - start)
	print("Exited_handle_data_recieving")

def handle_packet_sending(client):

	print("Entered_handle_packet_sending")

	#reciver header
	data_id_bytes = reliable_recv(client,4)
	starting_point_bytes = reliable_recv(client,8)
	file_size_bytes = reliable_recv(client, 8)



	print("recieved id")

	data_id = int.from_bytes(data_id_bytes, byteorder='big')
	starting_point = int.from_bytes(starting_point_bytes, byteorder='big')
	file_size = int.from_bytes(file_size_bytes,byteorder='big')

	name = id_to_file_to_be_read[data_id]
	file = open(name,"rb+")
	file.seek(starting_point)


	#send header
	client.sendall(data_id_bytes)
	client.sendall(starting_point_bytes)
	client.sendall(file_size_bytes)


	start_time = time.time()
	#send file
	bytes_sent = 0
	while(bytes_sent!=file_size):
		sending_size = BUFFER_SIZE
		if(sending_size>file_size-bytes_sent):
			sending_size = file_size-bytes_sent
		read = file.read(sending_size)
		client.sendall(read)
		bytes_sent = bytes_sent +len(read)

	end_time = time.time()


	print("time_taken",end_time-start_time)		

	file.close()
	client.close()


	print("Exited_handle_packet_sending")



def handle_temporary_client(client):

	print("Entered_handle_temporary_client")


	r = reliable_recv(client,1)

	r= r.decode("utf-8")
	if(r==PACKET_FROM_CLIENT):
		threading.Thread(target=handle_packet_recieving, args=(client,)).start()

	elif(r==PACKET_FROM_SERVER):
		threading.Thread(target=handle_packet_sending, args=(client,)).start()

	else:
		print("unkonwn type of non permanent connection \n closing it")
		client.close()

	print("Exited_handle_temporary_client")







def handle_response(client):

	print("Entered_handle_response")


	global id_to_file_to_be_read
	name_size_bytes = reliable_recv(client,4)
	name_size= int.from_bytes(name_size_bytes, byteorder='big')
	name_bytes = reliable_recv(client,name_size)
	name = name_bytes.decode("utf-8")
	# while (os.path.exists(name)):
	# 	lis = name.split(".")
	# 	name = lis[0]+"1." + ".".join(lis[1:])

	# id_to_file_to_be_wrote[id_count] = name
	# id_count= id_count+1

	file_size_bytes = reliable_recv(client,8)
	data_id_bytes = reliable_recv(client,4)
	socket_numbers_bytes = reliable_recv(client,4)

	file_size= int.from_bytes(file_size_bytes, byteorder='big')
	data_id = int.from_bytes(data_id_bytes, byteorder='big')
	number_of_sockets = int.from_bytes(socket_numbers_bytes, byteorder='big')

	id_to_file_to_be_read[data_id] = name

	print("Exited_handle_response")





def handle_request(client,number_of_socket=NUMBER_OF_SOCKETS):

	print("Entered_handle_request")


	global id_to_file_to_be_wrote,id_count
	name_size_bytes = reliable_recv(client,4)
	name_size= int.from_bytes(name_size_bytes, byteorder='big')
	name_bytes = reliable_recv(client,name_size)
	name = name_bytes.decode("utf-8")
	while (os.path.exists(name)):
		lis = name.split(".")
		name = lis[0]+"1." + ".".join(lis[1:])

	id_to_file_to_be_wrote[id_count] = name
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
