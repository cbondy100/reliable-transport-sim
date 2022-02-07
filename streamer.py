# do not import anything else from loss_socket besides LossyUDP
from concurrent.futures import ThreadPoolExecutor

from lossy_socket import LossyUDP
# do not import anything else from socket except INADDR_ANY
from socket import INADDR_ANY

import hashlib
import struct
import time

# HEADER INFO: (Sequence number, data, acknowledgement(no_ack (0) , ack (1), or fin (2)) )
# Updated Header structure: (SN, ack (0 or 1), fin (0 or 1), data)
# this way we only have to pack consistent with one struct

class Streamer:
    def __init__(self, dst_ip, dst_port,
                 src_ip=INADDR_ANY, src_port=0):
        """Default values listen on all network interfaces, chooses a random source port,
           and does not introduce any simulated packet loss."""
        self.socket = LossyUDP()
        self.socket.bind((src_ip, src_port))
        self.dst_ip = dst_ip
        self.dst_port = dst_port

        self.send_seq_num = 0
        self.rec_seq_num = 0
        self.rec_buffer = []

        #keep list of ACK packets
        self.ack_list = []
        self.closed = False

        # Start a new asynchronous thread with 'listener()' function
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.executor.submit(self.listener)


    def send(self, data_bytes: bytes) -> None:
        """Note that data_bytes can be larger than one packet."""
        # Your code goes here!  The code below should be changed!
        #PART 1: completed
        #PART 2: need to add header to these packets:
        #   - add sequence number
        #   - add to send buffer

        #Strategy: keep list (buffer) of packets that are sent

        #break data_bytes into multiple chunks and send each one

        for i in range(0, len(data_bytes), 1444):
            #multiple chunks of 1472 bytes (account for 28 byte buffer)
            len_data = len(data_bytes[0+i:1444+i])
            hash_data = self.GetHash(data_bytes) # generate hash from helper function GetHash() -> put in header
            packet = struct.pack('iii' + str(len_data) + 's' + '16s', self.send_seq_num, 0, 0, data_bytes[0 + i:1444 + i], hash_data)
            self.socket.sendto(packet, (self.dst_ip, self.dst_port))

            # Wait for acknowledgement every 0.01 secs
            timeout = 25
            curr_time = 0
            while self.send_seq_num not in self.ack_list:
                #this runs while sent SN is not part of ACK list
                if curr_time == timeout:
                    #if no ACK after .25s send again
                    self.socket.sendto(packet, (self.dst_ip, self.dst_port))
                    curr_time = 0
                time.sleep(0.01)
                curr_time += 1
            self.send_seq_num += 1


    def listener(self):
        while not self.closed:
            try:
                #get sent packet
                packet, addr = self.socket.recvfrom()
                if packet:
                    #unpack packet into fields
                    next_packet = self.unpack_packet(packet)
                    seq_num = next_packet[0]
                    ack = next_packet[1]
                    fin = next_packet[2]
                    data = next_packet[3]
                    hash_data = next_packet[4]

                    if ack == 1:
                        #this means packet was an ACK, store ACK SN in list
                        self.ack_list.append(seq_num)
                    elif fin == 1:
                        #this means packet was FIN call, send ACK
                        ack_packet = struct.pack('iii' + str(len(bytes())) + 's' + '16s', seq_num, 1, 0, bytes(), bytes())
                        self.socket.sendto(ack_packet, (self.dst_ip, self.dst_port))

                    else:
                        #packet was data, add to rec_buffer and send ACK where there is no data

                        # BEFORE we do the above step: need to check hash, if it fails, skip below code
                        # this will cause a timeout to occur and the send() function to resend packet
                        hs = self.GetHash(data)
                        if hash_data != hs:
                            continue

                        self.rec_buffer.append(next_packet)
                        ack_packet = struct.pack('iii' + str(len(bytes())) + 's' + '16s', seq_num, 1, 0, bytes(), bytes())
                        self.socket.sendto(ack_packet, (self.dst_ip, self.dst_port))

            except Exception as e:
                print("listener died!")
                print(e)

    #seperate unpacking to make it easier and only one unpack call
    #Header: (SN, ACK, FIN, DATA)
    def unpack_packet(self, packet):
        return struct.unpack('iii' + str(len(packet) - 28) + 's' + '16s', packet)

    # Uses hashlib to create an md5 hash of the packet data.
    # returns a constant 16 byte string
    def GetHash(self, data):
        byte_data = bytes(data)
        m = hashlib.md5(byte_data)
        return m.digest()

    def recv(self) -> bytes:
        """Blocks (waits) if no data is ready to be read from the connection."""
        # your code goes here!  The code below should be changed!
        #PART 2: must check sequence number
        #   - only receive packet if next SN
        #   - otherwise lose?
        #   - check buffer dictionary to see if correct sequence number is present
        #   - if next SN present, receive packet, otherwise wait

        # this sample code just calls the recvfrom method on the LossySocket
        while True:
            #loop through receive buffer
            for packet in self.rec_buffer:
                #check if seq num matches expected seq num
                if packet[0] == self.rec_seq_num:
                    # this means our expected packet has arrived
                    self.rec_seq_num += 1
                    return packet[3]


    def close(self) -> None:
        """Cleans up. It should block (wait) until the Streamer is done with all
           the necessary ACKs and retransmissions"""
        # your code goes here, especially after you add ACKs and retransmissions.

        timeout = 25
        curr_time = 0

        # Wait for acknowledgement every 0.01 secs
        while self.send_seq_num not in self.ack_list:
            #send FIN packet
            fin_packet = struct.pack('iii' + str(len(bytes())) + 's', self.send_seq_num, 0, 1, bytes())
            self.socket.sendto(fin_packet, (self.dst_ip, self.dst_port))

            #wait for ACK
            if curr_time == timeout:
                # if no ACK after .25s send again
                self.socket.sendto(fin_packet, (self.dst_ip, self.dst_port))
                curr_time = 0
            time.sleep(0.01)
            curr_time += 1

        time.sleep(2)
        self.closed = True
        self.socket.stoprecv()
        return