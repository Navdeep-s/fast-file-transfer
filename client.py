# An example script to connect to Google using socket 
# programming in Python 

port = 8080


BUFFER_SIZE = 1024
REQUEST = "o"
RESPONSE = "r"
PERMANENT = "p"
TEMPORARY = "t"
PACKET_FROM_SERVER= "s"
PACKET_FROM_CLIENT = "c"

id_to_file_to_be_wrote={}
id_count=0
it_to_file_to_be_send={}

import socket # for socket 
import sys ,os
import threading
try: 
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	print( "Socket successfully created")
except socket.error as err: 
	print( "socket creation failed with error %s" %(err) )

# default port for socket 


# connecting to the server 
s.connect(("127.0.0.1", port)) 

print( "the socket has successfully connected to google on port == %s" %(port) )


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


def sending(s):
	s.sendall(bytes(PERMANENT,"utf-8"))

	


	while True:
		y = input()
		s.sendall(bytes(REQUEST,"utf-8"))

		name = "hand.webp"

		name_size= len(name)

		name_size_bytes = name_size.to_bytes(4, byteorder='big')
		name_bytes = bytes(name,"utf-8")
		s.sendall(name_size_bytes)
		s.sendall(name_bytes)
		s.sendall(os.path.getsize(name).to_bytes(8, byteorder='big'))
		s.sendall((30).to_bytes(4, byteorder='big'))

		s.sendall((4).to_bytes(4, byteorder='big'))



def id_to_file(data_id):
	name = it_to_file_to_be_send[data_id]
	print("opening file",name)
	y= open(name, "rb+")
	return y


def id_to_file_for_recieve(data_id):
	name = id_to_file_to_be_wrote[data_id]
	if( not os.path.exists(name)):
		y = open(name,"wb")
		y.close()
	print("opening file",name)
	y= open(name, "rb+")
	return y


def send_packet(data_id,starting_point,file_size):

	try: 
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		print( "Socket successfully created")
	except socket.error as err: 
		print( "socket creation failed with error %s" %(err) )

	# default port for socket 


	# connecting to the server 
	client.connect(("127.0.0.1", port)) 


	#send connection information
	client.sendall(bytes(TEMPORARY,"utf-8"))
	client.sendall(bytes(PACKET_FROM_CLIENT,"utf-8"))

	file = id_to_file(data_id)
	file.seek(starting_point)

	#send file headers
	client.sendall((data_id).to_bytes(4, byteorder='big'))
	client.sendall((starting_point).to_bytes(8, byteorder='big'))
	client.sendall((file_size).to_bytes(8, byteorder='big'))

	#send files
	bytes_sent = 0
	while(bytes_sent!=file_size ):
		sending_size = BUFFER_SIZE
		if(sending_size>file_size-bytes_sent):
			sending_size = file_size-bytes_sent
		read = file.read(sending_size)
		client.sendall(read)
		bytes_sent = bytes_sent +len(read)
		print("starting point {} bytes_sent {} total size{}".format(starting_point,bytes_sent,file_size))
		
	file.close()
	print("closing files................\n\n\n")
	client.close()


def recieve_packet(client):
	print("recieve_packet")



	#recieve file headers
	data_id_bytes = reliable_recv(client,4)
	starting_point_bytes = reliable_recv(client,8)
	file_size_bytes = reliable_recv(client, 8)

	#decode them
	data_id  = int.from_bytes(data_id_bytes, byteorder='big')
	file = id_to_file_for_recieve(data_id)
	starting_point = int.from_bytes(starting_point_bytes, byteorder='big')
	print("stating point ",starting_point)
	file_size = int.from_bytes(file_size_bytes,byteorder='big')


	#recive file
	file.seek(starting_point)
	bytes_recived = 0

	while(bytes_recived!=file_size):
		data_bytes = client.recv(BUFFER_SIZE)
		bytes_recived = bytes_recived +len(data_bytes)
		file.write(data_bytes)


	file.close()
	print("closing .................{}{}".format(data_id,starting_point))

	client.close()

	print("Exited_handle_data_recieving")






