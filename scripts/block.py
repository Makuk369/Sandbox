import math
import random

from scripts.utils import get_color_from_range, load_from_json, move_to_zero

block_types = load_from_json("blockdata.json")

close_adjacent = ((-1, 0), (0, 1), (1, 0), (0, -1)) #y, x

class Block:
    def __init__(self, block_type: dict) -> None:
        self.id = block_type["id"]
        if type(block_type["color"][1]) == int: #zisti ci je blok grayscale
            self.color = get_color_from_range(block_type["color"], True)
        else:
            self.color = get_color_from_range(block_type["color"])
        self.density = block_type["density"]
        if self.density < 500:
            self.state = 1 #plyn
        elif self.density < 1500:
            self.state = 2 #tekutina
        else:
            self.state = 3 #pevne
        self.temperature = block_type["temperature"]
        self.thermal_conductivity = block_type["thermal_conductivity"]
        self.state_changes = (block_type["melting_temp"], block_type["freezing_temp"])
        self.velocity = (0, 0)
        self.friction = block_type["friction"]
        self.can_move = block_type["can_move"]
        self.has_moved = False
        self.is_moving = True #pre inertia, zastavy kazdy iny pohyb okrem zakladneho = dole, hore
        self.actiontags = block_type["actiontags"]
        self.has_made_action = False
        self.changesto = block_type["changesto"]

    def move(self, grid, xpos, ypos, environment):
        if not self.can_move: #ak sa nevie hybat
            return
        
        grid_size = (len(grid) - 1, len(grid[0]) - 1) #[0] = y height, [1] = x width

        # ----- vypocet velocity -----
        if self.is_moving or ((ypos + 1 <= grid_size[0]) and (grid[ypos + 1][xpos].state != 3) and (grid[ypos + 1][xpos].density < self.density)): #moze sa hybat alebo nieje dole blok
            if (random.randint(0, 100) - random.randint(0, 100)) > (self.friction * 100): #odfukne vietor
                self.velocity = (self.velocity[0] + random.randint(-1, 1), self.velocity[1] + environment["gravity"]) #x, y (kolko blokov sa pohne za frame)
            elif (random.randint(0, 100)) < (self.friction * 100): #prestava sa smikat
                self.velocity = (round(move_to_zero(self.velocity[0], 2, True)), self.velocity[1] + environment["gravity"])
            else: #smika sa = zachova svoj pohyb do boku
                self.velocity = (self.velocity[0], self.velocity[1] + environment["gravity"])
        # elif self.is_moving and ((grid[ypos + 1][xpos].state == 3) and (grid[ypos + 1][xpos].density > self.density)): #moze sa hybat a dole je blok
        #     if (self.state < 3) and (xpos + 1 <= grid_size[1]) and (grid[ypos + 1][xpos + 1].density < self.density): #je napravo grid a napravo dole blok s mensiou hustotou
        #         self.velocity = (1, 1)
        #     elif (self.state < 3) and (xpos - 1 >= 0) and (grid[ypos + 1][xpos - 1].density < self.density): #je vlavo grid a vlavo dole blok s mensiou hustotou
        #         self.velocity = (-1, 1)
        else: #nemoze sa hybat
            self.velocity = (0, 0)
            return
        
        # print("vel", self.velocity)

        # ----- pohyb -----
        next_positions = self.calc_pos_check((xpos, ypos), (xpos + self.velocity[0], ypos + self.velocity[1]))
        # print("next pos", next_positions)
        if not self.has_moved and self.velocity[0] == 0: # iba dole
            for next_pos in next_positions:
                if ypos + next_pos[1] <= grid_size[0]: #je dole grid
                    if (self.state < 3) and (grid[ypos + next_pos[1]][xpos].density < self.density): #je tekutina alebo plyn a pod nim je blok s mensiou hustotou
                        final_pos = next_pos
                    elif (self.state == 3) and (grid[ypos + next_pos[1]][xpos].state != 3): #je pevny a nie je pod nim pevny blok
                        final_pos = next_pos
                    else: #dopadol
                        self.velocity = ((math.floor(self.velocity[1] / (1 / max(1 - self.friction, 0.01))) * random.choice((-1, 1)), 0))
                        # print("dopadol", self.velocity)
                        break
                else: #dopadol na spodok gridu
                    self.velocity = ((math.floor(self.velocity[1] / (1 / max(1 - self.friction, 0.01))) * random.choice((-1, 1)), 0))
                    # print("dopadol g", self.velocity)
                    break
            try:
                grid[ypos][xpos] = grid[ypos + final_pos[1]][xpos] #vymeni seba za block do ktoreho pozicie ide
                grid[ypos + final_pos[1]][xpos] = self #da seba do cielovej pozicie
                for adjpos in close_adjacent:
                    if not (xpos + adjpos[1] <= grid_size[1]) or not (xpos + adjpos[1] >= 0) or not (ypos + adjpos[0] <= grid_size[0]) or not (ypos + adjpos[0] >= 0): #ak neni v gridu = skip
                        continue
                    grid[ypos + adjpos[0]][xpos + adjpos[1]].is_moving = True #nastavenie okolnych blokov aby sa mohli hybat
                self.has_moved = True
            except UnboundLocalError:
                if self.velocity == (0, 0):
                    self.is_moving = False
                    # print("stop")
                else:
                    pass
                    # print("no stop")

        elif not self.has_moved: # krivo dole
            for next_pos in next_positions:
                if (ypos + next_pos[1] <= grid_size[0]) and (xpos + next_pos[0] <= grid_size[1]) and (xpos + next_pos[0] >= 0): #je v gride
                    if (self.state < 3) and (grid[ypos + next_pos[1]][xpos + next_pos[0]].density < self.density): #je tekutina alebo plyn a dalsi blok ma mensiu hustotu
                        final_pos = next_pos
                    elif (self.state == 3) and (grid[ypos + next_pos[1]][xpos + next_pos[0]].state != 3): #je pevny a dalsi blok nie je pevny blok
                        final_pos = next_pos
                    else: #dopadol
                        self.velocity = ((self.velocity[0] + math.floor(self.velocity[1] / (1 / max(1 - self.friction, 0.01))) * random.choice((-1, 1)), 0))
                        # print("dopadol2", self.velocity)
                        break
                elif ((xpos + next_pos[0] > grid_size[1]) or (xpos + next_pos[0] < 0)): #napravo alebo nalavo neni grid
                    self.velocity = (0, self.velocity[1])
                    # print("odraz", self.velocity)
                    break
                else: #dopadol na spodok gridu
                    self.velocity = ((self.velocity[0] + math.floor(self.velocity[1] / (1 / max(1 - self.friction, 0.01))) * random.choice((-1, 1)), 0))
                    # print("dopadol2 g", self.velocity)
                    break
            try:
                grid[ypos][xpos] = grid[ypos + final_pos[1]][xpos + final_pos[0]] #vymeni seba za block do ktoreho pozicie ide
                grid[ypos + final_pos[1]][xpos + final_pos[0]] = self #da seba do cielovej pozicie
                for adjpos in close_adjacent:
                    if not (xpos + adjpos[1] <= grid_size[1]) or not (xpos + adjpos[1] >= 0) or not (ypos + adjpos[0] <= grid_size[0]) or not (ypos + adjpos[0] >= 0): #ak neni v gridu = skip
                        continue
                    grid[ypos + adjpos[0]][xpos + adjpos[1]].is_moving = True #nastavenie okolnych blokov aby sa mohli hybat
                self.has_moved = True
            except UnboundLocalError:
                if self.velocity == (0, 0):
                    self.is_moving = False
                    # print("stop2")
                else:
                    pass
                    # print("no stop")
        
    """
            elif not self.has_moved and tag == 1: # down side
                if (ypos + 1 <= grid_size[0]): #je dole grid
                    if (environment["wind"] > 0): #fuka vietor doprava
                        if (self.state < 3) and (xpos + 1 <= grid_size[1]) and (grid[ypos + 1][xpos + 1].density < self.density): #je napravo grid a napravo dole blok s mensiou hustotou
                            grid[ypos][xpos] = grid[ypos + 1][xpos + 1]
                            grid[ypos + 1][xpos + 1] = self
                            self.has_moved = True
                        elif (self.state < 3) and (xpos - 1 >= 0) and (grid[ypos + 1][xpos - 1].density < self.density): #je vlavo grid a vlavo dole blok s mensiou hustotou
                            grid[ypos][xpos] = grid[ypos + 1][xpos - 1]
                            grid[ypos + 1][xpos - 1] = self
                            self.has_moved = True
                        #pevne
                        if (self.state == 3) and (xpos + 1 <= grid_size[1]) and (grid[ypos + 1][xpos + 1].state != 3): #je napravo grid a napravo dole blok s mensiou hustotou
                            grid[ypos][xpos] = grid[ypos + 1][xpos + 1]
                            grid[ypos + 1][xpos + 1] = self
                            self.has_moved = True
                        elif (self.state == 3) and (xpos - 1 >= 0) and (grid[ypos + 1][xpos - 1].state != 3): #je vlavo grid a vlavo dole blok s mensiou hustotou
                            grid[ypos][xpos] = grid[ypos + 1][xpos - 1]
                            grid[ypos + 1][xpos - 1] = self
                            self.has_moved = True
                    if (environment["wind"] < 0): #fuka vietor dolava
                        if (self.state < 3) and (xpos - 1 >= 0) and (grid[ypos + 1][xpos - 1].density < self.density): #je vlavo grid a vlavo dole blok s mensiou hustotou
                            grid[ypos][xpos] = grid[ypos + 1][xpos - 1]
                            grid[ypos + 1][xpos - 1] = self
                            self.has_moved = True
                        elif (self.state < 3) and (xpos + 1 <= grid_size[1]) and (grid[ypos + 1][xpos + 1].density < self.density): #je napravo grid a napravo dole blok s mensiou hustotou
                            grid[ypos][xpos] = grid[ypos + 1][xpos + 1]
                            grid[ypos + 1][xpos + 1] = self
                            self.has_moved = True
                        #pevne
                        if (self.state == 3) and (xpos - 1 >= 0) and (grid[ypos + 1][xpos - 1].state != 3): #je vlavo grid a vlavo dole blok s mensiou hustotou
                            grid[ypos][xpos] = grid[ypos + 1][xpos - 1]
                            grid[ypos + 1][xpos - 1] = self
                            self.has_moved = True
                        elif (self.state == 3) and (xpos + 1 <= grid_size[1]) and (grid[ypos + 1][xpos + 1].state != 3): #je napravo grid a napravo dole blok s mensiou hustotou
                            grid[ypos][xpos] = grid[ypos + 1][xpos + 1]
                            grid[ypos + 1][xpos + 1] = self
                            self.has_moved = True

            elif not self.has_moved and tag == 2: # side (down)
                randnum = random.randint(0, 1)
                if (randnum != 0) and (xpos + 1 <= grid_size[1]) and (grid[ypos][xpos + 1].density < self.density): #je napravo grid a blok s mensiou hustotou
                    grid[ypos][xpos] = grid[ypos][xpos + 1]
                    grid[ypos][xpos + 1] = self
                    self.has_moved = True
                elif (randnum == 0) and (xpos - 1 >= 0) and (grid[ypos][xpos - 1].density < self.density): #je vlavo grid a blok s mensiou hustotou
                    grid[ypos][xpos] = grid[ypos][xpos - 1]
                    grid[ypos][xpos - 1] = self
                    self.has_moved = True

            elif not self.has_moved and tag == 10: #up
                if (ypos - 1 >= 0) and (grid[ypos - 1][xpos].density > self.density) and (grid[ypos - 1][xpos].state == 1): #je hore grid a plinovy blok s vacsiou hustotou
                    grid[ypos][xpos] = grid[ypos - 1][xpos] #vymeni seba za block do ktoreho pozicie ide
                    grid[ypos - 1][xpos] = self #da seba do cielovej pozicie
                    self.has_moved = True

            elif not self.has_moved and tag == 11: # up side
                if (ypos - 1 >= 0): #je hore grid
                    if (environment["wind"] > 0): #fuka vietor doprava
                        if (xpos + 1 <= grid_size[1]) and (grid[ypos - 1][xpos + 1].density > self.density) and (grid[ypos - 1][xpos + 1].state == 1): #je napravo grid a napravo hore blok s vacsiou hustotou
                            grid[ypos][xpos] = grid[ypos - 1][xpos + 1]
                            grid[ypos - 1][xpos + 1] = self
                            self.has_moved = True
                        elif (xpos - 1 >= 0) and (grid[ypos - 1][xpos - 1].density > self.density) and (grid[ypos - 1][xpos - 1].state == 1): #je vlavo grid a vlavo hore blok s vacsiou hustotou
                            grid[ypos][xpos] = grid[ypos - 1][xpos - 1]
                            grid[ypos - 1][xpos - 1] = self
                            self.has_moved = True
                    if (environment["wind"] < 0): #fuka vietor dolava
                        if (xpos - 1 >= 0) and (grid[ypos - 1][xpos - 1].density > self.density) and (grid[ypos - 1][xpos - 1].state == 1): #je vlavo grid a vlavo hore blok s vacsiou hustotou
                            grid[ypos][xpos] = grid[ypos - 1][xpos - 1]
                            grid[ypos - 1][xpos - 1] = self
                            self.has_moved = True
                        elif (xpos + 1 <= grid_size[1]) and (grid[ypos - 1][xpos + 1].density > self.density) and (grid[ypos - 1][xpos + 1].state == 1): #je napravo grid a napravo hore blok s vacsiou hustotou
                            grid[ypos][xpos] = grid[ypos - 1][xpos + 1]
                            grid[ypos - 1][xpos + 1] = self
                            self.has_moved = True

            elif not self.has_moved and tag == 12: # side (up)
                randnum = random.randint(0, 1)
                if (randnum != 0) and (xpos + 1 <= grid_size[1]) and (grid[ypos][xpos + 1].density > self.density) and (grid[ypos][xpos + 1].state == 1): #je napravo grid a plinovy blok s vacsiou hustotou
                    grid[ypos][xpos] = grid[ypos][xpos + 1]
                    grid[ypos][xpos + 1] = self
                    self.has_moved = True
                elif (randnum == 0) and (xpos - 1 >= 0) and (grid[ypos][xpos - 1].density > self.density) and (grid[ypos][xpos - 1].state == 1): #je vlavo grid a plinovy blok s vacsiou hustotou
                    grid[ypos][xpos] = grid[ypos][xpos - 1]
                    grid[ypos][xpos - 1] = self
                    self.has_moved = True
    """
    def action(self, grid, xpos, ypos, environment):
        grid_size = (len(grid) - 1, len(grid[0]) - 1) #[0] = y height, [1] = x width

        total_adj_temp = 0
        for adjpos in close_adjacent:
            if not (ypos + adjpos[0] >= 0): #zhora ide teplota atmosfery
                total_adj_temp += environment["temperature"]
                continue
            if not (xpos + adjpos[1] <= grid_size[1]) or not (xpos + adjpos[1] >= 0) or not (ypos + adjpos[0] <= grid_size[0]): #ak neni v gridu
                total_adj_temp += self.temperature
                continue
            total_adj_temp += grid[ypos + adjpos[0]][xpos + adjpos[1]].temperature
        self.temperature += (total_adj_temp / 4 - self.temperature) / (100 / self.thermal_conductivity)

        for tag in self.actiontags:
            for adjpos in close_adjacent:
                if not (xpos + adjpos[1] <= grid_size[1]) or not (xpos + adjpos[1] >= 0) or not (ypos + adjpos[0] <= grid_size[0]) or not (ypos + adjpos[0] >= 0): #ak neni v gridu = skip
                    continue

                for chtag in grid[ypos + adjpos[0]][xpos + adjpos[1]].changesto.keys(): #ked ovplivnuje okolne bloky
                    chtag = int(chtag)
                    if not self.has_made_action and (tag == 0) and (tag == chtag): #akcia je 0 a ma odpoved, vsiaknutie
                        new_block = Block(block_types[grid[ypos + adjpos[0]][xpos + adjpos[1]].changesto[str(chtag)]]) #zmeni blok
                        new_block.temperature = (self.temperature + new_block.temperature) / 2
                        grid[ypos + adjpos[0]][xpos + adjpos[1]] = new_block
                        grid[ypos][xpos] = Block(block_types["air"]) #znici sa
                        self.has_made_action = True

            for chtag in self.changesto.keys(): #ked ovplivnuje seba
                chtag = int(chtag)
                if not self.has_made_action and (tag == 1) and (tag == chtag): #stuhnutie
                    if (self.state_changes[1] != None) and (self.temperature < self.state_changes[1]):
                        new_block = Block(block_types[self.changesto[str(chtag)]])
                        new_block.temperature = environment["temperature"]
                        grid[ypos][xpos] = new_block
                        self.has_made_action = True
                
                elif not self.has_made_action and (tag == 2) and (tag == chtag): #rozpustanie
                    if (self.state_changes[0] != None) and (self.temperature > self.state_changes[0]):
                        new_block = Block(block_types[self.changesto[str(chtag)]])
                        new_block.temperature = environment["temperature"]
                        grid[ypos][xpos] = new_block
                        self.has_made_action = True

    def calc_pos_check(self, start: tuple, end: tuple) -> list:
        x_len = end[0] - start[0]
        y_len = end[1] - start[1]

        positions_to_check = []

        if abs(x_len) > abs(y_len): #ide cez x
            if x_len != 0:
                slope = y_len / x_len
            else:
                slope = y_len / 1
            # print("slope:",slope)

            if x_len > 0:
                for x in range(1, x_len + 1):
                    positions_to_check.append((x, round(slope * x)))

                    # print(f"X: {x} Y: {round(slope * x)}   {slope * x}")
            else:
                for x in range(-1, x_len - 1, -1):
                    positions_to_check.append((x, round(slope * x)))

                    # print(f"X: {x} Y: {round(slope * x)}   {slope * x}")
        else: #ide cez y
            if y_len != 0:
                slope = x_len / y_len
            else:
                slope = x_len / 1
            # print("slope:",slope)

            if y_len > 0:
                for y in range(1, y_len + 1):
                    positions_to_check.append((round(slope * y), y))

                    # print(f"X: {round(slope * y)} Y: {y}  {slope * y}")
            else:
                for y in range(-1, y_len - 1, -1):
                    positions_to_check.append((round(slope * y), y))

                    # print(f"X: {round(slope * y)} Y: {y}  {slope * y}")
        return positions_to_check