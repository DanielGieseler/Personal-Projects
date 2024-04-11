import random
import numpy as np
import itertools
from copy import deepcopy
import pandas as pd
from bisect import bisect
random.seed(12)


class Deck():
    def __init__(self, CARDS, times = 1):
        self.cards = CARDS.copy()
        if times > 1:
            self.cards = self.cards*times
        self.shuffle()
        
    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw(self, times = 1):
        return [self.cards.pop(-1) for _ in range(times)]


class Tree():
    def __init__(self):
        self.N_nodes = 0
        self.parent = {}
        self.groups = {}
    
    def addNode(self, parent, groups):
        self.N_nodes += 1
        self.parent[self.N_nodes] = parent
        self.groups[self.N_nodes] = groups
        return self.N_nodes

    def path2Root(self, node):
        path = []
        while (node != None):
            path.append(self.groups[node])
            node = self.parent[node]
        path.reverse()
        return path


def preprocessed_initialization():
    # ALL CARDS - TOTAL : 52
    CARDS = []
    for suit in range(0, 4):
        for number in range(0, 13):
            CARDS.append((suit, number))
    
    # ALL UNIQUE COMBINATIONS OF THREE - TOTAL: 100
    UNIQUE_TRIOS = []
    for s in range(0, 4):
        for n in range(0, 12):
            UNIQUE_TRIOS.append(((s, n), (s, n+1), (s, n+2 if n!=11 else 0)))
    for n in range(0, 13):
        for s1, s2, s3 in [(0,1,2), (0,1,3), (0,2,3), (1,2,3)]:
            UNIQUE_TRIOS.append(((s1, n), (s2, n), (s3, n)))

    # THE ABOVE TRIOS INDEXED BY CARD - TOTAL: 300
    TRIOS = {}
    for trio in UNIQUE_TRIOS:
        for card in trio:
            TRIOS.setdefault(card, []).append(trio)
    
    return CARDS, TRIOS


def add_card_to_table(card, table):
    table[card] += 1

def update_combinations(card, table, combinations):
    for trio in TRIOS[card]:
        check = np.prod(table[tuple(zip(*trio))])
        if check == 1:
            combinations[trio] = 1
        elif check == 8:
            combinations[trio] = 2


# TO DO (?)
#
# RETURN NOTHING AT REMAINDER IF DIVISION IS AT THE EXTREMETY
#
def divide(group, card, mode):
    index = group.index(card)
    if mode == 'LEFT':
        return group[index:], [group[:index]]
    elif mode == 'RIGHT':
        return group[:index+1], [group[index+1:]]
    elif mode == 'BOTH':
        return group[index:index+1], [group[:index], group[index+1:]]
    elif mode == 'POP':
        aux_group = list(group)
        aux_group.remove(card)
        return (card,), [tuple(aux_group)]


