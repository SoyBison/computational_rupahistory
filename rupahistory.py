from pdb import main
from textwrap import wrap
from matplotlib.pyplot import draw
import numpy as np
import itertools
from copy import deepcopy
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import time
from matplotlib.patches import RegularPolygon
from matplotlib.animation import FuncAnimation


red = '#982649'
blue = '#60B2E5'
yellow = '#F6AE2D'
green = '#758E4F'
ocean = '#33658A'
coast = '#F9CB77'
unclaimed = '#FFFFFF'
hills = '#517664'
deepocean = '#084C61'
mountains = '#5F6D67'

def hex_distance(c1, c2):
    return (abs(c1[0]-c2[0]) + abs(c1[1]-c2[1]) + abs(c1[2] - c2[2])) / 2

def hex_left(c):
    return (-c[1], -c[2], -c[0])

def hex_right(c):
    return (-c[2], -c[0], -c[1])

def hex_rotations(c):
    out = [c]
    last = c
    for _ in range(5):
        new = hex_left(last)
        out.append(new)
        last = new
    return out

class Hex():
    def __init__(self, color):
        self.color = color
    
    def __repr__(self):
        return str(self.color)
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Grid():
    def __init__(self, size, wraparound=False):
        self.grid = {}
        self.size = size
        self._directions = np.array(list(itertools.permutations((0, -1, 1))))
        self.grid = self.fresh_grid()
        self.wraparound = wraparound
        if wraparound:
            self.generate_mirror_table()
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
        if (idx[0], idx[1], idx[2]) not in self.grid and self.wraparound:
            return self.grid[self.mirror_table[idx[0], idx[1], idx[2]]]
        return self.grid[idx[0], idx[1], idx[2]]
    
    def generate_neighbors(self):
        self.neighbor_grid = {}
        for cel in self.grid:
            neighbors = self._directions + np.array(cel)
            if not self.wraparound:
                self.neighbor_grid[cel] = {tuple(n) for n in neighbors if tuple(n) in self.grid}
            else:
                self.neighbor_grid[cel] = {tuple(n) for n in neighbors}

    def neighbors(self, idx):
        return self.neighbor_grid[idx]
    
    def random_colors(self):
        for k in self.grid:
            choices = [red, blue, yellow, green, unclaimed, ocean]
            results = np.random.choice(choices)
            self.grid[k].color = results
    
    def fresh_grid(self, center=(0,0,0)):
        grid = {}
        for x in range(-self.size + center[0], self.size + 1 + center[0]):
            for y in range(max(-self.size + center[1], -x - self.size + center[1]), min(self.size + center[1], -x + self.size + center[1])+1):
                z = -x - y
                grid[(x, y, z)] = Hex(unclaimed)
        return grid

    def land_and_water(self, water_coef=3, beach_coef=3, land_coef=.4, mt_coef=0.1, water_border=False, _time_limit=50):
        for k in self.grid:
            self[k].color = np.random.choice([green, mountains, ocean],
                                                 p=[land_coef, mt_coef, 1 - mt_coef - land_coef])
        self.record = [Grid.from_grid(self.grid, self.size, self.wraparound)]
        def generate(t=0):
            new_grid = deepcopy(self.grid)
            self.record.append(Grid.from_grid(new_grid, self.size, self.wraparound))
            for k in self.grid:
                selfcolor = self.grid[k].color
                neighbor_colors = np.array([self[n].color for n in self.neighbors(k)])

                oceans = (neighbor_colors == ocean).sum() 
                coasts = (neighbor_colors == coast).sum()
                plains = (neighbor_colors == green).sum()
                peaks = (neighbor_colors == mountains).sum()
                highlands = (neighbor_colors == hills).sum()
                if len(neighbor_colors) != 6 and water_border:
                    new_grid[k].color = ocean
                if selfcolor == green:
                    if oceans >= 1:
                        new_grid[k].color = coast
                    if highlands > beach_coef:
                        new_grid[k].color = hills
                    if peaks >= 1:
                        new_grid[k].color = hills
                elif selfcolor == hills:
                    if not (plains + oceans + coasts):
                        new_grid[k].color = mountains
                    if coasts >= 1:
                        new_grid[k].color = green
                elif selfcolor == mountains:
                    if oceans >= 1:
                        new_grid[k].color = coast
                elif selfcolor == coast:
                    if oceans > beach_coef:
                        new_grid[k].color = ocean
                    elif highlands >= 1:
                        new_grid[k].color = green
                    elif peaks >= 1:
                        new_grid[k].color = hills
                    elif not oceans:
                        new_grid[k].color = green

                elif selfcolor == ocean:
                    if coasts > water_coef:
                        new_grid[k].color = coast
                    if highlands:
                        new_grid[k].color = coast
            if self.grid == new_grid:
                self.grid = new_grid
            else:
                self.grid = new_grid
                if t >= _time_limit:
                    raise RecursionError
                generate(t=t+1)

        try:
            generate()
        except RecursionError:
            print('Recursion Depths Plumbed, Map did not stabilize.')
            pass
                
    def land_init(self, land_coef=.5):
        for k in self.grid:
            self[k].color = np.random.choice([green, ocean],
                                                 p=[land_coef, 1-land_coef])
    
    def generate_mirror_table(self):
        self.mirror_table = {}
        centers = hex_rotations((2*self.size+1, -self.size, -self.size - 1))
        for c in centers:
            for coord in self.grid:
                self.mirror_table[tuple(np.array(c) + np.array(coord))] = coord

    def __eq__(self, other):
        return self.grid == other.grid

    @classmethod
    def from_grid(cls, grid, size, wraparound):
        obj = cls(size=size, wraparound=wraparound)
        obj.grid=grid
        return obj

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

