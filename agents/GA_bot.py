from helper_bot import HelperBot
from GA_helper import *

class GABot(HelperBot):
    # genes = [deal_strategies, flop_strategies, turn_strategies, river_strategies]
    # genes[strategy_index] = upper limit on the % of self.credits willing to use
    # % will be a value in the range [0, 1]
    # index will be in the range [0, 3140844486 - 1]
    # deal: (52 choose 2) = 1326 combinations
    # flop: (52 choose 2)*(50 choose 3) = 25989600 combinations
    # turn: (52 choose 2)*(50 choose 4) = 305377800 combinations
    # river: (52 choose 2)*(50 choose 5) = 2809475760 combinations

    def set_genes(genes):
        self.genes = genes

    def get_genes():
        return self.genes

    def turn(self):
        hand = self.get_hand()
        community_cards = self.get_community_cards()
        index = cards_to_gene_index(hand, community)
        upper_bound_bet = self.genes[index] * self.credits

        # Get current bid
        # If current bid > upper_bound_bet, fold
        # Decide whether to check or raise
        # If raise, submit a random bid between [current bid, upper_bound_bet]

        action = raw_input('Action: ').split()
        if action[0] == 'raise':
            return self.action('raise', amount=int(action[1]))
        elif action[0] == 'check' or action[0] == 'call':
            return self.action(action[0])
        else:
            return self.action('fold')