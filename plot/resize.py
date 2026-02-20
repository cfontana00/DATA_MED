from PIL import Image

import sys

image_path = sys.argv[1]
scale_factor = float(sys.argv[2])


with Image.open(image_path) as img:
        width, height = img.size
        
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Réécrit le même fichier
        resized_img.save(image_path)
