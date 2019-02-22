#!/usr/bin python3
import random
import cell_object
import minesweeper_constants as const

class Grid(object):
    def __init__(self, cell_textures, number_tex_list):
        self.cells = []
        self.cell_textures = cell_textures
        self.number_tex_list = number_tex_list
        self.create_grid()

    def create_grid(self):
        self.cells = []
        pos = const.GRID_START_COORD
        for i in range(const.GRID_DIM[1]):
            row = []
            for j in range(const.GRID_DIM[0]):
                new_cell = cell_object.Cell(pos[0], pos[1], const.CELLSIZE, const.CELLSIZE, self.cell_textures, (i,j), self)
                row.append(new_cell)
                pos = (pos[0]+const.CELLSIZE, pos[1])
            self.cells.append(row)
            pos = (const.GRID_START_COORD[0], pos[1] + const.CELLSIZE)

    def place_mines(self, mine_amount, first_click_idx, empty_radius):
        """ Place mines is called after first click so the player never clicks a mine on first click.
            There is also some radius of empty cells from the players first click """
        remaining_positions = []
        for i in range(const.GRID_DIM[1]):
            for j in range(const.GRID_DIM[0]):
                dist_from_click = max(first_click_idx[0], i) - min(first_click_idx[0], i)\
                                + max(first_click_idx[1], j) - min(first_click_idx[1], j)
                if dist_from_click > empty_radius:
                    remaining_positions.append((i,j))
        if mine_amount >= len(remaining_positions):
            print("Too many mines!!")
            mine_amount = remaining_positions
        while mine_amount > 0:
            rand_idx = random.randint(0, len(remaining_positions)-1)
            rand_pos = remaining_positions[rand_idx]
            del remaining_positions[rand_idx]
            self.cells[rand_pos[0]][rand_pos[1]].place_mine()
            mine_amount -= 1

        self.distribute_numbers()

    def distribute_numbers(self):
        for i in range(const.GRID_DIM[1]):
            for j in range(const.GRID_DIM[0]):
                if self.cells[i][j].is_mine:
                    continue
                num, cell = self.get_cell_minecount(i, j)
                self.cells[i][j].set_num(num, self.number_tex_list[num-1])

    def get_cell_minecount(self, row, col, flags_override = False):
        count = 0
        mine_exploded = None
        for i in range(row-1, row+2):
            for j in range(col-1, col+2):
                if i < 0 or i > const.GRID_DIM[1]-1 or j < 0 or j > const.GRID_DIM[0]-1:
                    continue
                cell = self.cells[i][j]
                if flags_override:
                    if cell.flagged:
                        count += 1
                    elif cell.is_mine and not cell.flagged:
                        mine_exploded = cell
                else:
                    if cell.is_mine:
                        count += 1
        return count, mine_exploded

    def reveal_all_mines(self):
        for i in range(const.GRID_DIM[1]):
            for j in range(const.GRID_DIM[0]):
                if self.cells[i][j].is_mine:
                    self.cells[i][j].reveal(True, True)

    def reveal_all(self):
        for i in range(const.GRID_DIM[1]):
            for j in range(const.GRID_DIM[0]):
                self.cells[i][j].reveal(True, True)
                if self.cells[i][j].is_mine:
                    self.cells[i][j].highlight = 2 # Set to green highlight

    def get_clicked_cell(self, click_pos):
        for i in range(const.GRID_DIM[1]):
            for j in range(const.GRID_DIM[0]):
                if self.cells[i][j].collidepoint(click_pos):
                    return self.cells[i][j]
        return None

    def draw(self, screen):
        for i in range(const.GRID_DIM[1]):
            for j in range(const.GRID_DIM[0]):
                self.cells[i][j].draw(screen)