# INPUT
#    trio_pack = [main_card, trio_type, trio]
#    groups_pack = [[other_card1, group1_type, group1], [other_card2, group2_type, group2]]
#        !! assumed to be in the other of the trio
# OUTPUT:
#    united
#    remaining
def realize_trio(trio_pack, groups_pack):
    main_card, trio_type, trio = trio_pack
    main_card_pos = trio.index(main_card)
    # if both groups are the same, then merge into one
    if groups_pack[0][2] == groups_pack[1][2]:
        groups_pack = [[trio[1], groups_pack[0][1], groups_pack[0][2]]] # get the middle card
    
    # find out which operations have to be performed before uniting the trio
    OPS_MODES = []
    for card, group_type, group in groups_pack:
        if group_type in ['single table', 'single hand']:
            OPS_MODE = 'PASS'
        if trio_type == 'run':
            if group_type == 'run':
                if len(groups_pack) == 1:
                    if main_card_pos == 1:
                        OPS_MODE = 'ABORT'
                    else:
                        OPS_MODE = {0: 'LEFT', 2: 'RIGHT'}[main_card_pos]
                else:
                    OPS_MODE = {0: 'RIGHT', 1: 'BOTH', 2: 'LEFT'}[trio.index(card)]
            elif group_type == 'set':
                OPS_MODE = 'POP'
        elif trio_type == 'set':
            if group_type == 'run':
                OPS_MODE = 'BOTH'
            elif group_type == 'set':
                if len(groups_pack) == 1:
                    if main_card in group:
                        OPS_MODE = 'ABORT'
                    else:
                        OPS_MODE = 'PASS'
                else:
                    if len(group) == 4:
                        OPS_MODE = 'POP'
                    else:
                        OPS_MODE = 'ABORT'
        OPS_MODES.append(OPS_MODE)
    
    # execute operations and unite
    created, consumed, remainder = [], [['INCOMPLETE', (main_card,)]], []
    if 'ABORT' in OPS_MODES:
        return {}
    else:
        to_unite = []
        for mode, [card, group_type, group] in zip(OPS_MODES, groups_pack):
            if mode == 'PASS':
                to_unite.append(group)
            else:
                target, rest = divide(group, card, mode)
                to_unite.append(target)
                for gr in rest:
                    if len(gr) >= 3:
                        created.append(['REMAINING', gr])
                    else:
                        remainder.append(gr)
            label = {'single hand':'HAND', 'single table':'INCOMPLETE', 'run':'COMPLETE', 'set':'COMPLETE'}[group_type]
            consumed.append([label, group])
        to_unite.insert(main_card_pos, (main_card,))
        created.append(['UNITED', tuple(itertools.chain.from_iterable(to_unite))])
        remainder = list(itertools.chain.from_iterable(remainder))
        
        return {'CARD': main_card, 'TRIO': trio, 'CONSUMED': consumed, 'CREATED': created, 'REMAINDER': remainder}


# can be up to 6 trios per card
def trio_from_card(card, player_groups):
    trios = []
    #card_count = TABLE[card] # (??) add heuristics to only try best opportunities
    for trio in player_groups['POSSIBLE TRIOS']: # (??) use combinations_count
        if card in trio:
            trios.append([card, 'run' if trio[0][0] == trio[1][0] else 'set', trio])
    return trios
    
# can be up to 2 groups per card 
def group_from_card(card, player_groups):
    groups = []
    for group in player_groups['COMPLETE']:
        if card in group:
            groups.append([card, 'run' if group[0][0] == group[1][0] else 'set', group])
    for c in player_groups['INCOMPLETE']:
        if card == c:
            groups.append([card, 'single table', (card,)])
    for c in player_groups['HAND']:
        if card == c:
            groups.append([card, 'single hand', (card,)])
    return groups


def get_permutations_t2g(card, player_groups):
    trios = trio_from_card(card, player_groups)
    permutations = []
    for trio_pack in trios:
        other_cards = tuple(c for c in trio_pack[2] if c != card)
        # all permutations of a same TRIO
        t2g_permutations = list(itertools.product(
            [trio_pack],
            group_from_card(other_cards[0], player_groups),
            group_from_card(other_cards[1], player_groups)
        ))
        permutations.extend(t2g_permutations)
    return permutations


def RECURSIVE_FUNCTION(player_groups, TREE, parent):
    permutations = get_permutations_t2g(player_groups['INCOMPLETE'][0], player_groups)
    for t2g in permutations:
        new_GROUPS = deepcopy(player_groups)
        trio_pack, g1, g2  = t2g
        groups_pack = [g1, g2]
        changes = realize_trio(trio_pack, groups_pack)
        
        # check abortion cases
        if len(changes) == 0:
            continue     # fruitless combination
        if sum([card in new_GROUPS['CARDS ALREADY PLAYED'] for card in changes['REMAINDER']]) > 0:
            continue     # repeated combination
        
        # if everything is ok, update groups and add tree node
        for group_label, group in changes['CREATED']:
            new_GROUPS['COMPLETE'].append(group)
        for group_label, group in changes['CONSUMED']:
            group = group if len(group) != 1 else group[0]
            new_GROUPS[group_label].remove(group)
            if group_label == 'INCOMPLETE':
                new_GROUPS['CARDS ALREADY PLAYED'].append(group)
        new_GROUPS['INCOMPLETE'].extend(changes['REMAINDER'])
        changes['REMAINDER'] = new_GROUPS['INCOMPLETE']
        new_GROUPS['CHANGE'] = changes
        child = TREE.addNode(parent, new_GROUPS)
        
        # CHECK CASES
        if len(new_GROUPS['INCOMPLETE']) == 0:
            return child          # base case for finding solution
        else:
            child = RECURSIVE_FUNCTION(new_GROUPS, TREE, child)
            if child != 0:
                return child      # found a solution
    else:
        return 0              # none of the t2g trials worked


