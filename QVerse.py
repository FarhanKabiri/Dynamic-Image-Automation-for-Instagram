import time
import random
import requests
import textwrap
import os
import urllib3.util.connection as utils # ADDED
from PIL import Image, ImageFont, ImageDraw
from instagrapi import Client
from dotenv import load_dotenv

import socket # Added this
import urllib3.util.connection as utils

# --- FIX: Force IPv4 for DigitalOcean ---
def allowed_gai_family():
    return socket.AF_INET # Use socket.AF_INET here

utils.allowed_gai_family = allowed_gai_family
# ----------------------------------------
load_dotenv()

def get_random_verse(edition):
    reference = random.randint(1, 6236)
    url = f'https://api.alquran.cloud/v1/ayah/{reference}/{edition}'

    for attempt in range(3):
        try:
            print(f"Attempt {attempt+1}: Fetching verse...")
            # Increased timeout slightly for server latency
            response = requests.get(url, timeout=15) 

            if response.status_code == 200:
                return response.json()
            else:
                print(f"API error: {response.status_code}")

        except Exception as e:
            print(f"Request failed: {e}")
            time.sleep(2)

    return None

def create_image_with_verse(verse_data):
    print("Creating image...")
    backgroundColor = (10, 20, 40)
    titleColor = (229, 200, 50)

    img_width, img_height = 1080, 1080
    img = Image.new('RGB', (img_width, img_height), color=backgroundColor)
    draw = ImageDraw.Draw(img)

    surah_name = verse_data.get('data', {}).get('surah', {}).get('englishName', '')
    ayah_text = verse_data.get('data', {}).get('text', '')
    ayah_number = verse_data.get('data', {}).get('numberInSurah', '')

    title_font_path = "fonts/Neuton-Regular.ttf"
    body_font_path = "fonts/YanoneKaffeesatz-Regular.ttf"

    if not os.path.exists(title_font_path) or not os.path.exists(body_font_path):
        print("Font not found. Using default font.")
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
    else:
        font_title = ImageFont.truetype(title_font_path, size=70)
        font_body = ImageFont.truetype(body_font_path, size=40)

    title_text = f"Surah {surah_name} [Ayah {ayah_number}]"
    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]
    title_position = ((img_width - title_w) // 2, 100)
    draw.text(title_position, title_text, font=font_title, fill=titleColor)

    max_line_length = 70
    ayah_lines = textwrap.wrap(ayah_text, width=max_line_length)
    starting_y = title_position[1] + title_h + 60

    ascent, descent = font_body.getmetrics()
    line_height = ascent + descent + 10

    for i, line in enumerate(ayah_lines):
        line_bbox = font_body.getbbox(line)
        line_w = line_bbox[2] - line_bbox[0]
        line_x = (img_width - line_w) // 2
        line_y = starting_y + i * line_height
        draw.text((line_x, line_y), line, font=font_body, fill='white')

    img.save("random_verse.png")
    print("Image saved.")

def post_to_instagram():
    print("Logging into Instagram...")
    user_name = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')

    if not user_name or not password:
        print("Missing Instagram credentials")
        return

    caption = 'Assalamualaikum, here is a random verse from the Quran.\n#quran #quranverses #quranquotes'
    png_image_path = 'random_verse.png'
    jpg_image_path = 'random_verse.jpg'

    if not os.path.exists(png_image_path):
        print("Image not found.")
        return

    img = Image.open(png_image_path)
    img.convert("RGB").save(jpg_image_path, "JPEG")

    try:
        client = Client()
        # On DigitalOcean, you might need to handle 2FA or suspicious login challenges
        client.login(user_name, password)
        print("Logged in successfully.")

        client.photo_upload(jpg_image_path, caption)
        print("Posted to Instagram.")

    except Exception as e:
        print(f"Instagram error: {e}")

def main():
    print("Starting script...")
    verse_data = get_random_verse("en.sahih")

    if not verse_data:
        print("Failed to fetch verse.")
        return

    create_image_with_verse(verse_data)
    post_to_instagram()
    print("Done.")

if __name__ == "__main__":
    main()