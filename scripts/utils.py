import os
import json
import random
import pygame

BASE_PATH = "assets/"

def load_image(path, set_transparent = True):
    img = pygame.image.load(BASE_PATH + path).convert()
    if set_transparent:
        img.set_colorkey((0, 0, 0))
    return img

def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_PATH + path)):
        images.append(load_image(path + "/" + img_name))
    return images

def save_to_json(path, data):
    file = open(BASE_PATH + path, "w")
    json.dump(data, file, indent=4)
    file.close()

def load_from_json(path):
    file = open(BASE_PATH + path, "r")
    data = json.load(file)
    file.close()
    return data

def get_color_from_range(color_range, is_grayscale = False):
    if not is_grayscale:
        return (random.randint(color_range[0][0], color_range[0][1]), random.randint(color_range[1][0], color_range[1][1]), random.randint(color_range[2][0], color_range[2][1]))
    else:
        grey_color = random.randint(color_range[0][0], color_range[0][1])
        return (grey_color, grey_color, grey_color)

def debug_rect(surface, rect, color = (255, 0, 0)):
    pygame.draw.rect(surface, color, rect, 2)

class Button():
    def __init__(self, return_on_press, image, rect):
        self.on_press = return_on_press
        self.image = image
        self.rect = self.image.get_rect(x = rect[0], y = rect[1], width = rect[2], height = rect[3])

    def draw(self, surface, debug = False):
        surface.blit(self.image, self.rect)
        if debug:
            pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)

    def press(self, mouse_pos):
        # print(f"mouse_pos: {mouse_pos}  X od {self.rect.left} do {self.rect.right}  Y od {self.rect.top} do {self.rect.bottom}")
        if mouse_pos[0] in range(self.rect.left, self.rect.right) and mouse_pos[1] in range(self.rect.top, self.rect.bottom):
            return self.on_press

    def select(self, mouse_pos, select_font, selected_color = (0, 0, 0)):
        # if mouse_pos[0] in range(self.rect.left, self.rect.right) and mouse_pos[1] in range(self.rect.top, self.rect.bottom):
        #     self.text_surf = select_font.render(self.text, False, selected_color)
        # else:
        #     self.text_surf = self.font.render(self.text, False, self.text_color)
        pass

class Button_wtext():
    def __init__(self, return_on_press, image, rect, text, text_pos, font, text_color = (0, 0, 0)):
        self.on_press = return_on_press
        self.image = image
        self.rect = self.image.get_rect(x = rect[0], y = rect[1], width = rect[2], height = rect[3])
        self.text = text
        self.text_pos = text_pos
        self.font = font
        self.text_color = text_color
        self.text_surf = self.font.render(self.text, False, self.text_color)

    def draw(self, surface, debug = False):
        surface.blit(self.image, self.rect)
        surface.blit(self.text_surf, self.text_pos)
        if debug:
            pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)


    def press(self, mouse_pos):
        # print(f"mouse_pos: {mouse_pos}  X od {self.rect.left} do {self.rect.right}  Y od {self.rect.top} do {self.rect.bottom}")
        if mouse_pos[0] in range(self.rect.left, self.rect.right) and mouse_pos[1] in range(self.rect.top, self.rect.bottom):
            return self.on_press

    def select(self, mouse_pos, select_font, selected_color = (0, 0, 0)):
        if mouse_pos[0] in range(self.rect.left, self.rect.right) and mouse_pos[1] in range(self.rect.top, self.rect.bottom):
            self.text_surf = select_font.render(self.text, False, selected_color)
        else:
            self.text_surf = self.font.render(self.text, False, self.text_color)