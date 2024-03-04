### TO DO ###
# - automate player response based on ideal strategy table
# - make GUI

### UPDATE vs v4.2 ###
# - reworked dealer's ace-first-blackjack. If dealer has 1st card ace and has blackjack, hand is over whether insurance taken or not. Compare with Player's hand.
# - added support for left sidebet perfect pairs
# - added support for right sidebet 21+3
# - code cleanup


import os
import time
import random
import copy
import inflect
num2word = inflect.engine()



## NEW_SHOE method ##
##
# Inputs:
# num_decks (int): No. of decks to be used in the new shoe
#
# Outputs:
# shoe (list): New shuffled shoe

def new_shoe(num_decks):

    suits = ['Hearts', 'Diamonds', 'Spades', 'Clubs']
    faces = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    shoe = [Card(suit=suit, face=face) for i in range(num_decks) for suit in suits for face in faces]
    print('\nNEW SHOE. Playing with %d decks in shoe' % (len(shoe)/52))

    shoe = shuffle_shoe(shoe, 3)

    return shoe


## SHUFFLE_SHOE method ##
##
# Inputs:
# shoe (list): Deck of cards to be shuffled
# times (int): No. of times the shoe is to be shuffled
#
# Outputs:
# shoe (list): Shuffled shoe

def shuffle_shoe(shoe = list, times = int):
    if times < 1:
        print("Shuffle times must be > 0\n")
        return shoe
    
    for i in range(times):
        random.shuffle(shoe)

    print("Shoe shuffled %d times" % times)
    return shoe


## SUM_CARDS method ##
##
# Inputs:
# hand_cards (list): Hand/deck of cards
#
# Outputs:
# sum_cards_prim (int): Sum of blackjack primary values of all cards
# sum_cards_sec (int): Sum of blackjack secondary values of all cards
# best_sum (int): Highest allowable sum out of primary and secondary sums calculated above

def sum_cards(hand_cards):
    sum_cards_sec = sum(card.value_sec for card in hand_cards)
     
    num_aces = sum(1 if card.face == 'A' else 0 for card in hand_cards)
    if num_aces > 0:
        sum_cards_prim = sum(card.value_sec for card in hand_cards) + 10
    else:
        sum_cards_prim = sum_cards_sec
    
    if sum_cards_prim <= 21:
        best_sum = sum_cards_prim
    else:
        best_sum = sum_cards_sec        

    return sum_cards_prim, sum_cards_sec, best_sum


## PRINT_CARDS_BESTSUM method ##
##
# Inputs:
# hand_cards (list): Hand of cards
#
# Outputs:
# prints all the cards in the hand in a single row along with best sum

def print_cards_bestsum(hand_cards):
    card_str = ''
    for card in hand_cards:
        card_str += str(card)+', '

    sum_cards_prim, sum_cards_sec, best_sum  = sum_cards(hand_cards)

    card_str = card_str[:-2] + (" (Sum: %d)" % best_sum)
    
    print(card_str)


## PRINT_CARDS_BOTHSUMS method ##
##
# Inputs:
# hand_cards (list): Hand of cards
#
# Outputs:
# prints all the cards in the hand in a single row along with primary sum and/or secondary sum as per situation

def print_cards_bothsums(hand_cards):
    card_str = ''
    for card in hand_cards:
        card_str += str(card)+', '

    sum_cards_prim, sum_cards_sec, best_sum  = sum_cards(hand_cards)

    if sum_cards_sec == sum_cards_prim:
        card_str = card_str[:-2] + (" (Sum: %d)" % sum_cards_prim)
    elif sum_cards_prim == 21:
        card_str = card_str[:-2] + (" (Sum: %d)" % sum_cards_prim)
    elif sum_cards_prim > 21:
        card_str = card_str[:-2] + (" (Sum: %d)" % sum_cards_sec)
    else:
        card_str = card_str[:-2] + (" (Sum: %d/%d)" % (sum_cards_sec, sum_cards_prim))
    
    print(card_str)


## GET_PLAYER_INIT_INPUT method ##
##
# Inputs:
# Player (Bro)
# playerHand (HandClass)
# num_hands (int): number of hands being played by the player. 2 if player splitted, else 1
#
# Outputs:
# player_action (string): H = Hit, S = Stand, D = Double down, SPLIT = split, EXIT = exit game

