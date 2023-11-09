from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
import requests
import random
import textwrap
from instagrapi import Client
import os

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
    img = Image.new('RGB', (800, 600), 'white')
    draw = ImageDraw.Draw(img)

    surah_name = verse_data.get('data', {}).get('surah', {}).get('englishName', '')
    ayah_text = verse_data.get('data', {}).get('text', '')
    ayah_number = verse_data.get('data', {}).get('numberInSurah', '')

    font_path = "fonts/EduTASBeginner-VariableFont_wght.ttf"
    font = ImageFont.truetype(font_path, size=30)  # Adjust the size if needed

    # Define text positions in the image
    surah_position = (50, 50)
    ayah_position = (50, 100)

    # Multiple lines
    max_line_length = 40
    ayah_lines = textwrap.wrap(ayah_text, width=max_line_length)

    # Adding it to an image
    draw.text(surah_position, f'Surah {surah_name}', font=font, fill='black')
    for i, line in enumerate(ayah_lines):
        if i == 0:
            draw.text((ayah_position[0], ayah_position[1] + i*35), f'Ayah {ayah_number}: {line}', font=font, fill='black')
        else:
            draw.text((ayah_position[0], ayah_position[1] + i*35), line, font=font, fill='black')

    img.save("random_verse.png")

# Automate posts on Instagram
def post_to_instagram():
    user_name = os.getenv('INSTAGRAM_USERNAME','reminder_of_akh1ra')
    password = os.getenv('INSTAGRAM_PASSWORD','Iownthis313')

    caption = 'Assalamualaykum, Here is a random verse from the Quran.'
    png_image_path = 'random_verse.png'
    jpg_image_path = 'random_verse.jpg'

    # PNG to JPEG
    img = Image.open(png_image_path)
    img.convert("RGB").save(jpg_image_path, "JPEG")

    client = Client()
    client.login(user_name, password)
    client.photo_upload(jpg_image_path, caption)

# Uncomment the following line to run the functions
verse_data = get_random_verse("en.sahih")
create_image_with_verse(verse_data)
post_to_instagram()
