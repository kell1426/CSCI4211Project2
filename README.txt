CSCI4211 Project2
Daniel Kelly
kell1426
4718021

The compilation of my program follows what is given in the guidlines. First the netowrk layer is initialized, then the server is initialized, and finally the client is initialized. My program is broken up into two sections. The client code and the server code.

The client code first checks the number of arguments to make sure it is the client code that should be run. The socket is set up, then the file_name packet is created, and the packet is sent out until a succesful ACKF is received signaling the server received the filename correctly. The next while loop is responsible for sending the data packets. First, the checksum based on the read file data is generated. The correct sequence number is set, along with the size of the data and the flag signaling the last packet. All this data is then packed into the packet and sent out of the socket. Line 95 is my implementation of the timeout for the client. It waits 5 seconds for new data to be available at the read side of the socket. If no data is there, the loop repeats and send the same packet. If there is data, the ACK is checked for the correct ACK number. If incorrect, the same packet is sent. If correct, the sequence number is toggled and the new file data is read. After all the data is sent, the file and socket is closed and some status text is printed to the terminal.

The server code first checks the number of arguments to make sure it is the server code that should be run. The socket is set up, and the filename packet is received. A new file is generated with the same filename and the ACKF is sent out. The next while loop is responsible for sending acknowledgements and writing to the file. The packet is received and parsed. The checksum of this packet is generated and the if statement in line 37 checks to make sure the correct checksum was made. This prevents mangeled packets from being used any further. Next the data is parsed out of the packet by using the size field of the packet. Next the seqno is checked to make sure this is the correct seqno the server is expecting. If it is, the ACK is sent and the data is written.

The current code for my program is almost working. I beleive that it is operating correctly on the client side, but there is some odd issue on the server side. I am unsure where the code is going wrong, but there are a few packets that are not successfully written to the file. Below are some known bugs that I found but did not have time to fix.

Current known bugs
1. There is an error with casting a character to an int for a mangled packet (since it could be a non-int character). I need to calculate the checksum to see if the packet is mangled, so I need the size of the data. But to get the correct size of the data, I need to know if the checksum is correct (non-mangled packet). With these two things I need, each one needs to come before the other which has created a circular dependency. I ran out of time to implement a fully working solution, so I modified the condidtion check to allow the last packet through always.

2. I currently do not have a checksum in place for the packet that sends the file name. It will send this filename_packet until the server receives it, but if it gets mangled the program will crash because of the incorrect filename format.
