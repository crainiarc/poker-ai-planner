from helper_bot import HelperBot
from cards import n_card_rank

import random

cardsDict = [(r, s) for s in ['d', 'c', 'h', 's'] for r in range(2, 15)]

class PokerState:
    def __init__(self, hand, community_cards, a_credits, b_credits, curr_pot_diff):
        self.credits = [a_credits, b_credits]
        self.hand = hand[:]
        self.community_cards = community_cards[:]
        self.playerJustMoved = 0

        if curr_pot_diff == 0:
            self.moves_taken = []
        elif curr_pot_diff == 10:
            self.moves_taken = [1, 3]
        else:
            self.moves_taken = [1, 4]

    def Clone(self):
        ps = PokerState(self.hand, self.community_cards, self.credits[0], self.credits[1], self.getPotDifference())
        ps.playerJustMoved = self.playerJustMoved
        return ps

    def DoMove(self, move):
        self.moves_taken += [move]
        player = self.getPlayerTurn()
        diff = self.getPotDifference()

        if move == 1 or move == 2:
            credits[player] -= diff
        elif move == 3:
            credit[player] -= (diff + 10)
        elif move == 4:
            credit[player] -= (diff + 20)

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
            return 1
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

            A = n_card_rank(hand + self.community_cards)
            B = n_card_rank(opp + self.community_cards)
            if (A == max(A, B)):
                return 1 if playerjm == 0 else 0
            else:
                return 0 if playerjm == 0 else 1

    def getPlayerTurn(self):
        return len(self.moves_taken) % 2

    def getFolded(self):
        if self.moves_taken[-1] == 0:
            return len(self.moves_taken) % 2 + 1
        else:
            return -1

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

class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """
    def __init__(self, move = None, parent = None, state = None):
        self.move = move # the move that got us to this node - "None" for the root node
        self.parentNode = parent # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.GetMoves() # future child nodes
        self.playerJustMoved = state.playerJustMoved # the only part of the state that the Node needs later
        
    def UCTSelectChild(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.childNodes, key = lambda c: c.wins/c.visits + sqrt(2*log(self.visits)/c.visits))[-1]
        return s
    
    def AddChild(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move = m, parent = self, state = s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n
    
    def Update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
             s += c.TreeToString(indent+1)
        return s

    def IndentString(self,indent):
        s = "\n"
        for i in range (1,indent+1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
             s += str(c) + "\n"
        return s


def UCT(rootstate, itermax, verbose = False):
    """ Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    rootnode = Node(state = rootstate)

    for i in range(itermax):
        node = rootnode
        state = rootstate.Clone()

        # Select
        while node.untriedMoves == [] and node.childNodes != []: # node is fully expanded and non-terminal
            node = node.UCTSelectChild()
            state.DoMove(node.move)

        # Expand
        if node.untriedMoves != []: # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves) 
            state.DoMove(m)
            node = node.AddChild(m,state) # add child and descend tree

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.GetMoves() != []: # while state is non-terminal
            state.DoMove(random.choice(state.GetMoves()))

        # Backpropagate
        while node != None: # backpropagate from the expanded node and work back to the root node
            node.Update(state.GetResult(node.playerJustMoved)) # state is terminal. Update node with result from POV of node.playerJustMoved
            node = node.parentNode

    # Output some information about the tree - can be omitted
    if (verbose): print rootnode.TreeToString(0)
    else: print rootnode.ChildrenToString()

    return sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move # return the move that was most visited
       





class MctsBot(HelperBot):
    def turn(self):
        # print "Community Cards: " + str(self.get_community_cards())
        # print "Hand: " + str(self.get_hand())

        self._process_events()

        state = PokerState(self.hand, self.community_cards, self.credits,
            self.opponent[1], self.pot_diff)
        m = UCT(rootstate = state, itermax = 1000, verbose = False)
        if m == 0:
            self.action('fold')
        elif m == 1:
            self.action('check')
        elif m == 2:
            self.action('call')
        elif m == 3:
            self.action('raise', 10)
        elif m == 4:
            self.action('raise', 20)


        # action = raw_input('Action: ').split()
        # if action[0] == 'raise':
        #     return self.action('raise', amount=int(action[1]))
        # elif action[0] == 'check' or action[0] == 'call':
        #     return self.action(action[0])
        # else:
        #     return self.action('fold')

    def _process_events(self):
        for event in self.event_queue:
            method = getattr(self, '_' + event.type)
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
        self.community_cards += event.card

    def _river(self, event):
        self.round = "river"
        self.community_cards += event.card

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
