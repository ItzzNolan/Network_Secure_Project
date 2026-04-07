import pygame
import os

def load_sprite(path, upscale_factor=1):
    if not os.path.exists(path):
        print(f"ERREUR : Impossible de trouver l'image : {path}")
        return None 

    image = pygame.image.load(path).convert_alpha()

   
    if upscale_factor > 1:
        width = image.get_width()
        height = image.get_height()
        image = pygame.transform.scale(image, (width * upscale_factor, height * upscale_factor))
    
    return image