def get_player_init_input(Player, playerHand, num_hands):
    playerHand.player_action = ""
    
    # Don't allow doubling down or splitting if balance not sufficient
    if Player.balance < 2*playerHand.bets['main'] or num_hands > 1:
        playerHand.player_action = input('\nHit (h)/ Stand (s) or exit: ').upper()

        while playerHand.player_action not in ('H', 'S', 'EXIT'):
            if playerHand.player_action == 'D'and num_hands == 1:
                print("Insufficient balance to double down (Required $%s, Balance $%s)." % (2*playerHand.bets['main'], Player.balance))
                print("Please respond with 'h', 's' or 'exit'")
            elif playerHand.player_action == 'D':
                print("Cannot double down after splitting")
                print("Please respond with 'h', 's' or 'exit'")
            elif playerHand.player_action == 'SPLIT' and num_hands == 1 and playerHand.hand_cards[0].value_prim != playerHand.hand_cards[1].value_prim:
                print("Invalid response. Please respond with 'h', 's' or 'exit'")
            elif playerHand.player_action == 'SPLIT' and num_hands == 1:
                print("Insufficient balance for splitting (Required $%s, Balance $%s)." % (2*playerHand.bets['main'], Player.balance))
                print("Please respond with 'h', 's' or 'exit'")
            elif playerHand.player_action == 'SPLIT':
                print("Cannot split again.")
                print("Please respond with 'h', 's' or 'exit'")
            else:
                print("Invalid response. Please respond with 'h', 's' or 'exit'")

            playerHand.player_action = input('\nHit (h)/ Stand (s) or exit: ').upper()

    # Allow doubling down and splitting if sufficient balance
    else:
        # if player has two cards of the same value, give option of splitting
        if playerHand.hand_cards[0].value_prim == playerHand.hand_cards[1].value_prim:
            playerHand.player_action = input('\nHit (h)/ Double Down (d)/ Split (split)/ Stand (s) or exit: ').upper()

            while playerHand.player_action not in ('H', 'S', 'D', 'SPLIT', 'EXIT'):
                print("Invalid response. Please respond with 'h', 'd', 'split', 's' or 'exit'")
                playerHand.player_action = input('\nHit (h)/ Double Down (d)/ Split (split)/ Stand (s) or exit: ').upper()
        else:
            playerHand.player_action = input('\nHit (h)/ Double Down (d)/ Stand (s) or exit: ').upper()

            while playerHand.player_action not in ('H', 'S', 'D', 'EXIT'):
                print("Invalid response. Please respond with 'h', 'd', 's' or 'exit'")
                playerHand.player_action = input('\nHit (h)/ Double Down (d)/ Stand (s) or exit: ').upper()

    if (playerHand.player_action == 'SPLIT'):
        if playerHand.hand_cards[0].face == 'A':
            print("Splitting Aces ...")
        elif playerHand.hand_cards[0].face == 'K':
            print("Splitting Kings ...")
        elif playerHand.hand_cards[0].face == 'Q':
            print("Splitting Queens ...")
        elif playerHand.hand_cards[0].face == 'J':
            print("Splitting Jacks ...")
        elif playerHand.hand_cards[0].face == '6':
            print("Splitting Sixes ...")
        else:
            print("Splitting %ss ..." % (num2word.number_to_words(playerHand.hand_cards[0].value_prim).capitalize()))
        return playerHand.player_action
    elif (playerHand.player_action == 'EXIT'):
        exit_action = ''
        while exit_action not in ('y','n'):
            exit_action = input('\nDo you want to exit the game? ALL ACTIVE BETS WILL BE FORFEITED (y/n): ').lower()
        
        if exit_action == 'y':
            return 'EXIT'
        else:
            return get_player_init_input(Player, playerHand, num_hands)
    else:
        return playerHand.player_action


## GET_PLAYER_INPUT method ##
##
# Inputs:
# <none>
#
# Outputs:
# player_action (string): H = Hit, S = Stand, EXIT = exit game

def get_player_input():
    player_action = ""
    player_action = input('\nHit (h)/ Stand (s) or exit: ').upper()

    while player_action not in ('H', 'S', 'EXIT'):
        print("Invalid response. Please respond with 'H', 'S' or 'exit'")
        player_action = input('\nHit (h)/ Stand (s) or exit: ').upper()
    
    if (player_action == 'EXIT'):
        exit_action = ''
        while exit_action not in ('y','n'):
            exit_action = input('\nDo you want to exit the game? BET WILL BE FORFEITED (y/n): ').lower()
        
        if exit_action == 'y':
            return 'EXIT'
        else:
            return get_player_input()
    else:
        return player_action


## GET_PLAYER_BET method ##
##
# Inputs:
# Player (Bro)
#
# Outputs:
# Player (Bro)
# Sets Player's bet amounts (main, left sidebet, right sidebet). Gives the option to repeat last bet.

def get_player_bet(Player):    
    bet_amt = '0'
        
    def is_bet_valid(bet_amt: list):
        if len(bet_amt) != 3:
            return False
        # all bets should be numeric
        elif not (bet_amt[0].isnumeric() == bet_amt[1].isnumeric() == bet_amt[2].isnumeric() == True):
            return False 
        # main bet should be > 0, rest should be >= 0
        elif int(bet_amt[0]) < 1 or int(bet_amt[1]) < 0 or int(bet_amt[2]) < 0:
            return False
        # all bets should be multiples of 10
        elif int(bet_amt[0])%10 > 0 or int(bet_amt[1])%10 > 0 or int(bet_amt[2])%10 > 0:
            return False
        else:
            return True
    
    
    ask_bet_again = True
    while (ask_bet_again):

        last_bet_total = sum(Player.prev_bets.values())

        if  last_bet_total != 0 and last_bet_total <= Player.balance:
            print("\nLast Bet: Main $%s, Left sidebet $%s, Right sidebet $%s" % (Player.prev_bets['main'], Player.prev_bets['sidebet_L'], Player.prev_bets['sidebet_R']))
            bet_amt = input("Place Bet Amount [main, left sidebet, right sidebet] \nin multiples of 10 (enter 'r' to repeat last bet): $").upper()
        else:
            bet_amt = input("\nPlace Bet Amount [main, left sidebet, right sidebet] in multiples of 10: $").upper()

        bet_amt = bet_amt.replace(' ','').split(',')
        len_bet = len(bet_amt)


        # if player entered 'r' and balance lower than total last bet
        if len_bet == 1 and bet_amt[0] == 'R' and last_bet_total > Player.balance:
            print("Insufficient balance to repeat last bet (Required $%s, Balance $%s)" % (sum(Player.prev_bets.values()), Player.balance))
            
        # if player entered 'r' and there WAS a last bet and balance is enough
        elif len_bet == 1 and bet_amt[0] == 'R' and last_bet_total > 0 and last_bet_total <= Player.balance:
            Player.Hand1.bets = Player.prev_bets.copy()
            ask_bet_again = False
            
        # else if player input only 1 entry (assume it to be main bet) but bet is invalid
        elif len_bet == 1 and (bet_amt[0].isnumeric() == False or int(bet_amt[0]) < 1 or int(bet_amt[0])%10 > 0):
            print("Invalid bet")
            
        # else if player input only 1 entry (assume it to be main bet) but bet is more than balance
        elif len_bet == 1 and int(bet_amt[0]) > Player.balance:
            print("Insufficient balance to repeat last bet (Required $%s, Balance $%s)" % (sum(Player.prev_bets.values()), Player.balance))
            
        elif len_bet == 1:
            Player.Hand1.bets['main'] = int(bet_amt[0])*1.0
            ask_bet_again = False

        # else bet MUST have 3 (non-negative, multiples of 10, integer) inputs separated by comma. Main bet should be > 0.
        elif is_bet_valid(bet_amt) == False:
            print("Invalid bet")
            
        # else if total amount bet is higher than balance
        elif is_bet_valid(bet_amt) == True and sum(int(values) for values in bet_amt) > Player.balance:
            print("Insufficient balance ($%s)" % Player.balance)
            
        else:
            Player.Hand1.bets['main'] = int(bet_amt[0])*1.0
            Player.Hand1.bets['sidebet_L'] = int(bet_amt[1])*1.0
            Player.Hand1.bets['sidebet_R'] = int(bet_amt[2])*1.0
            ask_bet_again = False

    return Player


