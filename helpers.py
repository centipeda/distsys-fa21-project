"""Helper functions for formatting messages, etc."""

import json
import pickle

from globalvars import PACKET_TERM,PACKET_HEADER

def marshal_message(self, message):
    """Accepts a serializable dict to convert to the message format used for
    communicating between client and server. Returns a bytestring suitable to
    send."""
    return pickle.dumps(PACKET_HEADER+json.dumps(message)+PACKET_TERM)

def unmarshal_message(self, packet):
    """Accepts a bytestring packet to convert to a message dict."""
    message = packet.lstrip(PACKET_HEADER).rstrip(PACKET_TERM)
    return json.loads(pickle.loads(message))
    