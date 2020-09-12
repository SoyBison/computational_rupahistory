from pdb import main
import numpy as np
import itertools
from copy import deepcopy
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import time
from matplotlib.patches import RegularPolygon


red = '#982649'
blue = '#60B2E5'
yellow = '#F6AE2D'
green = '#758E4F'
ocean = '#33658A'
coast = '#F9CB77'
unclaimed = '#FFFFFF'

class Hex():
    def __init__(self, color):
        self.color = color
    
    def __repr__(self):
        return str(self.color)
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Grid():
    def __init__(self, size):
        self.grid = {}
        self.size = size
        self._directions = np.array(list(itertools.permutations((0, -1, 1))))
        self.grid = self.fresh_grid()
        self.generate_neighbors()


    def __str__(self):
        return str(self.grid)

    @property
    def coords(self):
        return np.array(list(self.grid.keys()))
    
    @property
    def colors(self):
        return [cell.color for cell in self.grid.values()]

    def __getitem__(self, idx):
        if idx[0] + idx[1] + idx[2] != 0:
            raise KeyError(f'{(idx[0], idx[1], idx[2])} is not a valid hex coordinate. '
                            'x + y + z must equal zero.')
        return self.grid[idx[0], idx[1], idx[2]]
    
    def generate_neighbors(self):
        self.neighbor_grid = {}
        for cel in self.grid:
            neighbors = self._directions + np.array(cel)
            self.neighbor_grid[cel] = {tuple(n) for n in neighbors if tuple(n) in self.grid}

    def neighbors(self, idx):
        return self.neighbor_grid[idx]
    
    def random_colors(self):
        for k in self.grid:
            choices = [red, blue, yellow, green, unclaimed, ocean]
            results = np.random.choice(choices)
            self.grid[k].color = results
    
    def fresh_grid(self):
        grid = {}
        for x in range(-self.size, self.size + 1):
            for y in range(max(-self.size, -x - self.size), min(self.size, -x + self.size)+1):
                z = -x - y
                grid[(x, y, z)] = Hex(unclaimed)
        return grid

    def land_and_water(self, water_coef=3, beach_coef=3, land_coef=.5):
        for k in self.grid:
            self[k].color = np.random.choice([1, 0],
                                                 p=[land_coef, 1-land_coef])

        def generate():
            new_grid = deepcopy(self.grid)

            for k in self.grid:
                selfcolor = self.grid[k].color
                neighbor_colors = np.array([self.grid[n].color for n in self.neighbors(k)])

                oceans = (neighbor_colors == 0).sum()
                coasts = (neighbor_colors == 2).sum()
                if selfcolor == 1:
                    if oceans >= 1:
                        new_grid[k].color = 2
                elif selfcolor == 2:
                    if oceans > beach_coef:
                        new_grid[k].color = 0
                    if not oceans:
                        new_grid[k].color = 1
                elif selfcolor == 0:
                    if coasts > water_coef:
                        new_grid[k].color = 2
            if self.grid == new_grid:
                self.grid = new_grid
            else:
                self.grid = new_grid
                generate()

        generate()
        
        conversion = {0: ocean, 1: green, 2: coast}

        for k in self.grid:
            self[k].color = conversion[self[k].color]
            
    
    def land_init(self, land_coef=.5):
        for k in self.grid:
            self[k].color = np.random.choice([green, ocean],
                                                 p=[land_coef, 1-land_coef])

    def __eq__(self, other):
        return self.grid == other.grid



def draw_map(grid, save=False, show=True):
    coords = grid.coords
    colors = grid.colors
    xcoord = coords[:, 0]
    ycoord = 2. * np.sin(np.radians(60)) * (coords[:, 1] - coords[:, 2]) /3.

    fig, ax = plt.subplots(1, figsize=(20, 20))
    ax.set_aspect('equal')
    patch_list = []
    for x, y, c in zip(xcoord, ycoord, colors):
        hexes = RegularPolygon((x, y), numVertices=6, radius=(2/3), 
                                orientation=np.radians(30), facecolor=c, edgecolor='k', 
                                linewidth=.25)
        patch_list.append(hexes)

    hexes = PatchCollection(patch_list, match_original=True)
    ax.add_collection(hexes)
    ax.axis('off')
    ax.scatter(xcoord, ycoord, alpha=0)
    if show:
        plt.show()
    if save:
        plt.savefig('map.png')

if __name__ == "__main__":
    tic = time.time()
    grid = Grid(25)
    toc1 = time.time()
    grid.land_and_water()
    toc2 = time.time()
    draw_map(grid, save=True, show=False)
    toc3 = time.time()

    print(f'Generating the grid took {toc1 - tic}.')
    print(f'Generating the land took {toc2 - toc1}.')
    print(f'Generating the map took {toc3 - toc2}.')