## DEAL_CARDS_TO_PLAYER method ##
##
# Inputs:
# playerHand (HandClass)
# deck (list)
#
# Outputs:
# playerHand (HandClass)
# deck (list)

def deal_cards_to_player(playerHand, deck):
    
    while playerHand.player_action in ('H','D'):
        new_card = deck.pop(0)
        playerHand.hand_cards.append(new_card)

        # If DOUBLE DOWN
        if playerHand.player_action == 'D':
            playerHand.bets['main'] *= 2
            print('\n____________\nDOUBLE DOWN\n------------\nTotal bet doubled to: $%s\n' % playerHand.bets['main'])
            time.sleep(2)

        print("\nPlayer:")
        print_cards_bothsums(playerHand.hand_cards)

        player_sum_cards_prim, player_sum_cards_sec, player_best_sum = sum_cards(playerHand.hand_cards)

        if player_best_sum > 21:
        # if player's best allowable score > 21 then bust out
            playerHand.hand_status = 'bust'
            break
        elif player_best_sum == 21 or playerHand.player_action == 'D':
        # if player's best allowable score == 21 or player had doubled down then auto-stand
            playerHand.hand_status = 'stand'
            break

        # if player has not busted, ask for hit/stand action
        playerHand.player_action = get_player_input()

    return playerHand, deck


## PLAY_HAND method ##
##
# Inputs:
# playerHand (HandClass)
# deck (list)
#
# Outputs:
# playerHand (HandClass)
# deck (list)

def play_hand(playerHand, deck):
    # if player has Blackjack in first two cards of the hand, return
    if playerHand.hand_status == 'stand_blackjack':
        print("\nPlayer has got Blackjack.")
        return playerHand, deck
    
    playerHand, deck = deal_cards_to_player(playerHand, deck)
    
    if playerHand.player_action == 'EXIT':
        playerHand.hand_status = 'exit'
        
    elif playerHand.player_action == 'S':
        playerHand.hand_status = 'stand'
        print("\nPlayer has stood.")

    # If player busted
    elif playerHand.hand_status == 'bust':
        time.sleep(2)
        print("\nPlayer has busted.")

    return playerHand, deck


## COMPARE_PLAYER_DEALER method ##
##
# Inputs:
# playerHand (HandClass): Player's Hand object
# dealerHand (HandClass): Dealer's Hand object
# payoffs (dict): Dictionary containing payoff of every event - main bet, blackjack, sidebets
#
# Outputs:
# playerHand (HandClass)

def compare_player_dealer(playerHand, dealerHand, payoffs):
    dealer_sum_cards_prim, dealer_sum_cards_sec, dealer_best_sum = sum_cards(dealerHand.hand_cards)
    player_sum_cards_prim, player_sum_cards_sec, player_best_sum = sum_cards(playerHand.hand_cards)

    if player_best_sum > 21:
        playerHand.hand_winnings['main'] = -playerHand.bets['main']
        print("\nPlayer has busted. Dealer wins.")
    
    elif dealer_best_sum > 21:
        playerHand.hand_winnings['main'] = playerHand.bets['main']
        playerHand.hand_winnings['blackjack'] = playerHand.blackjack_hand * payoffs['blackjack'] * playerHand.bets['blackjack']
        print("\nDealer has busted. Player wins.")
    
    elif dealer_best_sum >= 17:
        # Dealer has higher hand
        if dealer_best_sum > player_best_sum:
            playerHand.hand_winnings['main'] = -playerHand.bets['main']
            print("\nPlayer has a lower hand. Dealer wins.")
            
        # Equal hands
        elif dealer_best_sum == player_best_sum:
            playerHand.hand_winnings['main'] = 0.0
            playerHand.hand_winnings['blackjack'] = 0.0
            if playerHand.hand_status == 'stand_insurance':
                print("\nPlayer also has Blackjack.\nPush.")
            else:
                print("\nPush.")
            
        # Player has higher hand
        else:
            playerHand.hand_winnings['main'] = playerHand.bets['main']
            playerHand.hand_winnings['blackjack'] = playerHand.blackjack_hand * payoffs['blackjack'] * playerHand.bets['blackjack']
            print("\nPlayer wins.")
    else:
        # Code will reach here only if player has a Blackjack
        # Dealer has higher hand
        if dealer_best_sum > player_best_sum:
            playerHand.hand_winnings['main'] = -playerHand.bets['main']
            print("\nPlayer has a lower hand. Dealer wins.")
            
        # Equal hands
        elif dealer_best_sum == player_best_sum:
            playerHand.hand_winnings['main'] = 0.0
            playerHand.hand_winnings['blackjack'] = 0.0
            if playerHand.hand_status == 'stand_insurance':
                print("\nPlayer also has Blackjack.\nPush.")
            else:
                print("\nPush.")
            
        # Player has higher hand
        else:
            playerHand.hand_winnings['main'] = playerHand.bets['main']
            playerHand.hand_winnings['blackjack'] = playerHand.blackjack_hand * payoffs['blackjack'] * playerHand.bets['blackjack']
            print("\nPlayer has Blackjack. Dealer has a lower hand. Player wins.")

    return playerHand


## CHECK_PERFECT_PAIR method ##
##
# Inputs:
# player_hand_cards (list): Player's Hand of cards
# payoffs (dict)
#
# Outputs:
# payoffs (dict)
# Checks for Perfect Pairs sidebet

