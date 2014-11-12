import random

from agents.mcts.uct import UCT
from helper_bot import HelperBot
from cards import n_card_rank

# Generate Cards Dictionary
cardsDict = [(r, s) for s in ['d', 'c', 'h', 's'] for r in range(2, 15)]


class PokerState:
    def __init__(self, hand, community_cards, a_credits, b_credits, curr_pot_diff, pot):
        self.credits = [a_credits, b_credits]
        self.hand = hand[:]
        self.community_cards = community_cards[:]
        self.playerJustMoved = 0
        self.pot = pot

        if curr_pot_diff == 0:
            self.moves_taken = []
        elif curr_pot_diff == 10:
            self.moves_taken = [1, 3]
        else:
            self.moves_taken = [1, 4]

    def Clone(self):
        ps = PokerState(self.hand, self.community_cards, self.credits[0],
            self.credits[1], self.getPotDifference(), self.pot)

        ps.playerJustMoved = self.playerJustMoved
        return ps

    def DoMove(self, move):
        self.moves_taken += [move]
        player = self.getPlayerTurn()
        diff = self.getPotDifference()

        if move == 1 or move == 2:
            self.credits[player] -= diff
            self.pot += diff
        elif move == 3:
            self.credits[player] -= (diff + 10)
            self.pot += (diff + 10)
        elif move == 4:
            self.credits[player] -= (diff + 20)
            self.pot += (diff + 20)

        self.playerJustMoved = (self.playerJustMoved + 1) % 2


    def GetMoves(self):
        if self.getFolded() != -1 or self.getStageNum() == 5:
            return []
        
        player = self.getPlayerTurn()
        diff = self.getPotDifference()
        
        moves = [0]
        if diff == 0:
            moves += [1]
        
        if self.credits[(player + 1) % 2] == 0:
            return moves

        if self.credits[player] >= diff:
            moves += [2]

        if self.credits[player] >= diff + 10:
            moves += [3]

        if self.credits[player] >= diff + 20:
            moves += [4]
            
        return moves

    def GetResult(self, playerjm):
        if self.getFolded() == playerjm:
            return 0
        elif self.getFolded() == (playerjm + 1) % 2:
            return self.pot #1
        else:
            # evaluate
            opp = []
            while len(opp) < 2:
                c = cardsDict[random.randrange(52)]
                if not c in self.hand + self.community_cards + opp:
                    opp += [c]

            while len(self.community_cards) < 5:
                c = cardsDict[random.randrange(52)]
                if not c in self.hand + self.community_cards + opp:
                    self.community_cards += [c]

            # print self.hand + self.community_cards
            # print opp + self.community_cards
            A = n_card_rank(self.hand + self.community_cards)
            B = n_card_rank(opp + self.community_cards)
            if (A == max(A, B)):
                return self.pot if playerjm == 0 else 0
            else:
                return 0 if playerjm == 0 else self.pot

    def getPlayerTurn(self):
        return len(self.moves_taken) % 2

    def getFolded(self):
        if len(self.moves_taken) == 0 or self.moves_taken[-1] != 0:
            return -1
        else:
            return len(self.moves_taken) % 2 + 1

    def getPotDifference(self):
        sums = [0, 0]

        for i in range(1, len(self.moves_taken) + 1):
            if self.moves_taken[-i] == 3:
                sums[-i % 2] += 10
            elif self.moves_taken[-i] == 4:
                sums[-i % 2] += 20
            else:
                pass
        return abs(sums[0] - sums[1])

    def getStageNum(self):
        num = 0
        consecutive_check = 0

        for move in self.moves_taken:
            if move == 1:
                if consecutive_check == 1:
                    num += 1
                    consecutive_check = 0
                else:
                    consecutive_check = 1
            else:
                consecutive_check = 0
                if move == 2:
                    num += 1

        return num



       





class MctsBot(HelperBot):
    def turn(self):
        self._process_events()

        state = PokerState(self.hand, self.community_cards, self.credits,
            self.opponent[1], self.pot_diff, self.pot)
        m = UCT(rootstate = state, itermax = 1000, verbose = False)
        action_list = [self.action('fold'), self.action('check'),
                       self.action('call'), self.action('raise', 10),
                       self.action('raise', 20)]
        return action_list[m]

    def _process_events(self):
        for event in self.event_queue:
            method_name = '_' + event.type
            method = getattr(self, method_name)
            if not method:
                raise Exception("Method %s not implemented" % method_name)
            method(event)
            print event

        self.event_queue = []

    def _join(self, event):
        self.player_id = (event.player_id + 1) % 2
        self.opponent = [event.player_id, event.credits]

    def _new_round(self, event):
        self.community_cards = []
        self.pot = 0
        self.pot_diff = 0

    def _button(self, event):
        self.button = self.player_id == event.player_id

    def _big_blind(self, event):
        pass

    def _small_blind(self, event):
        pass

    def _deal(self, event):
        self.round = "deal"
        self.hand = event.cards[:]

    def _flop(self, event):
        self.round = "flop"
        self.community_cards += event.cards

    def _turn(self, event):
        self.round = "turn"
        self.community_cards += [event.card]

    def _river(self, event):
        self.round = "river"
        self.community_cards += [event.card]

    def _action(self, event):
        if self.player_id != event.player_id:
            if event.action.type == 'call':
                self.pot += self.pot_diff
                self.pot_diff = 0
            elif event.action.type == 'raise':
                self.pot += (self.pot_diff + event.action.amount)
                self.pot_diff = event.action.amount

    def _adjust_credits(self, event):
        if event.player_id == self.player_id:
            self.credits += event.amount
        else:
            self.opponent[1] += event.amount

    def _win(self, event):
        pass

    def _bad_bot(self, event):
        pass

    def _end_of_round(self, event):
        pass
