import time
import platform
import traceback
import sys

from poker_game import PokerGame

def main():
   from example_bots.example_bot import FoldBot
   from example_bots.raise_twenty_bot import RaiseTwentyBot
   # from bots.callbot import CallBot
   # from bots.jkbot import JKBot
   # from example_bots.protobot.cpp.foldbot_cpp import FoldBotCpp
   # from example_bots.protobot.java.foldbot_java import FoldBotJava
   # from example_bots.protobot.java.boten_anna import Anna
   # uncomment this line to run the CPP foldbot
   #bots = [ExampleBot, FoldBotCpp]
   seed = None
   if len(sys.argv) > 1:
       seed = int(sys.argv[1])
   # bots = [FoldBot, RaiseTwentyBot, Anna]
   bots = [FoldBot, RaiseTwentyBot]
   game = PokerGame(bots=bots, seed=seed)
   start_time = time.time()
   outcome = game.run()
   end_time = time.time()
   print "Result:", outcome
   print "Time elapsed: %0.2f seconds" % (end_time - start_time)

if __name__ == "__main__":
    import sys
    try:
        sys.exit(main())
    except Exception, e:
        print ""
        traceback.print_exc()
    if platform.system() == 'Windows':
        raw_input('\nPress enter to continue')