def check_perfect_pair(player_hand_cards, payoffs):
    if player_hand_cards[0].face == player_hand_cards[1].face and player_hand_cards[0].suit == player_hand_cards[1].suit:
        print("\nLeft sidebet WON. PERFECT PAIRS !!")
        payoffs['sidebet_L'] = 30
        return payoffs
    elif player_hand_cards[0].face == player_hand_cards[1].face:
        if player_hand_cards[0].suit in ('Diamonds','Hearts') and player_hand_cards[1].suit in ('Diamonds','Hearts'):
            print("\nLeft sidebet WON. COLOURED PAIRS !!")
            payoffs['sidebet_L'] = 12
            return payoffs
        elif player_hand_cards[0].suit in ('Clubs','Spades') and player_hand_cards[1].suit in ('Clubs','Spades'):
            print("\nLeft sidebet WON. COLOURED PAIRS !!")
            payoffs['sidebet_L'] = 12
            return payoffs
        else:
            print("\nLeft sidebet WON. MIXED PAIRS !!")
            payoffs['sidebet_L'] = 5
            return payoffs
    
    return payoffs


## CHECK_21_PLUS_3 method ##
##
# Inputs:
# player_hand_cards (list): Player's Hand of cards
# dealer_hand_cards (list): Dealer's Hand of cards
# payoffs (dict)
#
# Outputs:
# payoffs (dict)

def check_21_plus_3(player_hand_cards, dealer_hand_cards, payoffs):

    def are_cards_consecutive(hand_faces: list):
        hand_lo = sorted([(1 if face=='A' else 11 if face=='J' else 12 if face=='Q' else 13 if face=='K' else int(face)) for face in hand_faces])
        hand_hi = sorted([(14 if face=='A' else 11 if face=='J' else 12 if face=='Q' else 13 if face=='K' else int(face)) for face in hand_faces])

        # consecutive triplets are (A,2,3), (2,3,4) ... (J,Q,K) and (Q,K,A)
        if ( hand_lo[2]-hand_lo[0] == 2 and len(set(hand_lo)) == len(hand_lo) ) or \
            ( hand_hi[2]-hand_hi[0] == 2 and len(set(hand_hi)) == len(hand_lo) ):
            return True
        else:   
            return False


    card_faces = [player_hand_cards[0].face, player_hand_cards[1].face, dealer_hand_cards[0].face]
    card_suits = [player_hand_cards[0].suit, player_hand_cards[1].suit, dealer_hand_cards[0].suit]

    if len(set(card_faces)) == 1 and len(set(card_suits)) == 1:
        print("\nRight sidebet WON. SUITED THREE-OF-A-KIND !!") 
        payoffs['sidebet_R'] = 100
        return payoffs
    elif are_cards_consecutive(card_faces) and len(set(card_suits)) == 1:
        print("\nRight sidebet WON. STRAIGHT FLUSH !!")
        payoffs['sidebet_R'] = 40
        return payoffs
    elif len(set(card_faces)) == 1:
        print("\nRight sidebet WON. THREE-OF-A-KIND !!")
        payoffs['sidebet_R'] = 30
        return payoffs
    elif are_cards_consecutive(card_faces):
        print("\nRight sidebet WON. STRAIGHT !!")
        payoffs['sidebet_R'] = 10
        return payoffs
    elif len(set(card_suits)) == 1:
        print("\nRight sidebet WON. FLUSH !!")
        payoffs['sidebet_R'] = 5
        return payoffs
    
    return payoffs


## CARD class ##
##
# Attributes:
# face (string): Face of the card. e.g. 2, 3, 10, J, Q, K, A
# suit (string): Suit of the card. e.g. Hearts, Diamonds
# value_prim (int): Primary Blackjack value of the card. For 2 to 10, value is same as face. For J, Q, K value is 10. For Ace, value is 11.
# value_sec (int): Secondary Blackjack value of the card. For Ace, value is 1. For others, value is same as Primary value.

class Card:
    def __init__(self, face, suit):
        self.face = face
        self.suit = suit
        
        if self.face in ['J','Q','K']:
            self.value_prim = 10
            self.value_sec = 10
        elif self.face == 'A':
            self.value_prim = 11
            self.value_sec = 1
        else:
            self.value_prim = int(self.face)
            self.value_sec = int(self.face)

    def __str__(self):
        return '{} of {}'.format(self.face, self.suit)


## HANDCLASS class ##
##
# Attributes:
# name (string): name of Hand e.g. Hand #1, Hand #2, Dealer Hand #1
# player_action (string): H = Hit, S = Stand, D = Double down, SPLIT = split, EXIT = exit game
# hand_cards (list): All the cards in current hand
# hand_status (string): 'active' if player is hitting, 'stand_insurance' if player wins insurance, stand_blackjack' if player gets blackjack, 'stand', 'bust'
# hand_winnings (list): Winnings corresponding to each type of bet
# bets (list): Bet amounts for each type of bet
# blackjack_hand (int): 1 if hand is blackjack, 0 otherwise

class HandClass:
    def __init__(self, name):
        self.name = name
        self.player_action = ''
        self.hand_cards = []
        self.hand_status = 'active'    # active, stand, stand_insurance, stand_blackjack, bust
        self.hand_winnings = {'main':0.0, 'blackjack':0.0, 'insurance':0.0, 'sidebet_L':0.0, 'sidebet_R':0.0}
        self.bets = {'main':0.0, 'blackjack':0.0, 'insurance':0.0, 'sidebet_L':0.0, 'sidebet_R':0.0}
        self.blackjack_hand = 0     # if hand has blackjack then 1 else 0

    def __str__(self):
        show_hand_cards = "{"
        for card in self.hand_cards:
            show_hand_cards += (card.face+" of "+card.suit+", ")
        show_hand_cards = show_hand_cards[:-2] + "}"

        show_hand_winnings = "["
        for key in self.hand_winnings:
            show_hand_winnings += (key+": "+str(self.hand_winnings[key])+", ")
        show_hand_winnings = show_hand_winnings[:-2] + "]"

        show_bets = "["
        for key in self.bets:
            show_bets += (key+": "+str(self.bets[key])+", ")
        show_bets = show_bets[:-2] + "]"

        tempshow = "name: %s, player_action: %s,\nhand_cards: %s,\nhand_status: %s,\nbets: %s,\nhand_winnings: %s,\nblackjack_hand: %s" % (self.name, 
                self.player_action, show_hand_cards, self.hand_status, show_bets, show_hand_winnings, self.blackjack_hand)
        
        return tempshow


