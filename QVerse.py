import time
import random
from PIL import Image, ImageFont, ImageDraw
import requests
import textwrap
from instagrapi import Client
import os
from instagrapi.types import Media as OriginalMedia
from typing import Union

class Media(OriginalMedia):
    pk: Union[str, int]


# Function to get a random verse from Quran API
def get_random_verse(edition):
    reference = random.randint(1, 6236)
    url = f'http://api.alquran.cloud/v1/ayah/{reference}/{edition}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to create an image with the verse
def create_image_with_verse(verse_data):
    color_picker = (1, 31, 102)
    img = Image.new('RGB', (800, 600), color=color_picker)
    draw = ImageDraw.Draw(img)

    surah_name = verse_data.get('data', {}).get('surah', {}).get('englishName', '')
    ayah_text = verse_data.get('data', {}).get('text', '')
    ayah_number = verse_data.get('data', {}).get('numberInSurah', '')

    font_path = "fonts/EduTASBeginner-VariableFont_wght.ttf"

    # Check if font file exists
    if not os.path.exists(font_path):
        print("Error: Font file not found. Using default font.")
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(font_path, size=30)

    # Positions in the image
    surah_position = (300, 50)
    ayah_position = (80, 100)

    # Multiple lines
    max_line_length = 50
    ayah_lines = textwrap.wrap(ayah_text, width=max_line_length)

    # Adding it to an image
    draw.text(surah_position, f'Surah {surah_name}', font=font, fill='white')
    for i, line in enumerate(ayah_lines):
        if i == 0:
            draw.text((ayah_position[0], ayah_position[1] + i*35), f'Ayah {ayah_number}: {line}', font=font, fill='white')
        else:
            draw.text((ayah_position[0], ayah_position[1] + i*35), line, font=font, fill='white')

    img.save("random_verse.png")

# Automate posts on Instagram
def post_to_instagram():
    user_name = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')

    caption = 'Assalamualaikum, here is a random verse from the Quran. \n#quran #quranverses #quranquotes'
    png_image_path = 'random_verse.png'
    jpg_image_path = 'random_verse.jpg'

    # PNG to JPEG
    if os.path.exists(png_image_path):
        img = Image.open(png_image_path)
        img.convert("RGB").save(jpg_image_path, "JPEG")
    else:
        print("Error: Image file not found! Exiting script.")
        return

    client = Client()
    client.login(user_name, password)
    client.photo_upload(jpg_image_path, caption)

# Run the script
verse_data = get_random_verse("en.sahih")

if verse_data:
    create_image_with_verse(verse_data)
    post_to_instagram()
else:
    print("Error: Failed to retrieve verse data.")
