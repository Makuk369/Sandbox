import sys
import pygame
import random
import math

from scripts import utils

# ----- Funkcie -----
def fall_down(block):
    if (block.y + 1 < HEIGHT_S) and surface.get_at((block.x, block.y + 1)) == bg_color:
        block.y += 1
        return True
    else:
        return False

def fall_down_side(block):
    if (block.y + 1 < HEIGHT_S):
        if (block.x + 1 < WIDTH_S) and (surface.get_at((block.x + 1, block.y + 1)) == bg_color) and random_seed: #right
            block.x += 1
            block.y += 1
            return True
        elif (block.x - 1 >= 0) and (surface.get_at((block.x - 1, block.y + 1)) == bg_color): #left
            block.x -= 1
            block.y += 1
            return True
        else:
            return False
    else:
        return False
        
def fall_side(block):
    if (block.x + 1 < WIDTH_S) and (wind_dir > 0) and (surface.get_at((block.x + 1, block.y)) == bg_color) and (surface.get_at((block.x + 1, block.y - 1)) == bg_color): #right
        block.x += 1
        return True
    elif (block.x - 1 >= 0) and (wind_dir < 0) and (surface.get_at((block.x - 1, block.y)) == bg_color) and surface.get_at((block.x - 1, block.y - 1)) == bg_color: #left
        block.x -= 1
        return True
    else:
        return False

WIDTH = 1280 #16
HEIGHT = 720 #9
SCALE = 10
WIDTH_S = WIDTH // SCALE
HEIGHT_S = HEIGHT // SCALE
GAME_SPEED = 30 #fps

show_fps = True

pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT)) 
surface = pygame.Surface((WIDTH_S, HEIGHT_S))

clock = pygame.time.Clock()

pygame.display.set_caption("Makuk's Sandbox")

# ----- UI -----
ui_font = pygame.font.Font("assets/fonts/Grand9K Pixel.ttf", 16)
ui_font_selected = pygame.font.Font("assets/fonts/Grand9K Pixel.ttf", 16)
ui_font_selected.set_underline(True)
surface_ui = pygame.Surface(((WIDTH_S // 10) * SCALE, HEIGHT))
block_select_bg = pygame.transform.scale(utils.load_image("block_select_bg.png"), surface_ui.get_size())

bg_color = (184, 237, 255, 255)

# ----- Blocks setup -----
block_types = {
    "sand": {
        "color": (237, 212, 45, 255),
        "blocks": [],  #block = Rect(x, y, width, height)
        "tags": ("fall_down", "fall_down_side")
        },
    "rock": {
        "color": (130, 130, 130, 255),
        "blocks": [],
        "tags": ()
        },
    "water": {
        "color": (0, 153, 255, 255),
        "blocks": [],
        "tags": ("fall_down", "fall_side")
        },
    }

selected_block = "sand"

wind_speed = 0

is_mouseL_pressed = False
is_mouseR_pressed = False
variant = 0

while True:
    random_seed = random.getrandbits(1)

    wind_speed += (3 / GAME_SPEED) + random.randint(-1, 1)
    if wind_speed > 30:
        wind_speed = 0
    wind_dir = math.sin(wind_speed)

    surface.fill(bg_color, (WIDTH_S // 10, 0, WIDTH_S - WIDTH_S // 10, HEIGHT_S))
    
    # ----- UI -----
    surface_ui.blit(block_select_bg, (0, 0))
    ypos = 20
    for btype in block_types:
        pygame.draw.rect(surface_ui, (0, 0, 0), (20, ypos + 5, 16, 16))
        pygame.draw.rect(surface_ui, block_types[btype]["color"], (22, ypos + 7, 12, 12))
        if btype == selected_block:
            utils.draw_text(surface_ui, btype, ui_font_selected, (40, ypos))
        else:
            utils.draw_text(surface_ui, btype, ui_font, (40, ypos))
        ypos += 25

    # ----- Update blocks -----
    # ----- Graphic -----
    for btype in block_types:
        for block in block_types[btype]["blocks"]:
            pygame.draw.rect(surface, block_types[btype]["color"], block)

    # ----- Logic -----
    for btype in block_types:
        for block in block_types[btype]["blocks"]:
            action = True
            for tag in block_types[btype]["tags"]:
                if action and tag == "fall_down":
                    action = not fall_down(block)
                if action and tag == "fall_down_side":
                    action = not fall_down_side(block)
                if action and tag == "fall_side":
                    fall_side(block)

    #----- Input -----
    mouse_pos = pygame.mouse.get_pos()

    if is_mouseL_pressed and surface.get_at((mouse_pos[0] / SCALE, mouse_pos[1] / SCALE)) == bg_color:
        block_types[selected_block]["blocks"].append(pygame.Rect(mouse_pos[0] / SCALE, mouse_pos[1] / SCALE, 1, 1))

    # if is_mouseR_pressed and surface.get_at((mouse_pos[0] / SCALE, mouse_pos[1] / SCALE)) == bg_color:
    #     rock_blocks.append(pygame.Rect(mouse_pos[0] / SCALE, mouse_pos[1] / SCALE, 1, 1))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            #print(event)
            if event.button == 1:
                is_mouseL_pressed = True
                #print(len(block_types["rock"]["blocks"]))
                #print(surface.get_at((mouse_pos[0] / SCALE, mouse_pos[1] / SCALE)))
                #print(block_types["sand"])
            if event.button == 3:
                is_mouseR_pressed = True
                print(len(block_types["sand"]["blocks"]))
            if event.button == 2:
                print(surface.get_at((mouse_pos[0] / SCALE, mouse_pos[1] / SCALE)))
            if event.button == 4:
                variant += 1
                selected_block = list(block_types.keys())[abs(variant) % len(block_types)]
            if event.button == 5:
                variant -= 1
                selected_block = list(block_types.keys())[abs(variant) % len(block_types)]
    
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_mouseL_pressed = False
            if event.button == 3:
                is_mouseR_pressed = False

    window.blit(pygame.transform.scale(surface, window.get_size()), (0, 0))
    window.blit(surface_ui, (0, 0))
    pygame.display.update()
    clock.tick(GAME_SPEED)

    if show_fps:
        pygame.display.set_caption(f"Makuk's Sandbox | FPS:{int(clock.get_fps())}")