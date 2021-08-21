# Python-Chess-Engine v0.9
 A UCI chess engine written in Python.  
This engine returns moves in UCI and uses alpha/beta search along with a simple eval function based on piecesquare tables.  It supports parallel computing although it can't really utilize more than ~50 threads.
Please allow up to a minute for the engine to make its move.  If it still has not made its move, stop the program, change the ply variable, and retry.

Only works from the perspective of black right now (will be changed in the future)