## BRO class ##
##
# Attributes:
# name (string): name of Bro. e.g. dealer, player
# balance (int): Latest balance. NULL for dealer.
# init_balance (int): Starting balance = deposited money. NULL for dealer.
# max_balance (int): Highest balance achieved. NULL for dealer.
# prev_bets (list): Bet amounts in last hand for each type of bet. Always 0 for insurance.

class Bro:
    def __init__(self, name, balance = int):
        self.name = name
        self.balance = balance
        self.init_balance = balance
        self.max_balance = balance
        self.prev_bets = {'main':0.0, 'blackjack':0.0, 'insurance':0.0, 'sidebet_L':0.0, 'sidebet_R':0.0}


#############################################################
######################## main method ########################
#############################################################

def start_game():

    print("\nWelcome to TakeMyMoney BlackJack ©\n")

    # Deposit player balance
    init_bal = '0'
    while init_bal.isnumeric() is False or int(init_bal) < 10:
        init_bal = input("Deposit Balance (minimum 10): $")

    # initializing Bros - Dealer and Player
    Dealer = Bro('dealer', None)
    Player = Bro('player', int(init_bal)*1.0)


    # PAYOFFS
    payoffs = {'blackjack':0.5, 'insurance':2.0, 'sidebet_L':0, 'sidebet_R':0}     # Blackjack payoffs are additive on main bet, i.e. BJ pays 0.5x over normal win unless push. Rest are their own payoffs.

    # initializing shoe/deck
    num_decks = 8
    suits = ['Hearts', 'Diamonds', 'Spades', 'Clubs']
    faces = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    deck = [Card(suit=suit, face=face) for i in range(num_decks) for suit in suits for face in faces]
    print('\nPlaying with %d decks in shoe' % (len(deck)/52))

    deck = shuffle_shoe(deck, 3)

    
    #######################
    ### COMMENCING HAND ###
    #######################
    
    keep_playing = 'y'
    while(keep_playing == 'y' and Player.balance >= 10):
        print("\nBalance: $%s" % Player.balance)

        if len(deck) < num_decks*52/2:
            deck = new_shoe(num_decks)

        # reinitialize
        payoffs = {'blackjack':0.5, 'insurance':2.0, 'sidebet_L':0, 'sidebet_R':0}
        playerHand1 = HandClass('Hand #1')
        setattr(Player, 'Hand1', playerHand1)
        dealerHand = HandClass('Dealer Hand #1')
        setattr(Dealer, 'Hand', dealerHand)


        # get player's bet amounts
        Player = get_player_bet(Player)
        Player.prev_bets = Player.Hand1.bets.copy()
        

        # deal first two cards to Dealer and Player
        for i in range(2):
            new_card = deck.pop(0)
            Player.Hand1.hand_cards.append(new_card)
            
            new_card = deck.pop(0)
            Dealer.Hand.hand_cards.append(new_card)
        
        # new_card = deck.pop(0)
        # Player.Hand1.hand_cards = [Card(suit='Hearts',face=new_card.face), Card(suit='Clubs',face=new_card.face)]
        # Player.Hand1.hand_cards = [Card(suit='Clubs',face='6'), Card(suit='Clubs',face='6')]
        # Dealer.Hand.hand_cards = [Card(suit='Clubs',face='6'), Card(suit='Clubs',face='3')]

        print("\nBets closed. Dealing hand ...")
        time.sleep(1.5)
        print("\nDealer:\n%s, <hidden card> (Sum: %s)" % (str(Dealer.Hand.hand_cards[0]), Dealer.Hand.hand_cards[0].value_prim))
        print("\nPlayer:")
        print_cards_bothsums(Player.Hand1.hand_cards)


        ##########################
        ### Check for Sidebets ###
        ##########################
        
        # check LEFT sidebet if player has bet on it
        if Player.Hand1.bets['sidebet_L'] != 0:
            payoffs = check_perfect_pair(Player.Hand1.hand_cards, payoffs)

            if payoffs['sidebet_L'] == 0:
                print("\nLeft sidebet LOST")
                Player.Hand1.hand_winnings['sidebet_L'] = -Player.Hand1.bets['sidebet_L']
                Player.balance += Player.Hand1.hand_winnings['sidebet_L']
            else:
                Player.Hand1.hand_winnings['sidebet_L'] = payoffs['sidebet_L'] * Player.Hand1.bets['sidebet_L']
                Player.balance += Player.Hand1.hand_winnings['sidebet_L']
                print("You win $%s" % Player.Hand1.hand_winnings['sidebet_L'])
        

        # check RIGHT sidebet if player has bet on it
        if Player.Hand1.bets['sidebet_R'] != 0:
            payoffs = check_21_plus_3(Player.Hand1.hand_cards, Dealer.Hand.hand_cards, payoffs)

            if payoffs['sidebet_R'] == 0:
                print("\nRight sidebet LOST")
                Player.Hand1.hand_winnings['sidebet_R'] = -Player.Hand1.bets['sidebet_R']
                Player.balance += Player.Hand1.hand_winnings['sidebet_R']
            else:
                Player.Hand1.hand_winnings['sidebet_R'] = payoffs['sidebet_R'] * Player.Hand1.bets['sidebet_R']
                Player.balance += Player.Hand1.hand_winnings['sidebet_R']
                print("You win $%s" % Player.Hand1.hand_winnings['sidebet_R'])


        ####################################
        ### Check for Dealer's Blackjack ###
        ####################################

        #if Dealer's face up card is Ace, offer insurance
        if Dealer.Hand.hand_cards[0].face == 'A':
            
            if Player.balance >= Player.Hand1.bets['main']*1.5:
                insurance_input = ''
                while insurance_input not in ('Y','N'):
                    insurance_input = input('\nDealer has an Ace. Do you want to buy insurance for $%d? (y/n): ' % (Player.Hand1.bets['main']/2)).upper()
                
                # if Player takes insurance
                if insurance_input == 'Y':
                    Player.Hand1.bets['insurance'] = Player.Hand1.bets['main']/2
                    print("Insurance Bought")
                    time.sleep(1.5)
            else:
                print("\nDealer has an Ace. Insufficient balance for buying insurance")
                time.sleep(1.5)

            # if Player took insurance and Dealer doesn't have blackjack, lose insurance and continue BAU
            if insurance_input == 'Y' and Dealer.Hand.hand_cards[1].value_prim != 10:
                Player.Hand1.hand_winnings['insurance'] = -Player.Hand1.bets['insurance']
                Player.balance += Player.Hand1.hand_winnings['insurance']
                print("\nDealer doesn't have Blackjack. Insurance LOST.")
            # if Player took insurance and Dealer has blackjack, win insurance and stand
            elif insurance_input == 'Y':
                Player.Hand1.hand_winnings['insurance'] = payoffs['insurance'] * Player.Hand1.bets['insurance']
                Player.balance += Player.Hand1.hand_winnings['insurance']
                Player.Hand1.player_action = 'S_IN'
                Player.Hand1.hand_status = 'stand_insurance'
                print('\nDealer has Blackjack. Insurance WON.')
            # if Player didn't take insurance and Dealer has blackjack, stand
            elif Dealer.Hand.hand_cards[1].value_prim == 10:
                Player.Hand1.player_action = 'S_IN'
                Player.Hand1.hand_status = 'stand_insurance'
                print('\nDealer has Blackjack.')
            # else (player didn't take insurance and Dealer doesn't have blackjack) continue BAU



        ##########################################################################
        ### LOOP TO DEAL CARDS TO PLAYER until player busts, gets 21 or stands ###
        ##########################################################################

        #>>>>> if player has blackjack, don't ask for input, skip to results/comparison
        #>>>>> Else if player splits, run Two hand plays
        num_hands = 1

        # If player has blackjack then stand
        if sum_cards(Player.Hand1.hand_cards)[2] == 21 and Player.Hand1.hand_status != 'stand_insurance':
            Player.Hand1.player_action = 'S_BJ'
            Player.Hand1.blackjack_hand = 1
            Player.Hand1.bets['blackjack'] = Player.Hand1.bets['main']
            Player.Hand1.hand_status = 'stand_blackjack'
            time.sleep(3)
        # Ask Hit/Stand action from player and deal card accordingly
        elif Player.Hand1.hand_status != 'stand_insurance':
            Player.Hand1.blackjack_hand = 0
            Player.Hand1.player_action = get_player_init_input(Player, Player.Hand1, num_hands)
        

        if Player.Hand1.player_action == 'SPLIT':
            num_hands += 1

            # create new hand = Hand #2. Hand #1's second card will get transferred to Hand #2.
            # Hand #2 will only have main bet (equal to Hand #1's main bet before DD) and no other bets
            playerHand2 = HandClass('Hand #2')
            playerHand2.bets['main'] = playerHand1.bets['main']
            playerHand2.hand_cards.append(Player.Hand1.hand_cards[1])
            Player.Hand1.hand_cards.pop(1)
            setattr(Player, 'Hand2', playerHand2)

            # Deal one card each to both hands
            new_card = deck.pop(0)
            Player.Hand1.hand_cards.append(new_card)
            new_card = deck.pop(0)
            Player.Hand2.hand_cards.append(new_card)
            # Player.Hand2.hand_cards.append(Card(suit='Diamonds',face='A'))
            
            print("\nPlayer Hand #1:")
            print_cards_bothsums(Player.Hand1.hand_cards)
            print("\nPlayer Hand #2:")
            print_cards_bothsums(Player.Hand2.hand_cards)

            time.sleep(3)

            # If player has blackjack on any hand, then stand on that hand
            print("\n-------------------\nPlaying Hand #1 ...")
            
            print("\nDealer:\n%s, <hidden card> (Sum: %s)" % (str(Dealer.Hand.hand_cards[0]), Dealer.Hand.hand_cards[0].value_prim))
            print("\nPlayer Hand #1:")
            print_cards_bothsums(Player.Hand1.hand_cards)

            if sum_cards(Player.Hand1.hand_cards)[2] == 21:
                Player.Hand1.player_action = 'S_BJ'
                Player.Hand1.blackjack_hand = 1
                Player.Hand1.bets['blackjack'] = Player.Hand1.bets['main']
                Player.Hand1.hand_status = 'stand_blackjack'
                time.sleep(2)
            else:
                Player.Hand1.blackjack_hand = 0
                Player.Hand1.player_action = get_player_init_input(Player, Player.Hand1, num_hands)
            
            # If player didn't "exit" then proceed
            if Player.Hand1.player_action != 'EXIT':
                Player.Hand1, deck = play_hand(Player.Hand1, deck)

                # If player didn't "exit" on Hand #1, then proceed with Hand #2
                if Player.Hand1.hand_status != 'exit':
                    time.sleep(1.5)
                    print("\n-------------------\nPlaying Hand #2 ...")
                    print("\nDealer:\n%s, <hidden card> (Sum: %s)" % (str(Dealer.Hand.hand_cards[0]), Dealer.Hand.hand_cards[0].value_prim))
                    print("\nPlayer Hand #2:")
                    print_cards_bothsums(Player.Hand2.hand_cards)

                    if sum_cards(Player.Hand2.hand_cards)[2] == 21:
                        Player.Hand2.player_action = 'S_BJ'
                        Player.Hand2.blackjack_hand = 1
                        Player.Hand2.bets['blackjack'] = Player.Hand2.bets['main']
                        Player.Hand2.hand_status = 'stand_blackjack'
                        time.sleep(2)
                    else:
                        Player.Hand2.blackjack_hand = 0
                        Player.Hand2.player_action = get_player_init_input(Player, Player.Hand2, num_hands)
                    
                    # If player didn't "exit" then proceed
                    if Player.Hand2.player_action != 'EXIT':
                        Player.Hand2, deck = play_hand(Player.Hand2, deck)
                    else:
                        Player.Hand2.hand_status = 'exit'
            else:
                Player.Hand1.hand_status = 'exit'
        
        # If player didn't SPLIT and didn't "exit"
        elif Player.Hand1.player_action != 'EXIT':
            Player.Hand1, deck = play_hand(Player.Hand1, deck)

        # If player hit "exit"
        else:
            Player.Hand1.hand_status = 'exit'


        #############################################################
        ### RESULT TIME. By now player has either Busted or Stood ###
        #############################################################

        #>>>>>>
        # IF num_hands > 2
            # if both hands are in (blackjack, bust), dealer doesn't deal himself more.
                # Show dealer cards. Compare with player's cards for result
            # else reveal dealer cards
                # If any hand is blackjack, compare with dealer now for result
                # dealer deals himself more until 17+
                # compare remaining hands with dealer
        # ELSE 
            # if hand is blackjack, dealer doesn't deal himself more.
                # Show dealer cards. Compare with player's cards for result
            # else reveal dealer cards
                # dealer deals himself more until 17+
                # compare remaining hands with dealer
        #>>>>>>
            
        time.sleep(2)

        if Player.Hand1.hand_status == 'exit' or (hasattr(Player, 'Hand2') and Player.Hand2.hand_status == 'exit'):
            Player.Hand1.hand_winnings['main'] = -Player.Hand1.bets['main']
            if hasattr(Player, 'Hand2'):
                Player.Hand2.hand_winnings['main'] = -Player.Hand2.bets['main']
            keep_playing = 'exit'
        
        # If player split hand
        elif num_hands > 1:
            hand_BJ = copy.deepcopy(Player.Hand1) if Player.Hand1.blackjack_hand == 1 else copy.deepcopy(Player.Hand2) if Player.Hand2.blackjack_hand == 1 else None
            hand_other = copy.deepcopy(Player.Hand2) if Player.Hand1.blackjack_hand == 1 else copy.deepcopy(Player.Hand1) if Player.Hand2.blackjack_hand == 1 else None

            # At least 1 hand with Blackjack
            if hand_BJ is not None:
                print("\nREVEALING DEALER'S CARDS")

                # Reveal Dealer's both cards
                print("\nDealer:")
                print_cards_bestsum(Dealer.Hand.hand_cards)
                print("\nPlayer %s:" % hand_BJ.name)
                print_cards_bestsum(hand_BJ.hand_cards)
                
                # Compare Blackjack hand with Dealer
                time.sleep(1)
                hand_BJ = compare_player_dealer(hand_BJ, Dealer.Hand, payoffs)
                if hand_BJ.name == 'Hand #1':
                    Player.Hand1 = copy.deepcopy(hand_BJ)
                else:
                    Player.Hand2 = copy.deepcopy(hand_BJ)
                

                # If other hand is Blackjack or Bust, don't deal cards to Dealer. Directly compare.
                if hand_other.hand_status in ('stand_blackjack','bust'):
                    time.sleep(1)
                    print("\nPlayer %s:" % hand_other.name)
                    print_cards_bestsum(hand_other.hand_cards)
                
                    time.sleep(1)
                    hand_other = compare_player_dealer(hand_other, Dealer.Hand, payoffs)
                    if hand_other.name == 'Hand #1':
                        Player.Hand1 = copy.deepcopy(hand_other)
                    else:
                        Player.Hand2 = copy.deepcopy(hand_other)

                # If other card is neither Blackjack nor Bust, then Dealer takes cards. Then compare.
                else:
                    time.sleep(1)
                    print("\nDealer:")
                    print_cards_bestsum(Dealer.Hand.hand_cards)
                    print("\nPlayer %s:" % hand_other.name)
                    print_cards_bestsum(hand_other.hand_cards)

                    # Dealer deals cards to himself
                    dealer_card_count = 2
                    while (sum_cards(Dealer.Hand.hand_cards)[2] < 17):
                        print("\nDealer picking card #%s" % (dealer_card_count+1))
                        time.sleep(2)

                        new_card = deck.pop(0)
                        Dealer.Hand.hand_cards.append(new_card)

                        print("\nDealer:")
                        print_cards_bestsum(Dealer.Hand.hand_cards)
                        print("\nPlayer %s:" % hand_other.name)
                        print_cards_bestsum(hand_other.hand_cards)

                        dealer_card_count += 1

                    time.sleep(1)
                    hand_other = compare_player_dealer(hand_other, Dealer.Hand, payoffs)
                    if hand_other.name == 'Hand #1':
                        Player.Hand1 = copy.deepcopy(hand_other)
                    else:
                        Player.Hand2 = copy.deepcopy(hand_other)

                ## NOW SKIP TO PRINTING WINNINGS
            
            # If both hands are bust, don't deal cards to Dealer. Just compare                        
            elif Player.Hand1.hand_status == Player.Hand2.hand_status == 'bust':
                print("\nREVEALING DEALER'S CARDS")

                # Reveal Dealer's both cards
                print("\nDealer:")
                print_cards_bestsum(Dealer.Hand.hand_cards)
                print("\nPlayer Hand #1:")
                print_cards_bestsum(Player.Hand1.hand_cards)
                
                # Compare both hands to Dealer's
                time.sleep(1)
                Player.Hand1 = compare_player_dealer(Player.Hand1, Dealer.Hand, payoffs)
                
                time.sleep(2)
                print("\nPlayer Hand #2:")
                print_cards_bestsum(Player.Hand2.hand_cards)
                
                time.sleep(1)
                Player.Hand2 = compare_player_dealer(Player.Hand2, Dealer.Hand, payoffs)
            
            # If neither hand has Blackjack and at least one hand is not bust, then Dealer takes cards. Then compare both hands.
            else:
                print("\nREVEALING DEALER'S CARDS")

                # Reveal Dealer's both cards
                print("\nDealer:")
                print_cards_bestsum(Dealer.Hand.hand_cards)
                
                time.sleep(1)
                # Dealer deals cards to himself
                dealer_card_count = 2
                while (sum_cards(Dealer.Hand.hand_cards)[2] < 17):
                    print("\nDealer picking card #%s" % (dealer_card_count+1))
                    time.sleep(2)

                    new_card = deck.pop(0)
                    Dealer.Hand.hand_cards.append(new_card)

                    print("\nDealer:")
                    print_cards_bestsum(Dealer.Hand.hand_cards)

                    dealer_card_count += 1

                # Compare both hands to Dealer's
                time.sleep(1)
                print("\nPlayer Hand #1:")
                print_cards_bestsum(Player.Hand1.hand_cards)
                Player.Hand1 = compare_player_dealer(Player.Hand1, Dealer.Hand, payoffs)

                time.sleep(1)
                print("\nPlayer Hand #2:")
                print_cards_bestsum(Player.Hand2.hand_cards)
                Player.Hand2 = compare_player_dealer(Player.Hand2, Dealer.Hand, payoffs)
        
        # If player did not split hand
        else:
            # If Player stood - now dealer deals cards to himself until best allowable sum is 17 or higher.
            if Player.Hand1.hand_status in ('stand_blackjack', 'stand', 'stand_insurance', 'bust'):
                print("\nREVEALING DEALER'S CARDS")
                time.sleep(2)

                # Reveal Dealer's both cards
                print("\nDealer:")
                print_cards_bestsum(Dealer.Hand.hand_cards)
                print("\nPlayer:")
                print_cards_bestsum(Player.Hand1.hand_cards)
                
                time.sleep(1)
                
                # If Player didn't bust or didn't get blackjack, Dealer deals cards to himself
                if Player.Hand1.hand_status not in ('stand_blackjack','bust'):
                    dealer_card_count = 2
                    while (sum_cards(Dealer.Hand.hand_cards)[2] < 17):
                        print("\nDealer picking card #%s" % (dealer_card_count+1))
                        time.sleep(2)

                        new_card = deck.pop(0)
                        Dealer.Hand.hand_cards.append(new_card)

                        print("\nDealer:")
                        print_cards_bestsum(Dealer.Hand.hand_cards)
                        print("\nPlayer:")
                        print_cards_bestsum(Player.Hand1.hand_cards)

                        dealer_card_count += 1
                    time.sleep(1)

                Player.Hand1 = compare_player_dealer(Player.Hand1, Dealer.Hand, payoffs)

            else:
                print("\nWTF_1 !?")


        ######################################################
        ### Calculate and Display each hand's net winnings ###
        ######################################################

        time.sleep(2)

        hand1_winnings = sum(Player.Hand1.hand_winnings.values())
        this_hand_winnings = hand1_winnings
        
        hand1_win_str = "$"+str(hand1_winnings) if hand1_winnings >= 0 else "-$"+str(-hand1_winnings)
        insurance_win = Player.Hand1.hand_winnings['insurance']
        sidebet_L_win = Player.Hand1.hand_winnings['sidebet_L']
        sidebet_R_win = Player.Hand1.hand_winnings['sidebet_R']

        # Display Hand #1 winnings
        print("")
        if hasattr(Player, 'Hand2'):
            print("----------------\nHAND #1 WINNINGS\n----------------")
        if insurance_win != 0:
            ins_win_str = "$"+str(insurance_win) if insurance_win>=0 else "-$"+str(-insurance_win)
            print("Insurance win: %s" % ins_win_str)
        if sidebet_L_win != 0:
            sideL_win_str = "$"+str(sidebet_L_win) if sidebet_L_win>=0 else "-$"+str(-sidebet_L_win)
            print("Left Sidebet win: %s" % sideL_win_str)
        if sidebet_R_win != 0:
            sideR_win_str = "$"+str(sidebet_R_win) if sidebet_R_win>=0 else "-$"+str(-sidebet_R_win)
            print("Right Sidebet win: %s" % sideR_win_str)
        
        main_bet_win = Player.Hand1.hand_winnings['main'] + Player.Hand1.hand_winnings['blackjack']
        main_win_str = "$"+str(main_bet_win) if main_bet_win >= 0 else "-$"+str(-main_bet_win)
        print("Main bet win: %s" % main_win_str)

        Player.balance += main_bet_win

        # Display Hand #2 winnings if Hand #2 exists
        hand2_winnings = 0
        if hasattr(Player, 'Hand2'):
            print("----------------\nTotal: %s" % hand1_win_str)
            
            hand2_winnings = sum(Player.Hand2.hand_winnings.values())
            hand2_win_str = "$"+str(hand2_winnings) if hand2_winnings >= 0 else "-$"+str(-hand2_winnings)
            print("\n----------------\nHAND #2 WINNINGS\n----------------")
            print("Total: %s\n" % hand2_win_str)
        
            this_hand_winnings += hand2_winnings
            Player.balance += hand2_winnings

        
        Player.max_balance = Player.balance if Player.balance > Player.max_balance else Player.max_balance
        
        net_hand_win_str = "$"+str(this_hand_winnings) if (this_hand_winnings) >= 0 else "-$"+str(-this_hand_winnings)
        print("------------------------------\nNet Hand Winnings: %s \nBalance: $%s" % (net_hand_win_str, Player.balance))

        # If Hand2 exists, delete it from Player
        if hasattr(Player,'Hand2'):
            delattr(Player,'Hand2')

        # print("\nRemaining cards in deck: ", len(deck))

        # User input for next round
        if keep_playing != 'exit':
            next_round = ''
            while next_round not in ('y','n') and Player.balance >= 10:
                next_round = input("\nPlay another hand (y/n): ")
            
            keep_playing = next_round

        os.system('cls')


    ## display net winnings, max balance and final balance at exit
    net_win = Player.balance - Player.init_balance

    if net_win < 0:
        print("\n---- Exiting Game ----\n\nNet Winnings: -$%s" % -net_win)
        print("Highest Balance achieved: $%s" % Player.max_balance)
        print("\n----------------------\nFinal Balance: $%s\n----------------------" % Player.balance)
        print("\nThanks for donating your money to TakeMyMoney BlackJack ©. AHAHA YIPPIKAYAY MADAF... ;D \n")
    else:
        print("\n---- Exiting Game ----\n\nNet Winnings: $%s" % net_win)
        print("Highest Balance achieved: $%s" % Player.max_balance)
        print("\n----------------------\nFinal Balance: $%s\n----------------------" % Player.balance)
        print("\nThank you for playing with TakeMyMoney BlackJack © \n")

    return


start_game()

