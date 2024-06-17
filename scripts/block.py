from scripts.utils import get_color_from_range, load_from_json

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
        self.stability = block_type["stability"]
        self.temperature = block_type["temperature"]
        self.thermal_conductivity = block_type["thermal_conductivity"]
        self.state_changes = (block_type["melting_temp"], block_type["freezing_temp"])
        self.movetags = block_type["movetags"]
        self.has_moved = False
        self.actiontags = block_type["actiontags"]
        self.has_made_action = False
        self.changesto = block_type["changesto"]

    def move(self, grid, xpos, ypos, environment):
        grid_size = (len(grid) - 1, len(grid[0]) - 1) #[0] = y height, [1] = x width
        
        for tag in self.movetags:
            if not self.has_moved and tag == 0: # down
                if ypos + 1 <= grid_size[0]: #je dole grid
                    if grid[ypos + 1][xpos].density < self.density: #je pod nim blok s mensiou hustotou
                        grid[ypos][xpos] = grid[ypos + 1][xpos] #vymeni seba za block do ktoreho pozicie ide
                        grid[ypos + 1][xpos] = self #da seba do cielovej pozicie
                        self.has_moved = True

            elif not self.has_moved and tag == 1: # down side
                if (ypos + 1 <= grid_size[0]): #je dole grid
                    if (environment["wind"] > 0): #fuka vietor doprava
                        if (xpos + 1 <= grid_size[1]) and (grid[ypos + 1][xpos + 1].density < self.density): #je napravo grid a napravo dole blok s mensiou hustotou
                            grid[ypos][xpos] = grid[ypos + 1][xpos + 1]
                            grid[ypos + 1][xpos + 1] = self
                            self.has_moved = True
                        elif (xpos - 1 >= 0) and (grid[ypos + 1][xpos - 1].density < self.density): #je vlavo grid a vlavo dole blok s mensiou hustotou
                            grid[ypos][xpos] = grid[ypos + 1][xpos - 1]
                            grid[ypos + 1][xpos - 1] = self
                            self.has_moved = True
                    if (environment["wind"] < 0): #fuka vietor dolava
                        if (xpos - 1 >= 0) and (grid[ypos + 1][xpos - 1].density < self.density): #je vlavo grid a vlavo dole blok s mensiou hustotou
                            grid[ypos][xpos] = grid[ypos + 1][xpos - 1]
                            grid[ypos + 1][xpos - 1] = self
                            self.has_moved = True
                        elif (xpos + 1 <= grid_size[1]) and (grid[ypos + 1][xpos + 1].density < self.density): #je napravo grid a napravo dole blok s mensiou hustotou
                            grid[ypos][xpos] = grid[ypos + 1][xpos + 1]
                            grid[ypos + 1][xpos + 1] = self
                            self.has_moved = True

            elif not self.has_moved and tag == 2: # side-down
                if (environment["wind"] > 0) and (xpos + 1 <= grid_size[1]) and (grid[ypos][xpos + 1].density < self.density): #je napravo grid a blok s mensiou hustotou
                    grid[ypos][xpos] = grid[ypos][xpos + 1]
                    grid[ypos][xpos + 1] = self
                    self.has_moved = True
                elif (environment["wind"] < 0) and (xpos - 1 >= 0) and (grid[ypos][xpos - 1].density < self.density): #je vlavo grid a blok s mensiou hustotou
                    grid[ypos][xpos] = grid[ypos][xpos - 1]
                    grid[ypos][xpos - 1] = self
                    self.has_moved = True

            elif not self.has_moved and tag == 3: # sticky-down
                self.stability = block_types[list(block_types.keys())[grid[ypos][xpos].id]]["stability"] #resetne sa na defaultnu stabilitu
                if (environment["wind"] > 0): #fuka vietor doprava
                    for adjpos in close_adjacent:
                        if not (xpos + adjpos[1] <= grid_size[1]) or not (xpos + adjpos[1] >= 0) or not (ypos + adjpos[0] >= 0): #ak neni v gridu, okrem spodku = skip
                            self.stability =- 1
                            continue
                        grid[ypos - 1][xpos].stability = block_types[list(block_types.keys())[grid[ypos - 1][xpos].id]]["stability"] #reset neresetnutych blokov
                        grid[ypos][xpos - 1].stability = block_types[list(block_types.keys())[grid[ypos][xpos - 1].id]]["stability"]
                        if not (ypos + adjpos[0] <= grid_size[0]): #je na spodku
                            self.stability += 10
                            continue
                        else:
                            self.stability += grid[ypos + adjpos[0]][xpos + adjpos[1]].stability
                if (environment["wind"] < 0): #fuka vietor dolava
                    for adjpos in close_adjacent:
                        if not (xpos + adjpos[1] <= grid_size[1]) or not (xpos + adjpos[1] >= 0) or not (ypos + adjpos[0] >= 0): #ak neni v gridu, okrem spodku = skip
                            self.stability =- 1
                            continue
                        grid[ypos - 1][xpos].stability = block_types[list(block_types.keys())[grid[ypos - 1][xpos].id]]["stability"] #reset neresetnutych blokov
                        grid[ypos][xpos + 1].stability = block_types[list(block_types.keys())[grid[ypos][xpos + 1].id]]["stability"]
                        if not (ypos + adjpos[0] <= grid_size[0]): #je na spodku
                            self.stability += 10
                            continue
                        else:
                            self.stability += grid[ypos + adjpos[0]][xpos + adjpos[1]].stability
                # print(self.stability)
                if ypos + 1 <= grid_size[0]: #je dole grid
                    if grid[ypos + 1][xpos].density < self.density: #je pod nim blok s mensiou hustotou
                        if (self.stability) <= 0: #mala stabilita = spadne
                            grid[ypos][xpos] = grid[ypos + 1][xpos]
                            grid[ypos + 1][xpos] = self
                            self.has_moved = True

            elif not self.has_moved and tag == 10: #up
                if (ypos - 1 >= 0) and (grid[ypos - 1][xpos].density > self.density) and (grid[ypos - 1][xpos].density < 500): #je hore grid a plinovy blok s vacsiou hustotou
                    grid[ypos][xpos] = grid[ypos - 1][xpos] #vymeni seba za block do ktoreho pozicie ide
                    grid[ypos - 1][xpos] = self #da seba do cielovej pozicie
                    self.has_moved = True

            elif not self.has_moved and tag == 11: # up side
                if (ypos - 1 >= 0): #je hore grid
                    if (environment["wind"] > 0): #fuka vietor doprava
                        if (xpos + 1 <= grid_size[1]) and (grid[ypos - 1][xpos + 1].density > self.density) and (grid[ypos - 1][xpos + 1].density < 500): #je napravo grid a napravo hore blok s vacsiou hustotou
                            grid[ypos][xpos] = grid[ypos - 1][xpos + 1]
                            grid[ypos - 1][xpos + 1] = self
                            self.has_moved = True
                        elif (xpos - 1 >= 0) and (grid[ypos - 1][xpos - 1].density > self.density) and (grid[ypos - 1][xpos - 1].density < 500): #je vlavo grid a vlavo hore blok s vacsiou hustotou
                            grid[ypos][xpos] = grid[ypos - 1][xpos - 1]
                            grid[ypos - 1][xpos - 1] = self
                            self.has_moved = True
                    if (environment["wind"] < 0): #fuka vietor dolava
                        if (xpos - 1 >= 0) and (grid[ypos - 1][xpos - 1].density > self.density) and (grid[ypos - 1][xpos - 1].density < 500): #je vlavo grid a vlavo hore blok s vacsiou hustotou
                            grid[ypos][xpos] = grid[ypos - 1][xpos - 1]
                            grid[ypos - 1][xpos - 1] = self
                            self.has_moved = True
                        elif (xpos + 1 <= grid_size[1]) and (grid[ypos - 1][xpos + 1].density > self.density) and (grid[ypos - 1][xpos + 1].density < 500): #je napravo grid a napravo hore blok s vacsiou hustotou
                            grid[ypos][xpos] = grid[ypos - 1][xpos + 1]
                            grid[ypos - 1][xpos + 1] = self
                            self.has_moved = True

            elif not self.has_moved and tag == 12: # side-up
                if (environment["wind"] > 0) and (xpos + 1 <= grid_size[1]) and (grid[ypos][xpos + 1].density > self.density) and (grid[ypos][xpos + 1].density < 500): #je napravo grid a plinovy blok s vacsiou hustotou
                    grid[ypos][xpos] = grid[ypos][xpos + 1]
                    grid[ypos][xpos + 1] = self
                    self.has_moved = True
                elif (environment["wind"] < 0) and (xpos - 1 >= 0) and (grid[ypos][xpos - 1].density > self.density) and (grid[ypos][xpos - 1].density < 500): #je vlavo grid a plinovy blok s vacsiou hustotou
                    grid[ypos][xpos] = grid[ypos][xpos - 1]
                    grid[ypos][xpos - 1] = self
                    self.has_moved = True

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
