import pygame
from scripts.block import Block

class LogicGrid:
    def __init__(self, width, height, fill_block: dict, block_temperature) -> None:
        self.width = width
        self.height = height
        self.direction = 1

        # ----- grid[y][x] -----
        self.grid = [[Block(fill_block, block_temperature) for x in range(self.width)] for y in range(self.height)]

    def update(self, environment):
        self.direction = not self.direction

        if self.direction:
            for y in range(self.height - 1, -1, -1): # koncove treba o -1 zmensit
                for x in range(self.width - 1, -1, -1): 
                    if self.grid[y][x].has_moved:
                        continue
                    self.grid[y][x].action(self.grid, x, y, environment)
                    self.grid[y][x].move(self.grid, x, y, environment)
        else:
            for y in range(self.height - 1, -1, -1): # koncove treba o -1 zmensit
                for x in range(self.width): 
                    if self.grid[y][x].has_moved:
                        continue
                    self.grid[y][x].action(self.grid, x, y, environment)
                    self.grid[y][x].move(self.grid, x, y, environment)

    def draw(self, surface):
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x].has_moved = False
                pygame.draw.rect(surface, self.grid[y][x].color, (x, y, 1, 1))

    def log(self):
        grid_str = ""
        for y in range(self.height):
            for x in range(self.width):
                grid_str += str(self.grid[y][x].id) + " "
            grid_str += "\n"
        print(grid_str)

