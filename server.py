"""Executable for hosting matches."""

import game
import socket
import sys
import select
import pickle
import json
import uuid
import time

from globalvars import MIN_PLAYERS, SERVER_HOST, SERVER_PORT

def main():
    # accept command-line args, including where to listen
    if len(sys.argv) != 1:
        sys.exit("Usage: server.py")

    # set up GameServer object
    game_server = game.GameServer()

    # listen on a port for users who want to start a match
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen()

    while True: # The game loop. Inside are two loops: Lobby loop and In-Game loop
        #stores the sockets of clients + server
        socket_dict = {}
        socket_dict[server] = 1

        #set up new game
        matchId = str(uuid.uuid4())
        playerList = {} # Stores players in lobby + in-game
        
        while len(playerList) < MIN_PLAYERS: # LOBBY LOOP
            # Check for readable sockets
            r_sockets, w_sockets, e_sockets = select.select(socket_dict, [], [])
            while r_sockets:
                s = r_sockets.pop()
                if(s == server):  # If the socket is the server, then accept the connection and add to dict
                    (conn, addr) = s.accept()
                    socket_dict[conn] = 1
                else:  # If the socket is a client, handle a single request
                    try:
                        data = []
                        while True:
                            packet = s.recv(4096)
                            if not packet:
                                s.close()
                                del(socket_dict[s])
                                break
                            data.append(packet)
                            if packet.endswith(b'\0'):
                                break
                        request_data = pickle.loads(b''.join(data))
                        response = {}
                        try: # Handle request, expect JOINMATCH
                            if request_data == 'JOIN_MATCH':
                                print("JOINMATCH",s)
                                userId = str(uuid.uuid4()) # Generate unique ID for user
                                playerList[userId] = s
                                
                                response = json.dumps({"method": "MATCH_JOINED", "user_id": userId, "match_id": matchId})
                            else: # Trash was sent, ignore then
                                pass
                        except Exception:
                            pass
                        s.sendall(pickle.dumps(json.dumps(response))+b'\0')
                    except: # If something with request goes wrong, remove from player_dicts
                        try:
                            s.close()
                            del(socket_dict[s])
                        except:
                            continue

        # when enough users connect, start a match
        print("STARTING GAME IN... ")
        for sec in range(5, 0, -1):
            time.sleep(1)
            print(str(sec)+"... ")
        
        # while the match is not over:
        #     get inputs from each user
        #     relay inputs to each other user
        #     update the game state according to the inputs
        #     check if the match is over
        pass

if __name__ == "__main__":
    main()