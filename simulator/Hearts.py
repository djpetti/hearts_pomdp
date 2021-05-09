import random
from tkinter import StringVar, mainloop
from tkinter.ttk import Button, Label, OptionMenu

import classes


def continue_game():
    global player_first
    if not player_first:
        computer_turn()
    else:
        update_player_text("Alright, player it's your turn! Pick a Card.")


def players_turn(card):
    global player_has_chosen_card_for_this_trick
    if card == "pass" or player_has_chosen_card_for_this_trick:
        return

    global leading_suit
    global player_first
    global hearts_broken
    global first_play

    if not player_first:
        if card.get_suit() != leading_suit:
            if player.hand.contains_suit(leading_suit):
                update_player_text(
                    "You much match the leading suit! Try again."
                )
                return
    else:

        if (
            first_play
            and card.get_suit() != "Clubs"
            and player.get_hand().contains_suit("Clubs")
        ):
            update_player_text(
                "The first card of the game must be a Club! Try again."
            )
            return

        if card.get_suit() == "Hearts":
            if not hearts_broken:
                if (
                    player.get_hand().contains_suit("Spades")
                    or player.get_hand().contains_suit("Clubs")
                    or player.get_hand().contains_suit("Diamonds")
                ):
                    update_player_text(
                        "Hearts, Haven't been broken yet! Try again."
                    )
                    return

        leading_suit = card.get_suit()

    if card.get_suit() == "Hearts":
        hearts_broken = True

    first_play = False

    update_player_text("Player played the " + card.get_description() + "!")

    player_has_chosen_card_for_this_trick = True

    trick.add_card_to_trick(card, player)

    image = card.get_image()
    trick_card_buttons[card.get_description()] = Button(
        game.get_root(),
        image=image,
        command=lambda: players_turn("pass"),
        width=1,
    )
    trick_card_buttons[card.get_description()].place(x=815, y=530)

    player_card_buttons.get(card.get_description()).destroy()
    del player_card_buttons[card.get_description()]

    if not player_first:

        winner = trick.get_winner()

        if winner == "Tom":
            player_first = True
        else:
            player_first = False

        if winner == "Tom":
            update_game_text(
                "Player won this trick and will start the next one!"
            )
        else:
            update_game_text(
                "Computer won this trick and will start the next one!"
            )

        if len(player.get_hand().get_hand()) == 1:
            calculate_scores(player, computer)
            next_trick_button = Button(
                game.get_root(),
                text="Start Next Round",
                command=lambda: start_new_round(next_trick_button),
            )
            next_trick_button.place(x=150, y=580)

            if winner == "Tom":
                update_game_text("Player won this trick!")
            else:
                update_game_text("Computer won this trick!")

        else:

            next_trick_button = Button(
                game.get_root(),
                text="Start Next Trick",
                command=lambda: next_trick(next_trick_button),
            )
            next_trick_button.place(x=150, y=580)

    else:
        computer_turn()


def next_trick(next_trick_button):
    trick_cards = trick.get_cards()

    global player_has_chosen_card_for_this_trick
    player_has_chosen_card_for_this_trick = False

    for card in trick_cards:
        trick_card_buttons.get(card.get_description()).destroy()
        del trick_card_buttons[card.get_description()]

    trick.remove_cards_from_players_hands()
    trick.reset()
    next_trick_button.destroy()

    remove_all_text()

    continue_game()


