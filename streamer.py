# do not import anything else from loss_socket besides LossyUDP
from lossy_socket import LossyUDP
# do not import anything else from socket except INADDR_ANY
from socket import INADDR_ANY

import struct


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
        self.send_buffer = dict()

        self.rec_seq_num = 0
        self.rec_buffer = dict()

    def send(self, data_bytes: bytes) -> None:
        """Note that data_bytes can be larger than one packet."""
        # Your code goes here!  The code below should be changed!
        #PART 1: completed
        #PART 2: need to add header to these packets:
        #   - add sequence number
        #   - add to send buffer

        #Strategy: keep dictionary (buffer) of packets that are sent

        #break data_bytes into multiple chunks and send each one

        for i in range(0, len(data_bytes), 1472):
            #multiple chunks of 1472 bytes
            packet = struct.pack('i' + str(len(data_bytes[0 + i:1472 + i])) + 's', self.send_seq_num, data_bytes[0 + i:1472 + i])
            self.send_buffer[self.send_seq_num] = packet
            self.rec_buffer[self.send_seq_num] = packet
            self.socket.sendto(packet, (self.dst_ip, self.dst_port))
            self.send_seq_num += 1

    def recv(self) -> bytes:
        """Blocks (waits) if no data is ready to be read from the connection."""
        # your code goes here!  The code below should be changed!
        #PART 2: must check sequence number
        #   - only receive packet if next SN
        #   - otherwise lose?
        #   - check buffer dictionary to see if correct sequence number is present
        #   - if next SN present, receive packet, otherwise wait

        print(self.rec_buffer)


        # this sample code just calls the recvfrom method on the LossySocket
        data, addr = self.socket.recvfrom()
        #if self.rec_seq_num in self.rec_buffer:
            #print("Correct SN")
        length = struct.calcsize('i'+ str(len(data)) + 's')

        print(data)
        print(len(data))
        packet = struct.unpack('i' + str(length) + 's', data)
            #self.rec_seq_num += 1
            #print(packet)
            # For now, I'll just pass the full UDP payload to the app
            #return packet[1]

        print("FUCK")
        return packet[1]


    def close(self) -> None:
        """Cleans up. It should block (wait) until the Streamer is done with all
           the necessary ACKs and retransmissions"""
        # your code goes here, especially after you add ACKs and retransmissions.
        pass
