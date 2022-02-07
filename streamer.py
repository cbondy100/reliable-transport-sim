# do not import anything else from loss_socket besides LossyUDP
from concurrent.futures import ThreadPoolExecutor

from lossy_socket import LossyUDP
# do not import anything else from socket except INADDR_ANY
from socket import INADDR_ANY

import struct
import time

# HEADER INFO: (Sequence number, data, acknowledgement(no_ack (0) , ack (1), or fin (2)) )

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

        self.ack = False
        self.closed = False

        # Start a new asynchronous thread with 'listener()' function
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(self.listener)


    def send(self, data_bytes: bytes) -> None:
        """Note that data_bytes can be larger than one packet."""
        # Your code goes here!  The code below should be changed!
        #PART 1: completed
        #PART 2: need to add header to these packets:
        #   - add sequence number
        #   - add to send buffer

        #Strategy: keep dictionary (buffer) of packets that are sent

        #break data_bytes into multiple chunks and send each one

        for i in range(0, len(data_bytes), 1468):
            #multiple chunks of 1472 bytes
            print(len(data_bytes[0+i:1468+i]))
            len_data = len(data_bytes[0+i:1468+i])
            packet = struct.pack('i' + str(len_data) + 's' + 'i', self.send_seq_num, data_bytes[0 + i:1468 + i], 1) # added '0' indicating its data

            self.socket.sendto(packet, (self.dst_ip, self.dst_port))

            # Wait for acknowledgement every 0.01 secs
            TIMEOUT = 25
            curr_time = 0
            while not self.ack:
                if curr_time == TIMEOUT:
                    self.socket.sendto(packet, (self.dst_ip, self.dst_port))
                    curr_time = 0
                time.sleep(0.01)
                curr_time += 1
            self.send_seq_num += 1

        # self.close()


    def listener(self):
        while not self.closed:
            try:
                data, addr = self.socket.recvfrom()
                # store the data in the receive buffer
                next_packet = struct.unpack('i' + str(len(data) - 4) + 's' + 'i', data)
                self.rec_buffer.append(next_packet)

                if next_packet[-1] == 1:
                    self.ack = True
                elif next_packet[-1] == 2:
                    time.sleep(2)
                    self.closed = True
                    self.socket.stoprecv()

                pkt = struct.pack('i' + str(len(data)) + 's' + 'i', self.send_seq_num, data,1)  # added '1' indicating its ACK

                self.socket.sendto(pkt, addr)

            except Exception as e:
                print("listener died!")
                print(e)

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
                    return packet[1]

            # DONT NEED THIS ANYMORE: listener() function is our new "buffer creator"
            # data, addr = self.socket.recvfrom()
            # next_packet = struct.unpack('i' + str(len(data) - 4) + 's', data)
            # self.rec_buffer.append(next_packet)

    def close(self) -> None:
        """Cleans up. It should block (wait) until the Streamer is done with all
           the necessary ACKs and retransmissions"""
        # your code goes here, especially after you add ACKs and retransmissions.

        pkt = struct.pack('ii', self.send_seq_num, 2)  # added '2' indicating its FIN

        self.socket.sendto(pkt, (self.dst_ip, self.dst_port))

        # Wait for acknowledgement every 0.01 secs
        TIMEOUT = 25
        curr_time = 0
        while not self.ack:
            if curr_time == TIMEOUT:
                self.socket.sendto(pkt, (self.dst_ip, self.dst_port))
                curr_time = 0
            time.sleep(0.01)
            curr_time += 1

        return
