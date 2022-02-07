# do not import anything else from loss_socket besides LossyUDP
from lossy_socket import LossyUDP
# do not import anything else from socket except INADDR_ANY
from socket import INADDR_ANY

import struct
import time

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
            packet = struct.pack('i' + str(len_data) + 's', self.send_seq_num, data_bytes[0 + i:1468 + i])

            self.socket.sendto(packet, (self.dst_ip, self.dst_port))
            self.send_seq_num += 1

    def listener(self):
        #listener function declaration

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

            data, addr = self.socket.recvfrom()
            next_packet = struct.unpack('i' + str(len(data) - 4) + 's', data)
            self.rec_buffer.append(next_packet)

    def close(self) -> None:
        """Cleans up. It should block (wait) until the Streamer is done with all
           the necessary ACKs and retransmissions"""
        # your code goes here, especially after you add ACKs and retransmissions.
        pass
