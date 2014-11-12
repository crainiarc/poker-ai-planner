# genes = [deal_strategies, flop_strategies, turn_strategies, river_strategies]
# genes[strategy_index] = upper limit on the % of self.credits willing to use
# % will be a value in the range [0, 1]
# index will be in the range [0, 3140844486 - 1]
# deal: (52 choose 2) = 1326 combinations
# flop: (52 choose 2)*(50 choose 3) = 25989600 combinations
# turn: (52 choose 2)*(50 choose 4) = 305377800 combinations
# river: (52 choose 2)*(50 choose 5) = 2809475760 combinations
# numpy.random.rand(1, 3140844486)

def _get_rank(card):
    return card[0]

def _get_suit(card):
    return card[1]

def card_to_offset(card):
	rank = _get_rank(card) # 2, 3, ... , 14
	suit = _get_suit(card) # d, c, h, s
	rank_offset = rank - 2

	if suit == 'd':
		suit_offset = 0
	elif suit == 'c':
		suit_offset = 1
	elif suit == 'h':
		suit_offset = 2
	elif suit == 's':
		suit_offset = 3
	else:
		return "Error in card_to_offset"

	offset = suit_offset * 13 + rank_offset
	print card, offset
	return offset

def get_index(hand, community):
	deck_size = 52
	comm_size = len(community)

	# Set up offsets
	offsets = []
	offsets.append(card_to_offset(hand[0]))
	offsets.append(card_to_offset(hand[1]))

	for i in range(0, comm_size):
		offsets.append(card_to_offset(community[i]))

	# Set up total
	if comm_size == 0: # Deal phase: 1326 combinations
		total = 52*51
	elif comm_size == 3: # Flop phase: 25989600 combinations
		pass
	elif comm_size == 4: # Turn phase: 305377800 combinations
		pass
	elif comm_size == 5: # River phase: 2809475760 combinations
		pass
	else:
		return "Error in get_index"

	# Extract index
	print offsets
	index = 0
	for i in range(0, len(offsets)):
		block_size = total/deck_size
		index = index + offsets[i]*block_size

	return index

hand = [[10,'c'],[3,'s']]
community = []
print get_index(hand, community)

















