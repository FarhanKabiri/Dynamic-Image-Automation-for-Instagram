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
    img_width, img_height = 1080, 1080
    img = Image.new('RGB', (img_width, img_height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Extract data
    surah_name = verse_data.get('data', {}).get('surah', {}).get('englishName', '')
    ayah_text = verse_data.get('data', {}).get('text', '')
    ayah_number = verse_data.get('data', {}).get('numberInSurah', '')

    # Load fonts
    title_font_path = "fonts/Neuton-Regular.ttf"
    body_font_path = "fonts/YanoneKaffeesatz-Regular.ttf"
    if not os.path.exists(title_font_path) or not os.path.exists(body_font_path):
        print("Font not found. Using default font.")
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
    else:
        font_title = ImageFont.truetype(title_font_path, size=70)
        font_body = ImageFont.truetype(body_font_path, size=40)

    # Title: Surah Name + Ayah Number
    title_text = f"Surah {surah_name} [Ayah {ayah_number}]"
    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]
    title_position = ((img_width - title_w) // 2, 100)
    draw.text(title_position, title_text, font=font_title, fill='white')

    # Ayah Text (wrapped + centered)
    max_line_length = 65
    ayah_lines = textwrap.wrap(ayah_text, width=max_line_length)
    line_spacing = 8
    starting_y = title_position[1] + title_h + 60

    for i, line in enumerate(ayah_lines):
        line_bbox = draw.textbbox((0, 0), line, font=font_body)
        line_w = line_bbox[2] - line_bbox[0]
        line_h = line_bbox[3] - line_bbox[1]
        line_x = (img_width - line_w) // 2
        line_y = starting_y + i * (line_h + line_spacing)
        draw.text((line_x, line_y), line, font=font_body, fill='white')

    # Save the image
    img.save("random_verse.png")
   # img.show()  # Local preview

# Automate posts on Instagram
def post_to_instagram():
    user_name = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')

    caption = 'Assalamualaikum, here is a random verse from the Quran. \n#quran #quranverses #quranquotes'
    png_image_path = 'random_verse.png'
    jpg_image_path = 'random_verse.jpg'

    # Convert PNG to JPEG
    if os.path.exists(png_image_path):
        img = Image.open(png_image_path)
        img.convert("RGB").save(jpg_image_path, "JPEG")
    else:
        print("Error: Image file not found! Exiting script.")
        return

    # Login and post
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
