import numpy as np
import random
import pygame
from os.path import exists
from sys import exit


class Maze:

    def __init__(self, size_x, size_y):

        self.screen = None

        self.screen_size = None

        self.screen_block_size = None

        self.screen_block_offset = None

        self.prev_update = 0

        self.clock = pygame.time.Clock()

        self.slow_mode = False

        self.running = True


        self.wall_size = np.array([size_y, size_x], dtype=np.int16)

        self.walls = np.ones((self.wall_size[0] + 2, self.wall_size[1] + 2, 3), dtype=np.byte)

        self.walls[:, 0, 0] = -1

        self.walls[:, self.wall_size[1] + 1, 0] = -1

        self.walls[0, :, 0] = -1

        self.walls[self.wall_size[0] + 1, :, 0] = -1


        self.block_size = np.array([size_y * 2 + 1, size_x * 2 + 1], dtype=np.int16)

        self.blocks = np.ones((self.block_size[0], self.block_size[1]), dtype=np.byte)


    def gen_maze_walls(self, corridor_len=999):

        cell = np.array([random.randrange(2, self.wall_size[0]), random.randrange(2, self.wall_size[1])], dtype=np.int16)

        self.walls[cell[0], cell[1], 0] = 0

        up    = np.array([-1,  0], dtype=np.int16)

        down  = np.array([ 1,  0], dtype=np.int16)

        left  = np.array([ 0, -1], dtype=np.int16)

        right = np.array([ 0,  1], dtype=np.int16)


        need_cell_range = False

        round_nr = 0

        corridor_start = 0

        if corridor_len <= 4:

            corridor_len = 5

        while np.size(cell) > 0 and self.running:

            round_nr += 1

            cell_neighbors = np.vstack((cell + up, cell + left, cell + down, cell + right))

            valid_neighbors = cell_neighbors[self.walls[cell_neighbors[:, 0], cell_neighbors[:, 1], 0] == 1]


            if np.size(valid_neighbors) > 0:

                neighbor = valid_neighbors[random.randrange(0, np.shape(valid_neighbors)[0]), :]

                if np.size(cell) > 2:

                    cell = cell[np.sum(abs(cell - neighbor), axis=1) == 1]

                    cell = cell[random.randrange(0, np.shape(cell)[0]), :]

                self.walls[neighbor[0], neighbor[1], 0] = 0

                self.walls[min(cell[0], neighbor[0]), min(cell[1], neighbor[1]), 1 + abs(neighbor[1] - cell[1])] = 0

                if self.screen is not None:

                    self.draw_cell(cell, neighbor)

                if round_nr - corridor_start < corridor_len:

                    cell = np.array([neighbor[0], neighbor[1]], dtype=np.int16)

                else:

                    need_cell_range = True


            else:

                if np.size(cell) > 2:

                    cell = np.zeros((0, 0))

                    if self.screen is not None:

                        pygame.display.flip()

                else:

                    need_cell_range = True


            if need_cell_range:

                cell = np.transpose(np.nonzero(self.walls[1:-1, 1:-1, 0] == 0)) + 1

                valid_neighbor_exists = np.array([self.walls[cell[:, 0] - 1, cell[:, 1], 0],

                                                  self.walls[cell[:, 0] + 1, cell[:, 1], 0],

                                                  self.walls[cell[:, 0], cell[:, 1] - 1, 0],

                                                  self.walls[cell[:, 0], cell[:, 1] + 1, 0]

                                                  ]).max(axis=0)

                cell_no_neighbors = cell[valid_neighbor_exists != 1]

                self.walls[cell_no_neighbors[:, 0], cell_no_neighbors[:, 1], 0] = -1

                corridor_start = round_nr + 0

                need_cell_range = False

        if self.running:

            return self.walls[1:-1, 1:-1, 1:3]

    def gen_maze_2D(self, corridor_len=999):


        self.gen_maze_walls(corridor_len)

        if self.running:

            self.blocks[1:-1:2, 1:-1:2] = 0

            self.blocks[1:-1:2, 2:-2:2] = self.walls[1:-1, 1:-2, 2]

            self.blocks[2:-2:2, 1:-1:2] = self.walls[1:-2, 1:-1, 1]

            return self.blocks

    def draw_cell(self, cell, neighbor):

        min_coord = (np.flip(np.minimum(cell, neighbor) * 2 - 1) * self.screen_block_size + self.screen_block_offset).astype(np.int16)

        max_coord = (np.flip(np.maximum(cell, neighbor) * 2 - 1) * self.screen_block_size + int(self.screen_block_size) + self.screen_block_offset).astype(np.int16)
        pygame.draw.rect(self.screen, (200, 200, 200), (min_coord, max_coord - min_coord))

        if self.slow_mode or pygame.time.get_ticks() > self.prev_update + 50:

            self.prev_update = pygame.time.get_ticks()

            pygame.display.flip()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    self.running = False
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:

                        self.running = False
                    if event.key == pygame.K_f:

                        self.toggle_fullscreen()
                    if event.key == pygame.K_m:

                        self.toggle_slow_mode()

        if self.slow_mode:

            pygame.time.wait(3)

    def toggle_slow_mode(self):

        self.slow_mode = not(self.slow_mode)

    def toggle_fullscreen(self):

        screen_copy = self.screen.copy()

        pygame.display.toggle_fullscreen()

        self.screen.blit(screen_copy, (0, 0))

        pygame.display.flip()

    def save_image(self):

        for file_nr in range(1, 1000):

            file_name = 'Maze_' + ('00' + str(file_nr))[-3:] + '.png'

            if not exists(file_name):

                pygame.image.save(self.screen, file_name)
                break


