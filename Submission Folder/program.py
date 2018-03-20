# CSCI4211 Project 2
# Daniel Kelly
# kell1426
# 4718021
import sys
import socket
import struct
import hashlib
import select

# server.py
if len(sys.argv) == 3:
    s = socket.socket()
    port = int(sys.argv[1])
    host = sys.argv[2]
    s.bind((host, port))
    s.listen(5)

    print 'Server listening....'

    while True:
        conn, addr = s.accept()     # Establish connection with client.
        print 'Got connection from', addr
        #Get filename from packet and open file. Send out ACK for file packet.
        file_packet = conn.recv(512)
        filename_length = int(file_packet[0], 16)
        filename = file_packet[1:(1 + filename_length)]
        f = open(filename,'wb')
        ACKF = 'ACKF'
        ACKF_packet = struct.pack('4s508x', ACKF)
        conn.send(ACKF_packet.encode())
        expected_seqno = 0
        count = 0
        #Handle the data packets. Generate the checksum, check if its correct,
        #parse the data, check the expected_seqno, and then write the data
        #and send out the ACK.
        while True:
           #print(expected_seqno)
           packet = conn.recv(512)
           checksum = packet[0:20]
           seqno = packet[20:21]
           size = packet[21:24]
           last = packet[24:25]
           hash_object = hashlib.md5(packet[25:].encode())
           hex_checksum = hash_object.hexdigest()
           new_checksum = hex_checksum[0:20]
           if checksum == new_checksum or last == 'Y':
               if size == '487':
                    data = packet[25:]
               else:
                   hun = int(packet[21], 16) * 100
                   ten = int(packet[22], 16) * 10
                   one = int(packet[23], 16)
                   sizeint = hun + ten + one
                   data = packet[25:(25 + sizeint)]

               if expected_seqno == int(seqno) or last == 'Y':
                   ack = 'ACK'
                   f.write(data)
                   ACK_packet = struct.pack('3sc508x', ack, seqno)
                   expected_seqno = (expected_seqno + 1) % 2
                   #print('Toggling expected_seqno')
                   conn.send(ACK_packet.encode())
                   if size != '487':
                       break
               else:
                   count+=1
               if count > 5:
                   expected_seqno = (expected_seqno + 1) % 2
        f.close()
        print('Successfully received the file')
        conn.send('Thank you for connecting')
        conn.close()

#Client
if len(sys.argv) == 4:
    #Open the socket and send the filename
    s = socket.socket()
    port = int(sys.argv[1])
    host = sys.argv[2]
    s.connect((host, port))
    filename = sys.argv[3]
    file_packet = struct.pack('s511s', str(len(filename)), filename)
    f = open(sys.argv[3], 'rb')
    #repeatedly send out the filename packet until ACKF is received.
    while True:
        s.send(file_packet.encode())
        file_waiter = select.select([s], [], [], 5)
        if file_waiter[0]:
            ACKF = s.recv(512)
            if ACKF[0:4] == 'ACKF':
                break
    l = f.read(487)
    seqcount = 0
    last = 'N'
    #Generate the checksum, setup the packet, and send it.
    #Wait for the correct ACK to read next data, otherwise timeout and
    #send a duplicate packet
    while(l and last == 'N'):
        hash_object = hashlib.md5(l.encode())
        hex_checksum = hash_object.hexdigest()
        checksum = hex_checksum[0:20]
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
        s.send(packet.encode())
        ready = select.select([s], [], [], 5) #5 second timeout
        if ready[0]:
            ACK = s.recv(512)
            #print(ACK)
            if ACK[3:4] == seqno:
                seqcount = (seqcount + 1) % 2
                l = f.read(487)
                #print('Correct ACK received')
    f.close()
    print('Successfully sent the file')
    s.shutdown(socket.SHUT_WR)
    print s.recv(512)
    s.close()
    print('connection closed')
