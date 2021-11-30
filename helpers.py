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
    # LOGGER.debug('unstripped: %s',packet)
    message = packet[packet.find(PACKET_HEADER)+len(PACKET_HEADER):packet.rfind(PACKET_TERM)]
    # LOGGER.debug('stripped: %s',message)
    message = json.loads(pickle.loads(message))
    # unmarshal input state
    if message['method'] == "USER_INPUT":
        if "inputs" in message:
            inputs = []
            for i in message['inputs']:
                unmarshaled_state = {
                    "user_id": i['user_id'],
                    "tick": i['tick'],
                    "input_state": {}
                }
                state = i['input_state']
                for key in state:
                    if key == "fired":
                        unmarshaled_state["input_state"][key] = state[key]
                    else:
                        unmarshaled_state["input_state"][int(key)] = state[key]
                inputs.append(unmarshaled_state)
            message['inputs'] = inputs
            return message
        elif "input_state" in message:
            unmarshaled_msg = {
                "method": "USER_INPUT",
                "user_id": message['user_id'],
                "tick": message['tick'],
                "input_state": {}
            }
            for key in message['input_state']:
                if key == "fired":
                    unmarshaled_msg["input_state"][key] = message['input_state'][key]
                else:
                    unmarshaled_msg["input_state"][int(key)] = message['input_state'][key]
            return unmarshaled_msg
    else:
        return message

def recv_data(s):
    """Receives data from the socket, adding it to the buffer."""
    global INCOMING_BUFFER
    data = s.recv(PACKET_READ_SIZE)
    if not data:
        s.close()
        return None
    # LOGGER.debug('data received: %s', data)
    INCOMING_BUFFER += data

def recv_packet(user_socket):
    """Reads a data packet from the socket, and returns the raw bytes. If
    the socket has closed (returned no data on recv), return None."""
    global INCOMING_BUFFER
    packet = b''
    packet_read = False
    while not packet_read:
        if PACKET_HEADER not in INCOMING_BUFFER:
            # keep reading until we find the header
            recv_data(user_socket)
            continue
        header_index = INCOMING_BUFFER.find(PACKET_HEADER)

        if PACKET_TERM not in INCOMING_BUFFER[header_index:]:
            # keep reading until we find the terminator
            recv_data(user_socket)
            continue
        term_index = INCOMING_BUFFER.find(PACKET_TERM, header_index)

        packet = INCOMING_BUFFER[header_index:term_index+len(PACKET_TERM)]
        INCOMING_BUFFER = INCOMING_BUFFER[term_index:]
        packet_read = True
    return packet

def send_packet(user_socket, packet):
    """Sends a packet to the socket."""
    user_socket.sendall(packet)
