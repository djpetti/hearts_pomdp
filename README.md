# Hearts POMDP

A POMDP that plays a two-player Hearts variation.

## What is two-player hearts?

For the two-player variation of hearts, all cards are removed except twos, fours, sixes, eights,
tens, queens, and aces. 13 of each of the remaining 28 cards are dealt to each player,
and the remaining two cards are not used in the game.

## How does the POMDP work?

The POMDP uses a rather naive formulation in which the opponent is modeled as part of the
environment, and takes random actions (as allowed by the rules).

## How do I install/run it?

To run this code, you must first have Python 3.9 installed, as well as
[Poetry](https://python-poetry.org/).

To build the virtualenv and install dependencies, run:
```
poetry install --no-root
```

## Running the Planner

`plan_hearts.py` is an example script that plans a policy and uses it to play a
single game of hearts. Policy planning is done online, so the policy is updated after
each observation is received. It can be run as follows:

```
poetry run python plan_hearts.py
```

## Running the Simulator

If you want to play against the agent, you can do that through a simulator:

```
poetry run python -m simulator
```