def computer_turn():
    cards = computer.get_hand().get_hand()
    rand = int(random.random() * len(cards))
    global hearts_broken
    global player_first
    global leading_suit
    global first_play

    card = cards[rand]

    if player_first:
        if card.get_suit() != leading_suit:
            if computer.get_hand().contains_suit(leading_suit):
                computer_turn()
                return
    else:
        if (
            first_play
            and card.get_suit() != "Clubs"
            and computer.get_hand().contains_suit("Clubs")
        ):
            computer_turn()
            return

        if card.get_suit() == "Hearts":
            if not hearts_broken:
                if (
                    computer.get_hand().contains_suit("Spades")
                    or computer.get_hand().contains_suit("Clubs")
                    or computer.get_hand().contains_suit("Diamonds")
                ):
                    computer_turn()
                    return
        leading_suit = card.get_suit()

    if card.get_suit() == "Hearts":
        hearts_broken = True

    first_play = False
    update_computer_text("Computer played the " + card.get_description() + "!")

    trick.add_card_to_trick(card, computer)

    computer_card_buttons.get(card.get_description()).destroy()
    del computer_card_buttons[card.get_description()]

    image = card.get_image()

    trick_card_buttons[card.get_description()] = Button(
        game.get_root(),
        image=image,
        command=lambda: players_turn("pass"),
        width=1,
    )
    trick_card_buttons[card.get_description()].place(x=815, y=280)

    if player_first:

        winner = trick.get_winner()

        if winner == "Tom":
            player_first = True
        else:
            player_first = False

        if winner == "Tom":
            update_game_text(
                "Player won this trick and will start the next one!"
            )
        else:
            update_game_text(
                "Computer won this trick and will start the next one!"
            )

        if len(player.get_hand().get_hand()) == 1:
            calculate_scores(player, computer)
            next_trick_button = Button(
                game.get_root(),
                text="Start Next Round",
                command=lambda: start_new_round(next_trick_button),
            )
            next_trick_button.place(x=150, y=580)

            if winner == "Tom":
                update_game_text("Player won this trick!")
            else:
                update_game_text("Computer won this trick!")

        else:

            next_trick_button = Button(
                game.get_root(),
                text="Start Next Trick",
                command=lambda: next_trick(next_trick_button),
            )
            next_trick_button.place(x=150, y=580)
    else:
        update_player_text("Alright, player it's your turn! Pick a Card.")


def start_game():
    global player_first

    if (
        player.get_hand().get_lowest_club()
        < computer.get_hand().get_lowest_club()
    ):
        player_first = True
    else:
        player_first = False
    show_hand(player.get_hand().get_hand(), game.get_root())
    show_hand(computer.get_hand().get_hand(), game.get_root(), "computer")
    update_scores(player.get_points(), computer.get_points())
    continue_game()


def create_card_button(x, y, card, photo, root, player):

    if player == "player":
        player_card_buttons[card.get_description()] = Button(
            root, image=photo, command=lambda: players_turn(card), width=1
        )
        player_card_buttons.get(card.get_description()).place(x=x, y=y)

    else:
        computer_card_buttons[card.get_description()] = Button(
            root, image=photo, command=lambda: players_turn("pass"), width=1
        )
        computer_card_buttons.get(card.get_description()).place(x=x, y=y)


def show_hand(hand, root, player="player"):
    if player == "player":
        for i in range(len(hand)):
            photo = hand[i].get_image()

            create_card_button(
                5 + (i * 135), 750, hand[i], photo, root, "player"
            )

    if player == "computer":
        for i in range(len(hand)):
            photo = deck.get_card_back_image()

            create_card_button(
                5 + (i * 135), 50, hand[i], photo, root, "computer"
            )


def update_player_text(text):
    global player_label
    player_label.destroy()
    player_label = Label(game.get_root(), text=text, font=("Arial", 22))
    player_label.place(x=100, y=670)


def update_computer_text(text):
    global computer_label
    computer_label.destroy()
    computer_label = Label(game.get_root(), text=text, font=("Arial", 22))
    computer_label.place(x=100, y=300)


def update_game_text(text):
    global game_label
    game_label.destroy()
    game_label = Label(game.get_root(), text=text, font=("Arial", 28))
    game_label.place(x=100, y=485)


def remove_all_text():
    game_label.destroy()
    player_label.destroy()
    computer_label.destroy()


def update_scores(player_score, computer_score):
    global player_score_label
    global computer_score_label

    player_score_label.destroy()
    player_score_label = Label(
        game.get_root(), text="Score: " + str(player_score), font=("Arial", 28)
    )
    player_score_label.place(x=1630, y=710)

    computer_score_label.destroy()
    computer_score_label = Label(
        game.get_root(),
        text="Score: " + str(computer_score),
        font=("Arial", 28),
    )
    computer_score_label.place(x=1630, y=250)