if __name__ == '__main__':

    pygame.display.init()

    disp_size = (1920, 1080)

    rect = np.array([0, 0, disp_size[0], disp_size[1]])

    block_size = 10

    screen = pygame.display.set_mode(disp_size)

    pygame.display.set_caption('Maze.py')

    running = True

    while running:

        maze = Maze(rect[2] // (block_size * 2) - 1, rect[3] // (block_size * 2) - 1)

        maze.screen = screen

        screen.fill((0, 0, 0))

        maze.screen_size = np.asarray(disp_size)

        maze.screen_block_size = np.min(rect[2:4] / np.flip(maze.block_size))

        maze.screen_block_offset = rect[0:2] + (rect[2:4] - maze.screen_block_size * np.flip(maze.block_size)) // 2

        start_time = pygame.time.get_ticks()

        print(f'Generating a maze of {maze.wall_size[1]} x {maze.wall_size[0]} = {maze.wall_size[0] * maze.wall_size[1]} cells. Block size = {block_size}.')
        maze.gen_maze_2D()

        if maze.running:

            print('Ready. Time: {:0.2f} seconds.'.format((pygame.time.get_ticks() - start_time) / 1000.0))

            print('ESC or close the Maze window to end program. SPACE BAR for a new maze. UP & DOWN cursor keys to change block size. s to save maze image.')
        else:

            print('Aborted.')

        pygame.event.clear()

        running = maze.running

        pausing = maze.running

        while pausing:

            event = pygame.event.wait()

            if event.type == pygame.QUIT:

                pausing = False

                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    
                    pausing = False

                if event.key == pygame.K_f:

                    maze.toggle_fullscreen()
                if event.key == pygame.K_s:

                    maze.save_image()
                if event.key == pygame.K_DOWN:

                    block_size -= 1

                    if block_size < 1:

                        block_size = 1
                    pausing = False
                if event.key == pygame.K_UP:

                    block_size += 1
                    if block_size > min(rect[2], rect[3]) // 10:

                        block_size = min(rect[2], rect[3]) // 10
                    pausing = False
                if event.key == pygame.K_ESCAPE:
                    pausing = False
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pausing = False

    pygame.quit()
    exit()
