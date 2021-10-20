# BattleshAPy
The Python SDK for the BattleshAPI game

## Installation
This library will be eventually going on PyPI, but until then, simply clone or download this repository to use. 
The directory structure should look like this:

```
 BattleshAPy/
 main.py
```

Where `main.py` is whatever you have called your main Python script.

## Basic Usage
First sign up on https://battleshapi.pythonanywhere.com/ and create a bot. From there, you can use any of the three blocks of code to get started:

### Creating a Game
```python
import BattleshAPy


class MyGame(BattleshAPy.Game):
    def on_turn_start(self):
        pass


game = BattleshAPy.BattleshAPy(
    client_id="client_id",
    client_secret="client_secret"
).create_game(MyGame)
```

### Joining a Game
```python
import BattleshAPy


class MyGame(BattleshAPy.Game):
    def on_turn_start(self):
        pass


game = BattleshAPy.BattleshAPy(
    client_id="client_id",
    client_secret="client_secret"
).join_game(MyGame, "game_id")
```

### Attaching to a Game You Have Already Joined
```python
import BattleshAPy


class MyGame(BattleshAPy.Game):
    def on_turn_start(self):
        pass


game = BattleshAPy.BattleshAPy(
    client_id="client_id",
    client_secret="client_secret"
).connect_game(MyGame, "game_id", "token")
```

### Making Your Bot Do Something
The `on_turn_start` method of your bot is called whenever your bot's turn begins. 
When this method is finished, your turn is automatically ended

Simply add whatever code you would like to this method in order to make your bot do things!