def calculate_scores(player, computer):
    player_cards_won = player.get_won_cards()
    computer_cards_won = computer.get_won_cards()

    print(
        len(player_cards_won) + len(computer_cards_won), deck.get_heart_count()
    )

    heart_count = 0

    for card in player_cards_won:
        if card.get_suit() == "Hearts":
            heart_count += 1

    for card in computer_cards_won:
        if card.get_suit() == "Hearts":
            heart_count += 1

    player_score = 0
    computer_score = 0
    player_shot_the_moon = True
    computer_shot_the_moon = True

    for card in player_cards_won:
        if card.get_suit() == "Hearts":
            computer_shot_the_moon = False
            player_score += 1
        elif card.get_description() == "Queen of Spades":
            player_score += queen_of_spades_value
            computer_shot_the_moon = False

    for card in computer_cards_won:
        if card.get_suit() == "Hearts":
            player_shot_the_moon = False
            computer_score += 1
        elif card.get_description() == "Queen of Spades":
            computer_score += queen_of_spades_value
            computer_shot_the_moon = False

    if player_shot_the_moon:
        computer_score = heart_count + queen_of_spades_value
        player_score = 0
    elif computer_shot_the_moon:
        player_score = heart_count + queen_of_spades_value
        computer_score = 0

    player.add_points(player_score)
    computer.add_points(computer_score)

    update_scores(player.get_points(), computer.get_points())


def start_new_round(next_trick_button):
    global deck
    global leading_suit
    global hearts_broken
    global first_play
    global player_has_chosen_card_for_this_trick
    next_trick_button.destroy()
    deck = classes.Deck()
    deck.shuffle()
    deck.randomly_drop_cards()
    deck.deal_cards([player, computer])
    leading_suit = "Clubs"
    hearts_broken = False
    first_play = True
    player_has_chosen_card_for_this_trick = False

    trick_cards = trick.get_cards()

    for card in trick_cards:
        trick_card_buttons.get(card.get_description()).destroy()
        del trick_card_buttons[card.get_description()]

    trick.remove_cards_from_players_hands()
    trick.reset()

    remove_all_text()

    global current_round
    if current_round < int(number_of_rounds):
        current_round += 1
    else:

        if player.get_points() < computer.get_points():
            winner = "Player"
        else:
            winner = "Computer"

        label = Label(
            game.get_root(),
            text="Game Over! " + winner + " has won the game.",
            font=("Arial", 25),
        )
        label.place(x=650, y=450)
        return

    start_game()


def delete_ask_button_and_start_game(start_game_button, drop, label):
    global number_of_rounds
    global clicked
    number_of_rounds = clicked.get()
    drop.destroy()
    label.destroy()
    start_game_button.destroy()
    start_game()


trick = classes.Trick()

player_first = True

player_has_chosen_card_for_this_trick = False

player_card_buttons = {}
computer_card_buttons = {}
trick_card_buttons = {}

leading_suit = "Clubs"
hearts_broken = False

game = classes.Game()

player_label = Label(game.get_root(), text="")
computer_label = Label(game.get_root(), text="")
game_label = Label(game.get_root(), text="")

player_score_label = Label(game.get_root(), text="")
computer_score_label = Label(game.get_root(), text="")

players = game.get_players()
player = players[0]
computer = players[1]

deck = classes.Deck()
deck.shuffle()

deck.randomly_drop_cards()
deck.deal_cards([player, computer])

player_goes = True
first_play = True

queen_of_spades_value = 7

number_of_rounds = 5

current_round = 1

round_options = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
]

# datatype of menu text
clicked = StringVar()

# initial menu text
clicked.set("5")

# Create Dropdown menu
drop = OptionMenu(game.get_root(), clicked, *round_options)
drop.place(x=1010, y=450)

# Create Label
label = Label(game.get_root(), text=" How many rounds would you like to play?")
label.place(x=740, y=450)

start_game_button = Button(
    game.get_root(),
    text="Play Hearts!",
    command=lambda: delete_ask_button_and_start_game(
        start_game_button, drop, label
    ),
)
start_game_button.place(x=840, y=500)

mainloop()
