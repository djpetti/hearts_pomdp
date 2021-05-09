import random
from pathlib import Path
from tkinter import Canvas, PhotoImage, Tk

_MODULE_DIR = Path(__file__).parent
"""
Location of this module.
"""
_ASSET_DIR = _MODULE_DIR / "assets"
"""
Location of the assets for this game.
"""


class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        val = ""
        suit = ""

        if self.suit == "Clubs":
            suit = "C"
        elif self.suit == "Hearts":
            suit = "H"
        elif self.suit == "Diamonds":
            suit = "D"
        else:
            suit = "S"

        if self.value == "Queen":
            val = "Q"
        elif self.value == "Ace":
            val = "A"
        else:
            val = str(self.value)

        asset_path = _ASSET_DIR / f"{val}{suit}.png"
        photo = PhotoImage(file=asset_path.as_posix())
        self.image = photo.subsample(6, 6)

    def get_value(self):
        return self.value

    def get_suit(self):
        return self.suit

    def get_description(self):
        return self.value + " of " + self.suit

    def get_image(self):
        return self.image


class Deck:
    def __init__(self):
        self.deck = []
        self.dropped_cards = []
        self.heart_count = 7

        self.deck.append(Card("Hearts", "2"))
        self.deck.append(Card("Diamonds", "2"))
        self.deck.append(Card("Clubs", "2"))
        self.deck.append(Card("Spades", "2"))
        self.deck.append(Card("Hearts", "4"))
        self.deck.append(Card("Diamonds", "4"))
        self.deck.append(Card("Clubs", "4"))
        self.deck.append(Card("Spades", "4"))
        self.deck.append(Card("Hearts", "6"))
        self.deck.append(Card("Diamonds", "6"))
        self.deck.append(Card("Clubs", "6"))
        self.deck.append(Card("Spades", "6"))
        self.deck.append(Card("Hearts", "8"))
        self.deck.append(Card("Diamonds", "8"))
        self.deck.append(Card("Clubs", "8"))
        self.deck.append(Card("Spades", "8"))
        self.deck.append(Card("Hearts", "10"))
        self.deck.append(Card("Diamonds", "10"))
        self.deck.append(Card("Clubs", "10"))
        self.deck.append(Card("Spades", "10"))
        self.deck.append(Card("Hearts", "Queen"))
        self.deck.append(Card("Diamonds", "Queen"))
        self.deck.append(Card("Clubs", "Queen"))
        self.deck.append(Card("Spades", "Queen"))
        self.deck.append(Card("Hearts", "Ace"))
        self.deck.append(Card("Diamonds", "Ace"))
        self.deck.append(Card("Clubs", "Ace"))
        self.deck.append(Card("Spades", "Ace"))
        photo = PhotoImage(file=(_ASSET_DIR / "red_back.png").as_posix())
        self.back_image = photo.subsample(6, 6)

    def shuffle(self):
        random.shuffle(self.deck)

    def get_deck(self):
        return self.deck

    def get_card_back_image(self):
        return self.back_image

    def get_dropped_cards(self):
        return self.dropped_cards

    def pop_top_card(self):
        if len(self.deck) == 0:
            print("The deck is already empty...")
            return
        return self.deck.pop()

    def deal_cards(self, players):
        hand = Hand(self.deck[0:13])
        players[0].set_cards(hand)
        hand2 = Hand(self.deck[13:26])
        players[1].set_cards(hand2)
        for card in self.deck[0:26]:
            self.deck.remove(card)

    def randomly_drop_cards(self, num=2):
        if num > len(self.deck):
            print("Cannot drop more cards than are in the deck...")
            return

        for i in range(num):
            if self.deck[i].get_suit() == "Hearts":
                self.heart_count -= 1

            drop_index = int(random.random() * (len(self.deck)))
            self.dropped_cards.append(self.deck.pop(drop_index))

    def get_heart_count(self):

        return self.heart_count

    def collect_cards_and_shuffle(self, shuffle=True):
        self.deck.clear()

        self.deck.append(Card("Hearts", "2"))
        self.deck.append(Card("Diamonds", "2"))
        self.deck.append(Card("Clubs", "2"))
        self.deck.append(Card("Spades", "2"))
        self.deck.append(Card("Hearts", "4"))
        self.deck.append(Card("Diamonds", "4"))
        self.deck.append(Card("Clubs", "4"))
        self.deck.append(Card("Spades", "4"))
        self.deck.append(Card("Hearts", "6"))
        self.deck.append(Card("Diamonds", "6"))
        self.deck.append(Card("Clubs", "6"))
        self.deck.append(Card("Spades", "6"))
        self.deck.append(Card("Hearts", "8"))
        self.deck.append(Card("Diamonds", "8"))
        self.deck.append(Card("Clubs", "8"))
        self.deck.append(Card("Spades", "8"))
        self.deck.append(Card("Hearts", "10"))
        self.deck.append(Card("Diamonds", "10"))
        self.deck.append(Card("Clubs", "10"))
        self.deck.append(Card("Spades", "10"))
        self.deck.append(Card("Hearts", "Queen"))
        self.deck.append(Card("Diamonds", "Queen"))
        self.deck.append(Card("Clubs", "Queen"))
        self.deck.append(Card("Spades", "Queen"))
        self.deck.append(Card("Hearts", "Ace"))
        self.deck.append(Card("Diamonds", "Ace"))
        self.deck.append(Card("Clubs", "Ace"))
        self.deck.append(Card("Spades", "Ace"))

        if shuffle:
            self.shuffle()


