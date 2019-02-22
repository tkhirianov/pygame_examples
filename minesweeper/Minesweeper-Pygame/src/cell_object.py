#!/usr/bin python3
import pygame
import minesweeper_constants as const
import debugger

class Cell(pygame.Rect):
    def __init__(self, left, top, width, height, textures, idx, grid):
        pygame.Rect.__init__(self, left, top, width, height)
        self.hidden_tex     = textures[0]
        self.revealed_tex   = textures[1]
        self.mine_tex       = textures[2]
        self.mine_red_tex   = textures[3]
        self.mine_green_tex = textures[4]
        self.flag_tex       = textures[5]
        self.number_tex     = None
        self.idx = idx
        self.grid = grid
        self.is_revealed = False
        self.is_mine = False
        self.flagged = False
        self.number = -1
        self.held = False
        self.highlight = 0

        self.exploded_mine = (-1, -1)

        self.debug = debugger.Debugger("debug.log")

    def place_mine(self):
        self.is_mine = True

    def set_num(self, number, number_tex):
        self.number = number
        if number > 0:
            self.number_tex = number_tex

    def clicked(self, leftclick, double_click):
        if leftclick: # left click
            if self.is_revealed and self.number > 0 and double_click:
                succesful_flag_count, self.exploded_mine = self.grid.get_cell_minecount(self.idx[0], self.idx[1], flags_override=True)
                if succesful_flag_count == self.number:
                    if self.exploded_mine:
                        return -3 # Exit code 3 means player double clicked a cell with wrong flags around it (and is now dead)
                    self.search_and_reveal()
            else:
                return self.reveal(True)
        else: # right click
            if self.is_revealed:
                return 0 # Exit code 0 means nothing special happened
            self.flagged = not self.flagged
            if self.flagged and self.is_mine:
                return 1 # Exit code 1 means a mine was flagged
            elif not self.flagged and self.is_mine:
                return -1 # Exit code -1 means a mine was unflagged
            elif self.flagged and not self.is_mine:
                return 4 # Exit code 3 means an empty cell was flagged
            elif not self.flagged and not self.is_mine:
                return -4 # Exit code 4 means an empty cell was unflagged
            else:
                return 0

    def reveal(self, player_click, reveal_all=False):
        """ 'A technically recursive function is still a recursive function' -Author """
        if self.flagged and not reveal_all:
            return 0
        if self.is_mine and player_click:
            self.is_revealed = True
            return -2 # Exit code -2 means player clicked mine (and is now dead)
        elif self.is_mine:
            return 0 # See exit code 0 in clicked()
        elif self.number > 0:
            self.is_revealed = True
            return 0 # See above
        self.is_revealed = True
        if player_click:
            self.search_and_reveal()
        else:
            return 2 # Exitcode 2 means search_and_reveal() should append the cell to it's search queue
        return 0 # See above

    def search_and_reveal(self):
        queue = [self.idx]
        seen = [self.idx]
        while len(queue) > 0:
            for i in range(queue[0][0]-1, queue[0][0]+2):
                for j in range(queue[0][1]-1, queue[0][1]+2):
                    if not (i < 0 or i > const.GRID_DIM[1]-1 or j < 0 or j > const.GRID_DIM[0]-1) \
                    and (i,j) not in seen and not self.grid.cells[i][j].is_revealed:
                        seen.append((i,j))
                        exit_code = self.grid.cells[i][j].reveal(False)
                        if exit_code == 2:
                            queue.append((i,j))
            queue = queue[1:]

    def draw(self, screen):
        if self.is_revealed:
            screen.blit(self.revealed_tex, self.topleft)
            if self.is_mine:
                if self.highlight == 1:
                    screen.blit(self.mine_red_tex, self.topleft)
                elif self.highlight == 2:
                    screen.blit(self.mine_green_tex, self.topleft)
                else:
                    screen.blit(self.mine_tex, self.topleft)
            elif self.number > 0:
                screen.blit(self.number_tex, self.topleft)
        else:
            if self.flagged:
                screen.blit(self.hidden_tex, self.topleft)
                screen.blit(self.flag_tex, self.topleft)
            elif self.held:
                screen.blit(self.revealed_tex, self.topleft)
            else:
                screen.blit(self.hidden_tex, self.topleft)
