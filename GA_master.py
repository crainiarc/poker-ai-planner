from GA_bot import GABot
import numpy as np
# import random
# random.uniform(a, b)

# genes = [deal_strategies, flop_strategies, turn_strategies, river_strategies]
# genes[strategy_index] = upper limit on the % of self.credits willing to use
# % will be a value in the range [0, 1]
# index will be in the range [0, 3140844486 - 1]
# deal: (52 choose 2) = 1326 combinations
# flop: (52 choose 2)*(50 choose 3) = 25989600 combinations
# turn: (52 choose 2)*(50 choose 4) = 305377800 combinations
# river: (52 choose 2)*(50 choose 5) = 2809475760 combinations
# numpy.random.rand(1, 3140844486)