class Hand:
    def __init__(self, cards):
        self.hand = cards

    def remove_card(self, Card):
        if Card not in self.hand:
            print("You cannot remove a card that is not in your hand...")
            return
        self.hand.remove(Card)

    def get_hand(self):
        return self.hand

    def contains_suit(self, suit):
        for card in self.hand:
            if card.get_suit() == suit:
                return True
        return False

    def get_lowest_club(self):
        lowest = 1000
        for card in self.hand:
            if (
                card.get_value() == "Ace"
                or card.get_value() == "King"
                or card.get_value() == "Queen"
                or card.get_value() == "Jack"
            ):
                continue
            if card.get_suit() == "Clubs" and int(card.get_value()) < lowest:
                lowest = int(card.get_value())
        return lowest

    def print_hand(self):
        for card in self.hand:
            print(card.get_description())

    def get_card_count(self):
        return len(self.hand)


class Player:
    def __init__(self, name):
        self.hand = None
        self.points = 0
        self.name = name
        self.won_cards = []

    def add_points(self, points):
        self.points += points

    def get_points(self):
        return self.points

    def set_cards(self, cards):
        self.hand = cards

    def set_won_cards(self, cards):
        for card in cards:
            self.won_cards.append(card)

    def get_won_cards(self):
        return self.won_cards

    def empty_won_cards(self):
        self.won_cards = []

    def get_name(self):
        return self.name

    def get_hand(self):
        return self.hand


class Trick:
    def __init__(self):
        self.card_dict = {}
        self.first_to_play = None
        self.winner = None

    def remove_cards_from_players_hands(self):
        players = list((self.card_dict.keys()))
        cards = list(self.card_dict.values())

        for i in range(len(players)):
            players[i].get_hand().remove_card(cards[i])

    def add_card_to_trick(self, card, player):
        self.card_dict[player] = card
        if self.first_to_play is None:
            self.first_to_play = player

    def get_trick(self):
        return self.card_dict

    def get_cards(self):
        return list(self.card_dict.values())

    def reset(self):
        self.card_dict = {}
        self.first_to_play = None
        self.winner = None

    def get_winner(self):

        cards = list(self.card_dict.values())
        players = list((self.card_dict.keys()))

        val1 = cards[0].get_value()
        val2 = cards[1].get_value()

        if val1 == "Queen":
            val1 = 11
        elif val1 == "Ace":
            val1 = 12
        else:
            val1 = int(val1)

        if val2 == "Queen":
            val2 = 11
        elif val2 == "Ace":
            val2 = 12
        else:
            val2 = int(val2)

        if cards[0].get_suit() == cards[1].get_suit():
            if val1 > val2:
                self.winner = players[0]
                self.winner.set_won_cards(cards)
                return self.winner.get_name()
            else:
                self.winner = players[1]
                self.winner.set_won_cards(cards)
                return self.winner.get_name()
        else:
            self.winner = self.first_to_play
            self.winner.set_won_cards(cards)
            return self.winner.get_name()


class Game:
    def __init__(self):
        # creating tkinter window
        root = Tk()
        root.title("Hearts")
        root.geometry("2000x1000")
        self.root = root

        c = Canvas(root, width=1900, height=950)
        c.place(x=50, y=50)

        player = Player("Tom")
        computer = Player("Computer")

        self.players = [player, computer]

    def get_players(self):
        return self.players

    def get_root(self):
        return self.root
