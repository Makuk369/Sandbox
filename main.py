import sys
import pygame
import random
import time

from scripts import utils
from scripts.logic import LogicGrid
from scripts.block import Block

WIDTH = 1280 #16
HEIGHT = 720 #9
SCALE = 10
WIDTH_S = WIDTH // SCALE
HEIGHT_S = HEIGHT // SCALE
GAME_SPEED = 30 #fps

show_fps = True

pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT)) 
surface_s = pygame.Surface((WIDTH_S, HEIGHT_S)) #128, 72

clock = pygame.time.Clock()

pygame.display.set_caption("Makuk's Sandbox")

# ----- UI -----
ui_font = pygame.font.Font("assets/fonts/Grand9K Pixel.ttf", 32) #realne 52
ui_font_small = pygame.font.Font("assets/fonts/Grand9K Pixel.ttf", 16) #realne 26
ui_font_selected = pygame.font.Font("assets/fonts/Grand9K Pixel.ttf", 32)
ui_font_selected.set_underline(True)
surface_ui = pygame.Surface((WIDTH, HEIGHT))
surface_ui.set_colorkey((0, 0, 0))
block_select_bg = pygame.transform.scale(utils.load_image("imgs/block_select_bg.png"), (WIDTH, (HEIGHT_S // 10) * SCALE))
block_select_bg_WH = (block_select_bg.get_width(), block_select_bg.get_height()) #1280, 70
# print(block_select_bg_WH[0], block_select_bg_WH[1])
block_icons = utils.load_images("imgs/block_icons")
more_icon = pygame.transform.scale_by(utils.load_image("imgs/more_icon.png"), 10)
more_button = utils.Button(True, more_icon, (0, HEIGHT - (HEIGHT_S // 10) * SCALE, more_icon.get_width(), more_icon.get_height()))
up_arrow = pygame.transform.scale_by(utils.load_image("imgs/up_arrow.png"), 10)
down_arrow = pygame.transform.scale_by(utils.load_image("imgs/down_arrow.png"), 10)
up_button = utils.Button(True, up_arrow, (WIDTH - down_arrow.get_width() - up_arrow.get_height(), HEIGHT - (HEIGHT_S // 10) * SCALE, up_arrow.get_width(), up_arrow.get_height()))
down_button = utils.Button(True, down_arrow, (WIDTH - down_arrow.get_width(), HEIGHT - (HEIGHT_S // 10) * SCALE, down_arrow.get_width(), down_arrow.get_height()))

# print(HEIGHT - ((HEIGHT_S // 10) * SCALE))

environment = {
    "temperature": 50,
    "gravity": 1
}
env_i = 0

selected_block = "sand"

block_types = utils.load_from_json("blockdata.json")

logic_grid = LogicGrid(WIDTH_S, HEIGHT_S - (HEIGHT_S // 10), Block(block_types["air"])) #127, 63

block_buttons = []
xpos = 20
ypos = 20
for block_icon, block_type in zip(block_icons, block_types):
    block_buttons.append(utils.Button_wtext(block_type, pygame.transform.scale_by(block_icon, 2), (xpos, ypos, (WIDTH - 40) / 3, block_icon.get_height() * 2.25), block_type, (xpos + 36, ypos - 10), ui_font, (78, 52, 46)))
    ypos += 40
    if ypos > HEIGHT - ((HEIGHT_S // 10) * SCALE) - 20:
        xpos += (WIDTH - 40) / 3
        ypos = 20

is_LShift_held = False
is_mouseL_held = False
is_mouseR_held = False
is_block_menu_open = False
variant = block_types[selected_block]["id"]
brush_size = 1

while True:
    
    # ----- UI -----
    if is_block_menu_open:
        surface_ui.fill((188, 170, 164))
        for block_button in block_buttons:
            block_button.draw(surface_ui)
    else:
        surface_ui.fill("black")

    surface_ui.blit(block_select_bg, (0, HEIGHT - (HEIGHT_S // 10) * SCALE))
    more_button.draw(surface_ui)
    surface_ui.blit(pygame.transform.scale_by(block_icons[variant % len(block_types)], 2), (100, HEIGHT - (HEIGHT_S // 10) * SCALE + 20))
    surface_ui.blit(ui_font.render(selected_block, False, (78, 52, 46)), (140, HEIGHT - (HEIGHT_S // 10) * SCALE + 10))
    surface_ui.blit(ui_font.render(f"{environment["temperature"]}°C", False, (78, 52, 46)), (WIDTH - down_arrow.get_width() - up_arrow.get_height() - len(str(environment["temperature"])) * 25 - 40, HEIGHT - (HEIGHT_S // 10) * SCALE + 10))
    up_button.draw(surface_ui)
    down_button.draw(surface_ui)


    # ----- Update blocks -----
    # start = time.perf_counter()
    logic_grid.update(environment)
    # start2 = time.perf_counter()
    logic_grid.draw(surface_s)
    # end = time.perf_counter()
    # print(f"update: {start2 - start}, draw: {end - start2}")

    #----- Input -----
    mouse_pos = pygame.mouse.get_pos()
    mouse_pos_s = (mouse_pos[0] // SCALE, mouse_pos[1] // SCALE)
    # print(mouse_pos_s)

    #----- Pokladanie Blokov -----
    if not is_block_menu_open and (0 <= mouse_pos_s[0]) and (mouse_pos_s[0] + brush_size - 1 <= logic_grid.width - 1) and (0 <= mouse_pos_s[1]) and (mouse_pos_s[1] + brush_size - 1 <= logic_grid.height - 1):
        pygame.draw.rect(surface_ui, (204, 190, 184), (mouse_pos_s[0] * SCALE, mouse_pos_s[1] * SCALE, SCALE * brush_size, SCALE * brush_size), 1)

    if is_mouseL_held and not is_block_menu_open and (0 <= mouse_pos_s[0]) and (mouse_pos_s[0] + brush_size - 1 <= logic_grid.width - 1) and (0 <= mouse_pos_s[1]) and (mouse_pos_s[1] + brush_size - 1 <= logic_grid.height - 1):
        y = -1
        for x in range(brush_size * brush_size):
            if x % brush_size == 0:
                y += 1
            logic_grid.grid[mouse_pos_s[1] + y][mouse_pos_s[0] + (x - brush_size * y)] = Block(block_types[selected_block])
        # print("NEW BLOCK")
    
    if is_mouseR_held and not is_block_menu_open and (0 <= mouse_pos_s[0] <= logic_grid.width - 1) and (0 <= mouse_pos_s[1] <= logic_grid.height - 1):
        
        #----- Zobrazenie info o bloku -----
        hovered_block = list(block_types.keys())[logic_grid.grid[mouse_pos_s[1]][mouse_pos_s[0]].id % len(block_types)]
        info_header = ui_font_small.render(hovered_block.upper(), False, (78, 52, 46))
        info_texts = [str(f"ID: {block_types[hovered_block]["id"]}\n"),
                      str(f"Density: {block_types[hovered_block]["density"]}"),
                      str(f"Temperature: {"%.2f" % logic_grid.grid[mouse_pos_s[1]][mouse_pos_s[0]].temperature} °C"),
                      str(f"State: {logic_grid.grid[mouse_pos_s[1]][mouse_pos_s[0]].state}"),
                      str(f"Is moving: {logic_grid.grid[mouse_pos_s[1]][mouse_pos_s[0]].is_moving}"),
                      str(f"Velocity: {logic_grid.grid[mouse_pos_s[1]][mouse_pos_s[0]].velocity}")
                      ]
        
        longest_text = len(hovered_block)
        for text in info_texts:
            if len(text) > longest_text:
                longest_text = len(text)
        info_size = (longest_text * 10, 10 + (len(info_texts) + 1) * 20)

        ypos_lock = 0 #ak ui presahuje spodok obrazovky
        if (mouse_pos[1] + info_size[1] + 10) > HEIGHT:
            ypos_lock = mouse_pos[1] - (HEIGHT - info_size[1] - 10)

        if (mouse_pos[0] + 10 + info_size[0] + 20) > WIDTH: #ak ui presahuje pravu stranu
            pygame.draw.rect(surface_ui, (78, 52, 46), (mouse_pos[0] - 30 - info_size[0], mouse_pos[1] - ypos_lock, info_size[0] + 20, info_size[1] + 10)) #okraj
            pygame.draw.rect(surface_ui, (188, 170, 164), (mouse_pos[0] - 25 - info_size[0], mouse_pos[1] + 5 - ypos_lock, info_size[0] + 10, info_size[1])) #vnutorny
            surface_ui.blit(info_header, (mouse_pos[0] - 20 - info_size[0] // 2 - info_header.get_width() // 2, mouse_pos[1] + 5 - ypos_lock))
            ypos = 25
            for text in info_texts:
                surface_ui.blit(ui_font_small.render(text, False, (78, 52, 46)), (mouse_pos[0] - 20 - info_size[0], mouse_pos[1] + ypos - ypos_lock))
                ypos += 20  
        else:
            pygame.draw.rect(surface_ui, (78, 52, 46), (mouse_pos[0] + 10, mouse_pos[1] - ypos_lock, info_size[0] + 20, info_size[1] + 10)) #okraj
            pygame.draw.rect(surface_ui, (188, 170, 164), (mouse_pos[0] + 15, mouse_pos[1] + 5 - ypos_lock, info_size[0] + 10, info_size[1])) #vnutorny
            surface_ui.blit(info_header, (mouse_pos[0] + 20 + info_size[0] // 2 - info_header.get_width() // 2, mouse_pos[1] + 5 - ypos_lock))
            ypos = 25
            for text in info_texts:
                surface_ui.blit(ui_font_small.render(text, False, (78, 52, 46)), (mouse_pos[0] + 20, mouse_pos[1] + ypos - ypos_lock))
                ypos += 20  

    for event in pygame.event.get():
        # print(event)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:
                is_LShift_held = True
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                is_LShift_held = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # mouse L
                is_mouseL_held = True

                if more_button.press(mouse_pos):
                    is_block_menu_open = not is_block_menu_open

                if is_block_menu_open: #vyberanie bloku v block menu
                    for block_button in block_buttons:
                        sb = block_button.press(mouse_pos)
                        if sb != None:
                            selected_block = sb
                            variant = block_types[selected_block]["id"]
                
                if up_button.press(mouse_pos):
                    environment["temperature"] += 5
                if down_button.press(mouse_pos):
                    environment["temperature"] -= 5

            if event.button == 3: # mouse R
                is_mouseR_held = True
            if event.button == 2: # mouse mid
                GAME_SPEED = 1
            if event.button == 4:
                if is_LShift_held: #brush size down
                    brush_size = max(brush_size - 1, 1)
                else:
                    variant -= 1
                    selected_block = list(block_types.keys())[variant % len(block_types)]
            if event.button == 5:
                if is_LShift_held: #brush size up
                    brush_size += 1
                else:
                    variant += 1
                    selected_block = list(block_types.keys())[variant % len(block_types)]
    
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                is_mouseL_held = False
            if event.button == 3:
                is_mouseR_held = False

    window.blit(pygame.transform.scale(surface_s, window.get_size()), (0, 0))
    window.blit(surface_ui, (0, 0))
    pygame.display.update()
    clock.tick(GAME_SPEED)

    if show_fps:
        pygame.display.set_caption(f"Makuk's Sandbox | FPS:{int(clock.get_fps())}")