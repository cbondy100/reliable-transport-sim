# do not import anything else from loss_socket besides LossyUDP
from lossy_socket import LossyUDP
# do not import anything else from socket except INADDR_ANY
from socket import INADDR_ANY


class Streamer:
    def __init__(self, dst_ip, dst_port,
                 src_ip=INADDR_ANY, src_port=0):
        """Default values listen on all network interfaces, chooses a random source port,
           and does not introduce any simulated packet loss."""
        self.socket = LossyUDP()
        self.socket.bind((src_ip, src_port))
        self.dst_ip = dst_ip
        self.dst_port = dst_port

    def send(self, data_bytes: bytes) -> None:
        """Note that data_bytes can be larger than one packet."""
        # Your code goes here!  The code below should be changed!

        #print(data_bytes[0:1472])
        #break data_bytes into multiple chunks and send each one
        packetList = []
        for i in range(0, len(data_bytes), 1472):
            self.socket.sendto(data_bytes[0+i:1472+i], (self.dst_ip, self.dst_port))

        #print("PACKET LIST")
        #print(packetList)
        #for p in packetList:
            #print(p)
        #for packet in packetList:
        #    self.socket.sendto(packet, (self.dst_ip, self.dst_port))


        # for now I'm just sending the raw application-level data in one UDP payload
        #self.socket.sendto(data_bytes[0:1472], (self.dst_ip, self.dst_port))

    def recv(self) -> bytes:
        """Blocks (waits) if no data is ready to be read from the connection."""
        # your code goes here!  The code below should be changed!
        
        # this sample code just calls the recvfrom method on the LossySocket
        data, addr = self.socket.recvfrom()
        # For now, I'll just pass the full UDP payload to the app
        return data

    def close(self) -> None:
        """Cleans up. It should block (wait) until the Streamer is done with all
           the necessary ACKs and retransmissions"""
        # your code goes here, especially after you add ACKs and retransmissions.
        pass
