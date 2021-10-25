# distsys-fa21-project

A distributed, real-time competitive multiplayer game.

## challenges

Abstractly, the goal of this project is to maintain a highly available, consistent system where all users manipulate a shared state and can respond to each others' changes in real time. 

In terms of the CAP theorem, we have **consistency** and **availability** as our top priorities. In order for a multiplayer game to be *fair*, all players need to be able to come to the same conclusions about what exactly happens in the game, and it must not be easy for players to manipulate the game state outside of the ways possible with their normal inputs. In order for a multiplayer game to be *playable*, however, all players also need to be able to see each others' actions quickly, so they can react in turn.

## architecture

The architecture of the system reflects this. The simplest way to make sure every user receives the same information about the game state and comes to the same conclusion about the game is to define some node as a single source of truth -- in our case, we run a server program to officiate communicating to each user the inputs of others, as well as determine win/loss conditions.