def send_data(number_of_sockets,data_id,file_size):
	data_length = int(file_size/number_of_sockets)
	print("file size{}\ndata_length{}".format(file_size,data_length))
	for k in range(number_of_sockets-1):
		threading.Thread(target=send_packet,args=(data_id,k*data_length,data_length),).start()

	remaining_data = file_size-data_length*(number_of_sockets-1)
	threading.Thread(target=send_packet,args=(data_id,(number_of_sockets-1)*data_length,remaining_data),).start()




def create_reciving_sockets(data_id,starting_point,file_size):
	try: 
		new_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		print( "Socket successfully created")
	except socket.error as err: 
		print( "socket creation failed with error %s" %(err) )

	# default port for socket 


	# connecting to the server 
	new_client.connect(("127.0.0.1", port)) 

	#send connection infromation
	new_client.sendall(bytes(TEMPORARY,"utf-8"))
	new_client.sendall(bytes(PACKET_FROM_SERVER,"utf-8"))

	#send iformation of the file you want to receive
	new_client.sendall((data_id).to_bytes(4, byteorder='big'))
	new_client.sendall((starting_point).to_bytes(8, byteorder='big'))
	new_client.sendall((file_size).to_bytes(8, byteorder='big'))

	#start reciveing the packet
	threading.Thread(target=recieve_packet,args=(new_client,)).start()




def handle_request(client):


	global id_to_file_to_be_wrote,id_count
	name_size_bytes = reliable_recv(client,4)
	name_size= int.from_bytes(name_size_bytes, byteorder='big')
	print("name size ",name_size)
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
	client.sendall(socket_numbers_bytes)

	number_of_sockets = int.from_bytes(socket_numbers_bytes, byteorder='big')
	file_size = int.from_bytes(file_size_bytes, byteorder='big')
	data_id = id_count-1


	#calculate the segments you want to recive with each socket and start those sockets
	data_length = int(file_size/number_of_sockets)
	print("file size{}\ndata_length{}".format(file_size,data_length))
	for k in range(number_of_sockets-1):
		threading.Thread(target=create_reciving_sockets,args=(data_id,k*data_length,data_length),).start()

	remaining_data = file_size-data_length*(number_of_sockets-1)
	threading.Thread(target=create_reciving_sockets,args=(data_id,(number_of_sockets-1)*data_length,remaining_data),).start()




	


	print("Exited_handle_request")
	

def handle_response(client):
	print("Entered_handle_response")


	global it_to_file_to_be_send
	name_size_bytes = reliable_recv(client,4)
	name_size= int.from_bytes(name_size_bytes, byteorder='big')

	name_bytes = reliable_recv(client,name_size)
	file_size_bytes = reliable_recv(client,8)
	data_id_bytes = reliable_recv(client,4)
	socket_numbers_bytes = reliable_recv(client,4)
	
	name = name_bytes.decode("utf-8")
	file_size= int.from_bytes(file_size_bytes, byteorder='big')
	data_id = int.from_bytes(data_id_bytes, byteorder='big')
	number_of_sockets = int.from_bytes(socket_numbers_bytes, byteorder='big')
	it_to_file_to_be_send[data_id] = name

	threading.Thread(target=send_data,args=(number_of_sockets,data_id,file_size,)).start()


def recieving(s):
	while True:
		try:
			k= reliable_recv(s,1)
			message_type = k.decode("utf-8")

			if(message_type==RESPONSE):
				handle_response(s)
			elif(message_type==REQUEST):
				handle_request(s)
			else:
				print("unkown type of message",message_type)
		
		except ConnectionResetError:
				s.close()


threading.Thread(target=sending,args=(s,)).start()
threading.Thread(target=recieving,args=(s,)).start()