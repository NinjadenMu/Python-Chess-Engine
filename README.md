# Python-Chess-Engine v0.9
 A UCI chess engine written in Python.  
This engine returns moves in UCI and uses alpha/beta search along with a simple eval function based on piece square tables.  It uses an extremely primitive method for parallel search by simply dividing up the original complete search tree and assigning those subtrees to a free thread.  It also supports an opening book.  Baron's (an old but fairly strong chess engine) opening book is installed and used by default.

Please allow up to a minute for the engine to make its move.  If it still has not made its move, stop the program, change the ply variable, and retry.

This chess engine is set to play games as black.  At 4 or 5 ply, the engine plays at around 800 elo.
