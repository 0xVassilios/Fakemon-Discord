from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import random
import requests
import json
from io import BytesIO

with open("pokedex.json", "r", encoding="UTF8") as file:
    pokedex = json.load(file)

pokemon_one = random.choice(list(pokedex.keys()))
pokemon_two = random.choice(list(pokedex.keys()))

battle_scene = Image.open("battlescene.png")
pokemon_one_sprite = Image.open(
    BytesIO(requests.get(pokedex[pokemon_one]["Image URL"]).content))
pokemon_one_sprite.convert('RGBA')

pokemon_two_sprite = Image.open(
    BytesIO(requests.get(pokedex[pokemon_two]["Image URL"]).content))

pokemon_one_sprite.thumbnail((150, 150))
battle_scene.paste(pokemon_one_sprite, (343, 8), mask=pokemon_one_sprite)

pokemon_two_sprite.thumbnail((150, 150))
battle_scene.paste(pokemon_two_sprite, (74, 105), mask=pokemon_two_sprite)

# Their names.
draw = ImageDraw.Draw(battle_scene)
font = ImageFont.truetype('battlefont.ttf', 30)
draw.text((47, 45), pokemon_one, (0, 0, 0), font=font)
draw.text((330, 177), pokemon_two, (0, 0, 0), font=font)

battle_scene.show()
