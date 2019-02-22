#!/usr/bin python3
import pygame
import os
import re
import grid_object as grid_o
import minesweeper_constants as const

import debugger

class GameManager(object):
    def __init__(self):
        pygame.init()

        self.my_path = "%s/.." % os.path.dirname(os.path.realpath(__file__))

        logo = pygame.image.load("%s/img/minesweeper_logo.png" % self.my_path)
        pygame.display.set_icon(logo)

        pygame.display.set_caption("Minesweeper")

        self.screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))

        self.background_tex = pygame.image.load("%s/img/background.png" % self.my_path)
        self.cell_textures = [
            pygame.image.load("%s/img/cell/cell_hidden.png" % self.my_path),
            pygame.image.load("%s/img/cell/cell_revealed.png" % self.my_path),
            pygame.image.load("%s/img/cell/mine.png" % self.my_path),
            pygame.image.load("%s/img/cell/mine_red.png" % self.my_path),
            pygame.image.load("%s/img/cell/mine_green.png" % self.my_path),
            pygame.image.load("%s/img/cell/flag.png" % self.my_path)
        ]
        self.number_tex_list   = [
            pygame.image.load("%s/img/numbers/num_1.png" % self.my_path),
            pygame.image.load("%s/img/numbers/num_2.png" % self.my_path),
            pygame.image.load("%s/img/numbers/num_3.png" % self.my_path),
            pygame.image.load("%s/img/numbers/num_4.png" % self.my_path),
            pygame.image.load("%s/img/numbers/num_5.png" % self.my_path),
            pygame.image.load("%s/img/numbers/num_6.png" % self.my_path),
            pygame.image.load("%s/img/numbers/num_7.png" % self.my_path),
            pygame.image.load("%s/img/numbers/num_8.png" % self.my_path)
        ]
        self.restart_button_list = [
            pygame.image.load("%s/img/restart_button/restart_button_green.png" % self.my_path),
            pygame.image.load("%s/img/restart_button/restart_button_yellow.png" % self.my_path),
            pygame.image.load("%s/img/restart_button/restart_button_red.png" % self.my_path),
            pygame.image.load("%s/img/restart_button/restart_button_green_clicked.png" % self.my_path),
            pygame.image.load("%s/img/restart_button/restart_button_yellow_clicked.png" % self.my_path),
            pygame.image.load("%s/img/restart_button/restart_button_red_clicked.png" % self.my_path)
        ]
        self.restart_button_rect = pygame.Rect(const.RESTART_BUTTON_COORD, const.RESTART_BUTTON_SIZE)

        # Highscore button
        self.highscore_button_tex         = pygame.image.load("%s/img/highscore.png" % self.my_path)
        self.highscore_button_clicked_tex = pygame.image.load("%s/img/highscore_clicked.png" % self.my_path)
        self.highscore_cur_tex = self.highscore_button_tex
        self.highscore_button_rect = pygame.Rect(const.HIGHSCORE_BUTTON_COORD, const.HIGHSCORE_BUTTON_SIZE)
        # Highscore panel
        self.highscore_panel_tex = pygame.image.load("%s/img/highscore_menu.png" % self.my_path)
        self.highscore_panel_rect = pygame.Rect(const.HIGHSCORE_PANEL_COORD, const.HIGHSCORE_PANEL_SIZE)
        self.showing_highscores = False
        self.highscore_list = []
        # Change name button
        self.change_name_button_tex          = pygame.image.load("%s/img/change_name_button.png" % self.my_path)
        self.change_name_button_clicked_tex  = pygame.image.load("%s/img/change_name_button_clicked.png" % self.my_path)
        self.change_name_button_changing_tex = pygame.image.load("%s/img/change_name_button_changing.png" % self.my_path)
        self.change_name_cur_tex = self.change_name_button_tex
        self.change_name_button_rect = pygame.Rect(const.CHANGE_NAME_COORD, const.CHANGE_NAME_SIZE)
        self.changing_name = False

        self.ui_font = pygame.font.SysFont("monospace", 50, True)
        self.highscore_font = pygame.font.SysFont("monospace", 30, True)
        self.name_font = pygame.font.SysFont("monospace", 25, True)

        self.player_name = const.PLAYER_NAME

        ##################
        # This part should match restart_game()
        self.grid = grid_o.Grid(self.cell_textures, self.number_tex_list)
        self.is_alive = True
        self.mines_placed = False
        self.mines_flagged = 0
        self.empty_flagged = 0
        self.restart_button_state = 0
        self.time_elapsed = 0
        self.last_frame_time = pygame.time.get_ticks()
        ##################

        # For input
        self.left_mouse_held = False
        self.last_left_click = 0
        self.right_mouse_held = False
        self.last_cell_held = None

        self.debug = debugger.Debugger("debug.log")

    def play_game(self):
        running = True
        while running:
            if self.is_alive and self.mines_placed and not self.showing_highscores:
                self.update_time()

            self.last_frame_time = pygame.time.get_ticks()

            if len(self.player_name) == 3:
                self.changing_name = False

            if self.changing_name:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return -1
                    if event.type == pygame.KEYDOWN:
                        if (event.key >= ord('a') and event.key <= ord('z')) or event.key in [ord('æ'), ord('ø'), ord('å')]:
                            self.player_name += chr(event.key).upper()
            else:
                input_exit_code = self.handle_input()
                if input_exit_code == -1:
                    running = False
                elif input_exit_code == 1:
                    self.restart_game()

            self.draw_game()

    def update_time(self):
        now = pygame.time.get_ticks()
        self.time_elapsed += now - self.last_frame_time

    def restart_game(self):
        self.grid = grid_o.Grid(self.cell_textures, self.number_tex_list)
        self.is_alive = True
        self.mines_placed = False
        self.mines_flagged = 0
        self.empty_flagged = 0
        self.restart_button_state = 0
        self.time_elapsed = 0
        self.last_frame_time = pygame.time.get_ticks()

    def handle_input(self):
        mouse_button_state = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_released = False
        if mouse_button_state[0] and not self.left_mouse_held:
            self.left_mouse_held = True
        elif not mouse_button_state[0] and self.left_mouse_held:
            self.left_mouse_held = False
            mouse_released = True

        # Restart button
        if self.restart_button_state > 2:
            self.restart_button_state -= 3
        if self.left_mouse_held and self.restart_button_rect.collidepoint(mouse_pos) and self.restart_button_state < 3:
            self.restart_button_state += 3
        if mouse_released and self.restart_button_rect.collidepoint(mouse_pos):
            return 1

        # Highscore button
        self.highscore_cur_tex = self.highscore_button_tex
        mouse_over_highscore = self.highscore_button_rect.collidepoint(mouse_pos)
        if self.left_mouse_held and mouse_over_highscore:
            self.highscore_cur_tex = self.highscore_button_clicked_tex
        if mouse_released and mouse_over_highscore:
            self.toggle_highscore_panel()

        if self.showing_highscores:
            # Change button
            self.change_name_cur_tex = self.change_name_button_tex
            mouse_over_change_name = self.change_name_button_rect.collidepoint(mouse_pos)
            if self.left_mouse_held and mouse_over_change_name:
                self.change_name_cur_tex = self.change_name_button_clicked_tex
            if mouse_released and mouse_over_change_name:
                self.change_name()

        if self.last_cell_held:
            self.last_cell_held.held = False
        clicked_cell = self.grid.get_clicked_cell(mouse_pos)
        if self.restart_button_state == 1:
            self.restart_button_state = 0
        if self.left_mouse_held and clicked_cell and not clicked_cell.is_revealed:
            clicked_cell.held = True
            self.last_cell_held = clicked_cell
            if self.is_alive and not clicked_cell.flagged:
                self.restart_button_state = 1


        elif mouse_released or mouse_button_state[2]:
            if clicked_cell and self.is_alive and not self.showing_highscores:
                double_click = False
                if mouse_released:
                    now = pygame.time.get_ticks()
                    if now - self.last_left_click < const.DOUBLE_CLICK_TIME:
                        double_click = True
                    self.last_left_click = now
                if not self.mines_placed:
                    self.grid.place_mines(const.MINE_COUNT, clicked_cell.idx, const.EMPTY_RADIUS)
                    self.mines_placed = True
                if (mouse_released and not clicked_cell.flagged) or (mouse_button_state[2] and not self.right_mouse_held):
                    self.right_mouse_held = True
                    clicked_exit_code = clicked_cell.clicked(mouse_released, double_click)
                    if clicked_exit_code == 1:
                        self.mines_flagged += 1
                    elif clicked_exit_code == -1:
                        self.mines_flagged -= 1
                    elif clicked_exit_code == 4:
                        self.empty_flagged += 1
                    elif clicked_exit_code == -4:
                        self.empty_flagged -= 1
                    elif clicked_exit_code == -2:
                        self.player_dies(clicked_cell)
                    elif clicked_exit_code == -3:
                        self.player_dies(clicked_cell.exploded_mine)

        elif not mouse_button_state[2] and self.right_mouse_held:
            self.right_mouse_held = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return -1
            #if event.type == pygame.KEYDOWN:
            #    if event.key == pygame.K_d:
            #        if clicked_cell:
            #            self.debug.write("Is flagged: %s\n" % str(clicked_cell.flagged))

        if self.mines_flagged == const.MINE_COUNT and self.empty_flagged == 0 and self.is_alive:
            self.player_wins()


    def player_dies(self, clicked_mine_cell):
        self.is_alive = False
        self.grid.reveal_all_mines()
        self.restart_button_state = 2
        clicked_mine_cell.highlight = True

    def player_wins(self):
        self.is_alive = False
        self.grid.reveal_all()
        self.try_save_highscore(int(self.time_elapsed / 1000), self.player_name)

    def draw_game(self):
        self.screen.blit(self.background_tex, (0,0))
        self.grid.draw(self.screen)
        self.draw_ui()
        pygame.display.flip()

    def draw_ui(self):
        self.screen.blit(self.restart_button_list[self.restart_button_state], self.restart_button_rect.topleft)
        self.screen.blit(self.highscore_cur_tex, self.highscore_button_rect.topleft)
        if self.showing_highscores:
            self.draw_highscore_panel()
        # Remaining mines label
        mines_left_count = const.MINE_COUNT - (self.mines_flagged + self.empty_flagged)
        if mines_left_count < -99:
            mines_left_count = -99
        mines_left_label = self.ui_font.render("%03d" % mines_left_count, 1, (250, 34, 28))
        self.screen.blit(mines_left_label, const.MINES_LEFT_LABEL_POS)
        # Time label
        time_in_seconds = int(self.time_elapsed / 1000)
        if time_in_seconds > 999:
            time_in_seconds = 999
        time_label = self.ui_font.render("%03d" % time_in_seconds, 1, (250, 34, 28))
        self.screen.blit(time_label, const.TIME_LABEL_POS)

    def draw_highscore_panel(self):
        self.screen.blit(self.highscore_panel_tex, self.highscore_panel_rect.topleft)
        self.load_highscores()
        text_pos = (self.highscore_panel_rect.topleft[0] + 100, self.highscore_panel_rect.topleft[1] + 20)
        ypos = text_pos[1]
        for i in range(len(self.highscore_list)):
            highscores_label = self.highscore_font.render(self.highscore_list[i], 1, (0, 26, 65))
            self.screen.blit(highscores_label, (text_pos[0], ypos))
            ypos += 35

        name_label = self.name_font.render("My name is %s" % self.player_name, 1, (0, 26, 65))
        self.screen.blit(name_label, (text_pos[0] + 40, ypos + 18))
        if not self.changing_name:
            self.screen.blit(self.change_name_cur_tex, self.change_name_button_rect.topleft)
        else:
            self.screen.blit(self.change_name_button_changing_tex, self.change_name_button_rect.topleft)

    def toggle_highscore_panel(self):
        self.showing_highscores = not self.showing_highscores

    def try_save_highscore(self, new_score, name):
        highscores = []
        new_highscore = False
        with open("%s/saved/highscores.txt" % self.my_path, "r") as hf:
            for line in hf:
                highscore_object = self.parse_highscore_line(line)
                highscores.append(highscore_object)
        for i in range(len(highscores)):
            if highscores[i][1] > new_score:
                highscores = highscores[:i+1] + highscores[i:9]
                highscores[i] = (name.upper(), new_score)
                new_highscore = True
                break
        if len(highscores) < 10 and not new_highscore:
            new_highscore = True
            highscores.append((name.upper(), new_score))
        with open("%s/saved/highscores.txt" % self.my_path, "w") as hf:
            for highscore in highscores:
                hf.write("%s %d\n" % (highscore[0], highscore[1]))

        return new_highscore

    def load_highscores(self):
        res = []
        count = 0
        with open("%s/saved/highscores.txt" % self.my_path, "r") as hf:
            for line in hf:
                count += 1
                highscore_object = self.parse_highscore_line(line)
                res.append("%02d:......%s......%03d" % (count, highscore_object[0], highscore_object[1]))
        self.highscore_list = res

    def parse_highscore_line(self, line):
        highscore_match = re.search("([a-zA-Z]*) ([0-9]*)", line)
        if highscore_match:
            return (highscore_match.group(1), int(highscore_match.group(2)))
        return None

    def change_name(self):
        self.player_name = ""
        self.changing_name = True