def represent_path_as_dataframe(path):
    dicti = {'CARD & TRIO': [], 'CONSUMED': [], 'TYPE1': [], 'CREATED': [], 'TYPE2': [], 'REMAINDER': []}
    for g in path:
        maxLen = max(max([len(l) for l in list(g.values())[2:]]), 2) 
        dicti['CARD & TRIO'].extend([g['CARD'], g['TRIO']] + ['']*(maxLen - 2) + [''])
        dicti['CONSUMED'].extend([e[1] for e in g['CONSUMED']] + ['']*(maxLen - len(g['CONSUMED'])) + [''])
        dicti['TYPE1'].extend([e[0] for e in g['CONSUMED']] + ['']*(maxLen - len(g['CONSUMED'])) + [''])
        dicti['CREATED'].extend([e[1] for e in g['CREATED']] + ['']*(maxLen - len(g['CREATED'])) + [''])
        dicti['TYPE2'].extend([e[0] for e in g['CREATED']] + ['']*(maxLen - len(g['CREATED'])) + [''])
        dicti['REMAINDER'].extend(g['REMAINDER'] + ['']*(maxLen - len(g['REMAINDER'])) + [''])
    df = pd.DataFrame.from_dict(dicti)
    df = df.set_index('CARD & TRIO')
    return df

def actualize_play(simple_path):
    to_discard = [simple_path[0]['CARD']] # HAND CARD
    to_create, to_delete = [], []
    for step in simple_path:
        for g_type, g in step['CREATED']:
            to_create.append(g)

        for g_type, g in step['CONSUMED']:
            if g_type == 'COMPLETE':
                to_delete.append(g)
            elif g_type == 'HAND':
                to_discard.append(g[0])

    for intermediate in list(set(to_create).intersection(to_delete)):
        to_delete.remove(intermediate)
        to_create.remove(intermediate)
    
    for g in to_delete:
        GROUPS.remove(g)
    for g in to_create:
        GROUPS.append(g)
    for card in to_discard:
        HAND.remove(card)
        add_card_to_table(card, TABLE)
        update_combinations(card, TABLE, COMBINATIONS)

def update_player():
    PLAYER_TABLE = TABLE.copy()
    PLAYER_COMBINATIONS = COMBINATIONS.copy()
    for c in HAND:
        add_card_to_table(c, PLAYER_TABLE)
        update_combinations(c, PLAYER_TABLE, PLAYER_COMBINATIONS)
    PLAYER_GROUPS = {
        'COMPLETE'  : GROUPS,
        'INCOMPLETE': [],
        'HAND'      : HAND,
        'CARDS ALREADY PLAYED': [],
        'POSSIBLE TRIOS' : list(PLAYER_COMBINATIONS.keys())
    }
    return PLAYER_GROUPS

def start_game():
    global CARDS, TRIOS, DECK, TABLE, GROUPS, COMBINATIONS, HAND
    CARDS, TRIOS = preprocessed_initialization()
    DECK = Deck(CARDS, times = 2)
    TABLE = np.zeros((4,13), dtype = int)
    GROUPS = []
    COMBINATIONS = {}
    HAND = DECK.draw(times = 9)
    return CARDS, TRIOS, DECK, TABLE, GROUPS, COMBINATIONS, HAND




