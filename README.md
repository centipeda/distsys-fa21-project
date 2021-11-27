# distsys-fa21-project

A distributed, real-time competitive multiplayer game.

## TODO
- Add player KO
- Add win/loss conditions

## challenges

Abstractly, the goal of this project is to maintain a highly available, consistent system where all users manipulate a shared state and can respond to each others' changes in real time. 

In terms of the CAP theorem, we have **consistency** and **availability** as our top priorities. In order for a multiplayer game to be *fair*, all players need to be able to come to the same conclusions about what exactly happens in the game, and it must not be easy for players to manipulate the game state outside of the ways possible with their normal inputs. In order for a multiplayer game to be *playable*, however, all players also need to be able to see each others' actions quickly, so they can react in turn. Ideally, all clients are fully synchronized with as small a degree of latency as possible.

## system architecture

### overview

The architecture of the system reflects this. The simplest way to make sure every user receives the same information about the game state and comes to the same conclusion about the game is to define some node as a single source of truth -- in our case, we run a server program to officiate communicating to each user the inputs of others, as well as determine win/loss conditions. The server will run its own version of the game (without rendering graphics), which will serve as the only *authoritative* version of the game -- wins and losses will be determined only by the server program.

If each client must receive every single frame of game data from the server, however, the server must communicate a large amount of data to each client at all times (60 times a second for a 60 frames-per-second game!) and all input will be delayed by the amount of latency to each client. We will implement *input scheduling* and *rollback* to attempt to remedy this.

In this approach, each client maintains a local game state that can respond instantly to input, making for highly responsive gameplay. Additionally, all game state changes will be divided into *ticks*, with each tick (possibly) corresponding to a single rendered frame and input collected only once per tick. Both the client and the server record inputs as well as the initial game state.

When input is collected from the client, it is associated with a certain tick, and is then immediately sent to the server. Since latency cannot be perfectly known, the tick the input is scheduled in may be in a past, present, or future tick relative to the server's game state. The same goes for the other clients, all of which the server relays the input to. On receiving input scheduled for a present or future tick, each client and the server can simply use the input when the game progresses to that tick. On receiving an input scheduled for a past tick, however, the client or server must *rollback* to the tick where the input was scheduled, then "re-play" the game up to the current tick again, replacing the current game state with the new one.

As a result, all clients should be able to come to the same conclusion about the game state eventually, as long as inputs from other users come in at some point. The server will act mostly to relay inputs to the other clients, as well as the single source of truth for when matches begin and end.

Some parameters will need to be tuned to ensure the system is truly functional:

* Inputs on the client side can be scheduled for a future tick by a small amount, creating a fixed input delay to account for a small amount of latency to the other clients (so that other clients receive inputs for future ticks, instead of always rolling back)
* The client may not be allowed to progress past the server's game state more than a fixed number of frames, creating a maximum client frame advantage
* Client inputs may need to be dropped if they are scheduled too far into the past to prevent cheating
* In this case, the server may need to periodically send a full game state to each client to prevent descynchronization of the clients.

### communication

To standardize communication between client/server, we must define a communication protocol. Some messages we may implement, along with their parameters:

- `JOIN_MATCH`: sent to server to request joining a match/creating a new match
- `MATCH_JOINED(user_id, match_id)`: sent to client to indicate a match has been joined, along with a match identifier to tell the server what match a user is a part of, as well as a user identifier to tell the server what inputs belong to what user.
- `INPUT(tick, user_id, inputs)`: sent to server and to clients to indicate some input has happened
- `MATCH_END(winner)`: sent to clients to indicate the match ended and who won
- `GAME_STATE(entities, tick)`: sent to clients to re-synchronize the game state and
ensure that the connection is still maintained

If these messages are JSON-encoded, they may look like this:

```
{
  "method": "GAME_STATE",
  "entities": [
    { "kind": "player", "position": [200, 300], "velocity": [-3, 4], "knockback": 32 },
    { "kind": "projectile", "position": [40, 500], "velocity": [3, 20] }
  ],
  "tick": 402
}

{
  "method": "USER_INPUT",
  "inputs": [
    {
    "input_state": {
      pygame.K_w: true, pygame.K_a: false, pygame.K_s: false, pygame.K_d: false, 'fired': true
    },
    "user_id": 3853,
    "tick": 320
    },
    ...
  ]
}
```

### code organization

Most of the code is currently organized into classes:
- The `GameEngine` class manages the game state, recorded inputs, and rolling back to account for old inputs.
- The `GameClient` and `GameServer` classes faciliate communication, and are mainly responsible for marshaling/unmarshaling messages to and from the user and server, as well as relaying inputs to the `GameEngine`.
- The `GameDisplay` class is responsible for rendering the game to the screen and accepting input from the user. 
- `game.py` stores the aforementioned class's definitions.
- `client.py` is the actual client program, responsible for instantiating the `GameClient` and `GameDisplay` and managing the local game loop.
- `server.py` is the server program, managing listening for clients, holding matches, and relaying inputs.
- `globalvars.py` stores global constants, such as screen size, color aliases, and names.

#### Sources
- [Netcode Concepts Part 2: Topology
](https://meseta.medium.com/netcode-concepts-part-2-topology-ad64f9f8f1e6)
- [Netcode Concepts Part 3: Lockstep and Rollback
](https://meseta.medium.com/netcode-concepts-part-3-lockstep-and-rollback-f70e9297271)
- [Rollback Pseudocode](https://gist.github.com/rcmagic/f8d76bca32b5609e85ab156db38387e9)