def animate_landgen(grid):
    fig, ax = plt.subplots(1, figsize=(20, 20))
    ax.set_aspect('equal')
    ax.axis('off')
    patch_list = []
    frame = grid.record[0]
    coords = frame.coords
    colors = frame.colors
    xcoord = coords[:, 0]
    ycoord = 2. * np.sin(np.radians(60)) * (coords[:, 1] - coords[:, 2]) /3.
    patch_list = []
    for x, y, c in zip(xcoord, ycoord, colors):
        hexes = RegularPolygon((x, y), numVertices=6, radius=(2/3), 
                                orientation=np.radians(30), facecolor=c, edgecolor='k', 
                                linewidth=.25)
        patch_list.append(hexes)
    patches = PatchCollection(patch_list, match_original=True)

    ax.add_collection(patches)
    ax.scatter(xcoord, ycoord, alpha=0)

    def update(frame):
        frame = grid.record[frame]
        coords = frame.coords
        colors = frame.colors
        xcoord = coords[:, 0]
        ycoord = 2. * np.sin(np.radians(60)) * (coords[:, 1] - coords[:, 2]) /3.
        patch_list = []
        for x, y, c in zip(xcoord, ycoord, colors):
            hexes = RegularPolygon((x, y), numVertices=6, radius=(2/3), 
                                    orientation=np.radians(30), facecolor=c, edgecolor='k', 
                                    linewidth=.25)
            patch_list.append(hexes)
        ax.patches = []
        patches = PatchCollection(patch_list, match_original=True)
        ax.add_collection(patches)
        return ax,

    ani = FuncAnimation(fig, update, frames=len(grid.record), blit=False, interval=5)
    ani.save('mapgen.gif', fps=5, dpi=100)

    return ani

if __name__ == "__main__":
    tic = time.time()
    grid = Grid(25, wraparound=False)
    toc1 = time.time()
    print(f'Generating the grid took {toc1 - tic}.')
    grid.land_and_water(water_border=True)
    toc2 = time.time()
    print(f'Generating the land took {toc2 - toc1}.')
    ani = animate_landgen(grid)
    toc3 = time.time()
    print(f'Making the animation took {toc3 - toc2} seconds.')
