from PIL import Image, ImageDraw, ImageFont
import base64

img = Image.new('RGB', (180, 180), color='black')
d = ImageDraw.Draw(img)
# ⚡️
# Use a default font, but since emoji might be hard to render with PIL, we can just fetch an emoji from twitter.
