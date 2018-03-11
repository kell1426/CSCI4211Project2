

# server.py
import sys
import socket                   # Import socket module
import struct

port = int(sys.argv[1])                # Reserve a port for your service.
s = socket.socket()             # Create a socket object
host = sys.argv[2]     # Get local machine name
s.bind((host, port))            # Bind to the port
s.listen(5)                     # Now wait for client connection.

print 'Server listening....'

while True:
    conn, addr = s.accept()     # Establish connection with client.
    print 'Got connection from', addr
    #filename = conn.recv(512)
    #print('Server received', filename)
    filename = "Test.txt"
    f = open(filename,'wb')
    while True:
       packet = conn.recv(512)
       checksum = packet[0:20]
       seqno = packet[20:21]
       size = packet[21:24]
       last = packet[24:25]
       if size == '487':
            data = packet[25:]
       else:
           hun = int(packet[21], 16) * 100
           ten = int(packet[22], 16) * 10
           one = int(packet[23], 16)
           sizeint = hun + ten + one
           data = packet[25:(25 + sizeint)]
       f.write(data)
       ack = 'ACK'
       ACK_packet = struct.pack('3sc508x', ack, seqno)
       conn.send(ACK_packet)
       if size != '487':
           break

    f.close()
    print('Successfully received the file')
    conn.send('Thank you for connecting')
    conn.close()

# client.py
import struct
import socket                   # Import socket module
import sys
s = socket.socket()             # Create a socket object
host = sys.argv[2]     # Get local machine name
port = int(sys.argv[1])                   # Reserve a port for your service.

s.connect((host, port))
#s.send(sys.argv[3])
f = open(sys.argv[3], 'rb')
l = f.read(487)
seqcount = 0
last = 'N'
while(l and last == 'N'):
    checksum = "01234567890123456789"
    if seqcount == 0:
        seqno = '0'
    else:
        seqno = '1'
    if len(l) == 487:
            size = '487'
            last = 'N'
    else:
        size = str(len(l))
        last = 'Y'
    packet = struct.pack('20sc3sc487s', checksum, seqno, size, last, l)
    s.send(packet)
    ACK = s.recv(512)
    print(ACK[0:5])
    seqcount = (seqcount + 1) % 2
    l = f.read(487)

f.close()
print('Successfully sent the file')
s.shutdown(socket.SHUT_WR)
print s.recv(512)
s.close()
print('connection closed')