def check_for_plays():
    PLAYER_GROUPS = update_player()
    PLAYS = []
    for hand_card in PLAYER_GROUPS['HAND']:
        HAND_PLAYER_GROUPS = deepcopy(PLAYER_GROUPS)
        HAND_PLAYER_GROUPS['INCOMPLETE'].append(hand_card)
        HAND_PLAYER_GROUPS['HAND'].remove(hand_card)
        TREE = Tree()
        root = TREE.addNode(None, HAND_PLAYER_GROUPS)
        child = RECURSIVE_FUNCTION(HAND_PLAYER_GROUPS, TREE, root)
        if child != 0:
            path = TREE.path2Root(child)
            simple_path = []
            for g in path:
                if 'CHANGE' in g:
                    simple_path.append(g['CHANGE'])
            # find all discards
            hand_discards = []
            for i, step in enumerate(simple_path):
                if i == 0:
                    hand_discards.append(step['CARD'])
                for g_type, group in step['CONSUMED']:
                    if g_type == 'HAND':
                        hand_discards.extend(group)
            hand_discards = tuple(hand_discards)
            PLAYS.append([hand_discards, simple_path])
    # filter out repeated opportunities by same discarded cards
    plays_aux = [[tuple(sorted(p[0], key = lambda y: (y[1], y[0]))), p] for p in PLAYS]
    plays_aux.sort(key = lambda x: x[0])
    PLAYS = []
    for key, group in itertools.groupby(plays_aux, key = lambda x: x[0]):
        g = list(group)
        PLAYS.append(g[0][1])
    return PLAYS

def draw_card():
    HAND.append(DECK.draw()[0])
    HAND.sort(key = lambda x: (x[1], x[0]))

def list_spacer(list_of_lists, spacer, spaces):
    final_list = []
    if len(list_of_lists) != 0:
        final_list.extend(list_of_lists[0])
        for lst in list_of_lists[1:]:
            final_list.extend([spacer]*spaces)
            final_list.extend(lst)
    return final_list

def print_matrix(play_sequence):
    print_matrix = [[] for _ in range(5)]
    for step in play_sequence:
        for phase in ['CONSUMED', 'CREATED']:
            for r, subphase in enumerate(['FIXED', 'LOOSE']):
                groups = step[phase + ' ' + subphase]
                groups.sort(key = len)
                lengths = [len(g) for g in groups]
                middlePoint = max(bisect(np.cumsum(lengths), int(np.sum(lengths)/2)), 1)
                print_matrix[3*r].extend(list_spacer(groups[:middlePoint], 'None', 1))
                print_matrix[3*r+1].extend(list_spacer(groups[middlePoint:], 'None', 1))
            maxCol = max([len(rowCards) for rowCards in print_matrix])
            for rowCards in print_matrix:
                rowCards.extend(['None']*(maxCol - len(rowCards)))
                rowCards.extend([phase])
        for rowCards in print_matrix:
            rowCards.extend(['CREATED2'])
    for rowCards in print_matrix:
        rowCards.pop()
        rowCards.pop()
    return print_matrix


def format_play_opportunities(PLAYS):
    PLAY_OPPORTUNITIES = []
    for hand_discards, simple_path in PLAYS:
        simplest_path = []
        for step in simple_path:
            simplest_path.append({
                'CONSUMED FIXED': [s[1] for s in step['CONSUMED'] if s[0] != 'INCOMPLETE'],
                'CONSUMED LOOSE': [s[1] for s in step['CONSUMED'] if s[0] == 'INCOMPLETE'],
                'CREATED FIXED' : [s[1] for s in step['CREATED']],
                'CREATED LOOSE' : [(s,) for s in step['REMAINDER']]
            })

        PLAY_OPPORTUNITIES.append({
            'HAND DISCARDS' : hand_discards,
            'SIMPLE PATH'   : simple_path,
            'PRINT MATRIX'  : print_matrix(simplest_path)
        })
    return PLAY_OPPORTUNITIES

