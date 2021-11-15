"""Helper functions for formatting messages, etc."""

import json
import pickle
import socket

from globalvars import LOGGER, PACKET_TERM,PACKET_HEADER,PACKET_READ_SIZE

INCOMING_BUFFER = b""

def marshal_message(message):
    """Accepts a serializable dict to convert to the message format used for
    communicating between client and server. Returns a bytestring suitable to
    send over TCP."""
    return PACKET_HEADER+pickle.dumps(json.dumps(message).encode())+PACKET_TERM

def unmarshal_message(packet):
    """Accepts a bytestring packet from a socket and converts to a message dict."""
    LOGGER.debug('unstripped: %s',packet)
    message = packet.removeprefix(PACKET_HEADER).removesuffix(PACKET_TERM)
    LOGGER.debug('stripped: %s',message)
    return json.loads(pickle.loads(message))

def recv_packet(user_socket):
    """Reads a data packet from the socket, and returns the raw bytes. If
    the socket has closed (returned no data on recv), return None."""
    global INCOMING_BUFFER
    packet = b''
    packet_read = False
    while not packet_read:
        data = user_socket.recv(PACKET_READ_SIZE)
        if not data:
            user_socket.close()
            return None
        LOGGER.debug('data received: %s', data)
        INCOMING_BUFFER += data

        if PACKET_HEADER not in INCOMING_BUFFER:
            # keep reading until we find the header
            continue
        header_index = INCOMING_BUFFER.find(PACKET_HEADER)

        if PACKET_TERM not in INCOMING_BUFFER[header_index:]:
            # keep reading until we find the terminator
            continue
        term_index = INCOMING_BUFFER.find(PACKET_TERM, header_index)

        packet = INCOMING_BUFFER[header_index:term_index+len(PACKET_TERM)]
        INCOMING_BUFFER = INCOMING_BUFFER[term_index:]
        packet_read = True
    return packet

def send_packet(user_socket, packet):
    """Sends a packet to the socket."""
    user_socket.sendall(packet)
