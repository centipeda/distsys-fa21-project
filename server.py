"""Executable for hosting matches."""

import game
import socket
import sys
import select
import pickle
import json

def main():
    # accept command-line args, including where to listen
    if len(sys.argv) != 3:
        sys.exit("Usage: server.py HOSTNAME PORT")
    
    HOSTNAME = socket.gethostname()#sys.argv[1]
    PORT = int(sys.argv[2])

    # set up GameServer object
    game_server = game.GameServer()

    # listen on a port for users who want to start a match
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOSTNAME, PORT))
    server.listen()

    #stores the sockets from connected players
    player_dict = {}

    while True: # Think of this as the lobby loop, simply accepting players
        (conn, addr) = server.accept()
        # Check for readable sockets
        r_sockets, w_sockets, e_sockets = select.select(player_dict, [], [])
        while r_sockets:
            s = r_sockets.pop()
            if(s == server):  # If the socket is the server, then accept the connection and add to dict
                (conn, addr) = s.accept()
                player_dict[conn] = 1
            else:  # If the socket is a client, handle a single request
                try:
                    data = []
                    while True:
                        packet = s.recv(4096)
                        if not packet:
                            s.close()
                            del(player_dict[s])
                            break
                        data.append(packet)
                        if packet.endswith(b'\0'):
                            break
                    request_data = pickle.loads(b''.join(data))
                    response = {}
                    try: # Handle request, expect JOINMATCH
                        if request_data == 'JOINMATCH':
                            # TODO: Add to player list 

                            # TODO: Respond to client with info with MATCH_JOINED(user_id, match_id)

                            pass
                        pass
                    except Exception as e:
                        pass
                    s.sendall(pickle.dumps(json.dumps(response))+b'!')
                except: # If something with request goes wrong, remove from player_dicts
                    try:
                        s.close()
                        del(player_dict[s])
                    except:
                        continue

    # when enough users connect, start a match

    # while the match is not over:
    #     get inputs from each user
    #     relay inputs to each other user
    #     update the game state according to the inputs
    #     check if the match is over
    pass

if __name__ == "__main__":
    main()