"""Helper functions for formatting messages, etc."""

import json
import pickle
import socket

from globalvars import LOGGER, PACKET_TERM,PACKET_HEADER,PACKET_READ_SIZE

def marshal_message(message):
    """Accepts a serializable dict to convert to the message format used for
    communicating between client and server. Returns a bytestring suitable to
    send over TCP."""
    return PACKET_HEADER+pickle.dumps(json.dumps(message).encode())+PACKET_TERM

def unmarshal_message(packet):
    """Accepts a bytestring packet from a socket and converts to a message dict."""
    message = packet[packet.find(PACKET_HEADER)+len(PACKET_HEADER):packet.rfind(PACKET_TERM)]
    LOGGER.debug('stripped: %s',message)
    return json.loads(pickle.loads(message))

def recv_packet(user_socket):
    """Reads a data packet from the socket, and returns the raw bytes. If
    the socket has closed (returned no data on recv), return None."""
    packet = b''
    packet_read = False
    while not packet_read:
        data = user_socket.recv(PACKET_READ_SIZE)
        LOGGER.debug('data received: %s', data)
        if not data:
            user_socket.close()
            return None
        if PACKET_TERM in data:
            packet_read = True
        if PACKET_HEADER in data:
            # if we find the header in the stream, read it
            packet = data
        else:
            packet += data
    return packet

def send_packet(user_socket, packet):
    """Sends a packet to the socket."""
    user_socket.sendall(packet)
