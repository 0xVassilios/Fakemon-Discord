<div align="center">
    <br />
    <p>
        <img src="https://i.imgur.com/zzQcW4H.png">
        <br />
        <img src="https://img.shields.io/github/issues/VasVog/Fakemon-Discord.svg">
        <img src="https://img.shields.io/github/stars/VasVog/Fakemon-Discord.svg">
        <img src="https://img.shields.io/github/last-commit/VasVog/Fakemon-Discord.svg">
    </p>
</div>

Fakemon refers to non-canonical Pokemon character sprites and artworks created by fans of the popular Japanese franchise. This is a discord bot which utilises some of those characters to create a new Pokemon-like experience for old and new fans alike. This project was made for Discord Hack Week 2019 and we hope that you like our little project.

OFFICIAL DISCORD SERVER: https://discordapp.com/invite/yUtXM8F

## Features
- Over 1.500 Fakemon which you can capture and train!
- Over 500 moves which you add to your Fakemon.
- A Pokedex to retrieve information about any Fakemon you desire.
- Answer trivia questions in order to capture wild Fakemon!
- A global trading system.
- Are you busy with something? Go on an adventure and gain EXP by AFKing.
- Evolve your Fakemon into better versions of themselves.
- Duel with your friends to see who's the best trainer.
- An automated ever-updating shop which you can purchase items and moves from.

## Screenshots
![image](https://i.imgur.com/vofYrAf.png)
![image](https://i.imgur.com/cZqvlEG.png)
![image](https://i.imgur.com/gwG0MoE.png)
![image](https://i.imgur.com/cW8klAD.png)
![image](https://i.imgur.com/2JTI62D.png)
![image](https://i.imgur.com/DjEr3S3.png)
![image](https://i.imgur.com/w7t4CUX.png)

## Commands
- duel (user) : Duels another user in a predetermined category using your primary Fakemon.
- equip (fakemon) : Equips a fakemon to be your primary one.
- explore : Displays information about AFK exploring.
  - explore start (duration) : Starts AFK exploring.
  - explore status : Displays the remaining time for your exploration.
- inventory : Displays information about your inventory.
  - inventory fakemon (page) : Displays all your current fakemon in pages.
  - inventory items (page) : Displays all your current items in pages.
- inventory moves (page) : Displays all your current moves in pages.
  - money : Displays your money.
- pay (user) (amount) : Pays another user.
- pokedex (fakemon) : Displays information about said fakemon.
- set location (event) (channel/category) [Admin Usage] : Sets the events to happen in location.
- set [Admin Usage] : Dislays information about the set command.
  - shop : Displays all available items for purchase in the shop.
  - shop buy (item) : Buys an item from the shop.
- starter : Displays all available starters.
  - starter choose (fakemon) : Chooses a fakemon as your starter.
- stats (fakemon) : Displays the stats for an owned fakemon.
- teach (fakemon) (move) : Teaches your selected Fakemon a move, if compatible.
- trade (your fakemon) (user) (user's fakemon) : Trades Fakemon.

## How to set it up.
1. Download all the files in the repository.
2. Download PostgreSQL.
3. Make a database called "fakemon" then import the .dump file using psql.
4. Download Python.
5. Download all the libraries required.
6. Rename "passwords_example.json" to "passwords.json".
7. Open "passwords.json" and add your password.
8. Open a terminal and type "python main.py"


## Credits
**Coder**: VasVog (Vassilios#4451)

**Sprites**: ReallyDarkandWindie (https://www.deviantart.com/reallydarkandwindie)

Special thank you to ReallyDarkandWindie for all the effort he has put into all those sprites and also for allowing others to use them!
