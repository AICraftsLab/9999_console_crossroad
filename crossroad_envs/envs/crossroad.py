import gymnasium as gym
from gymnasium import spaces
import pygame as pg
import numpy as np
import sys

from crossroad_envs.envs.constants import *
from crossroad_envs.envs.objects import Block, PlayerBlock, Train, Direction


class CrossRoad(gym.Env):
    metadata = {'render_modes':['human', 'rgb_array']}
    
    def __init__(self, size=(10, 21), fov=2, render_mode=None, fps=3, caption='CrossRoad'):
        self.cols = size[0]
        self.rows = size[1]
        
        assert self.rows >= 7, 'Rows must be greater than 6'
        assert self.cols >= 5, 'Cols must be greater than 4'
        msg = f'Player field of view is greater than environment from top and bottom when it is' \
              f'at the middle of the environment. Current max value for FOV is {self.rows // 4}'
        assert  fov <= self.rows // 4, msg
        assert self.rows % 2 != 0, 'Environment rows must be odd'
        
        self.start_row = 3 # Home size, free 3 rows at the top
        
        # e.g. if fov * 2 = 4. Then it can see 4  rows up and 4 rows down
        # including the static rows. And of course it can see its own row.
        self.player_fov = fov * 2
        self.width = self.cols * CELL_SIZE
        self.height = self.rows * CELL_SIZE
        
        #CrossRoad.metadata['fps'] = fps
        CrossRoad.metadata['render_fps'] = fps
        
        # (self.player_fov + 1): +1 for player col
        # (self.cols + 1): Row length/cols + 1 for row train direction
        obs_num = (self.player_fov + 1) * (self.cols + 1)
        obs_num += 3  # player col, row, and lives
        
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(
            low=-1,
            high= 1,
            shape=(obs_num,),
            dtype=np.float32
        )
        
        assert render_mode is None or render_mode in CrossRoad.metadata['render_modes']
        self.render_mode = render_mode
        
        self.window = None
        self.clock = None
        self.surface = None
        self.bg = None
        self.caption = caption
            
        self.episode = -1
        
        self.bg_rect = pg.Rect(0, 0, self.width, self.height)
        self.inflated_bg_rect = self.bg_rect.inflate(BG_RECT_INFLATION, BG_RECT_INFLATION)
        
        PlayerBlock.inflated_bg_rect = self.inflated_bg_rect
        Block.bg_rect = self.bg_rect
        
    def _create_background(self):
        self.bg = pg.Surface((self.width, self.height))
        is_plain_row = False  # First row after goal rows is not plain
        start_y = self.start_row * CELL_SIZE
        for i in range(0, self.height, CELL_SIZE):
            for j in range(0, self.width, CELL_SIZE):
                x, y = j, i
                
                if i < start_y or is_plain_row:
                    cell_border_color = CELL_BORDER_COLOR
                    cell_inner_border_color = CELL_INNER_BORDER_COLOR
                    cell_inner_color = CELL_INNER_COLOR
                else:
                    cell_border_color = CHARACTER_BORDER_COLOR
                    cell_inner_border_color = CHARACTER_INNER_BORDER_COLOR
                    cell_inner_color = CHARACTER_INNER_COLOR
                    
                pg.draw.rect(self.bg, cell_border_color, (x, y, CELL_SIZE, CELL_SIZE))
                x += CELL_BORDER_WIDTH
                y += CELL_BORDER_WIDTH
                pg.draw.rect(self.bg, cell_inner_border_color, (x, y, CELL_MIDDLE_SIZE, CELL_MIDDLE_SIZE))
                x += CELL_INNER_BORDER_WIDTH
                y += CELL_INNER_BORDER_WIDTH
                pg.draw.rect(self.bg, cell_inner_color, (x, y, CELL_INNER_SIZE, CELL_INNER_SIZE))
            
            if i >= start_y:
                is_plain_row = not is_plain_row  # Alternating btw plain and bold
    
    def _create_trains(self, prob=0.3):
        for i in range(self.start_row + 1, self.rows - 2, 2):
            row = i
            col = 0
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            direction = self.np_random.choice([Direction.Right, Direction.Left])
            train = self._create_random_train(prob)  # Returns a list of 0's and 1's representing train
            Train(train, x, y, row, direction, self.trains_grp, self.obstacles_grp, self.all_sprites_grp)
    
    def _create_random_train(self, prob):
        """Returns a list of 0's and 1's"""
        train = [0 for i in range(self.cols)]
        
        for i in range(self.cols):
            if self.np_random.random() < prob :
                train[i] = 1
        return train
    
    def _get_info(self):
        return {'info':f'Episode:{self.episode} Blocks:{len(self.goal_blocks_grp)}'}

    def _get_observation(self):
        trains_positions = []
        blocks_positions = []
        trains_directions = {}
        
        for train in self.trains_grp:
            # If train not within FOV, skip it
            if abs(self.player.row - train.row) > self.player_fov:
                continue
            trains_positions.append((train.col, train.row))
            
            # All trains on the same row has same direction
            if train.row not in trains_directions:
                trains_directions[train.row] = int(train.direction == Direction.Right)
            
        for block in self.goal_blocks_grp:
            blocks_positions.append((block.col, block.row))
        
        data = []
        start_row = self.player.row - self.player_fov
        finish_row = self.player.row + self.player_fov
        #print(start_row, finish_row)
        
        # If player is at top and top of FOV is outside world, append -1s
        if start_row < 0:
            for _ in range(0, abs(start_row), 2):
                data.extend(-1 for x in range(self.cols + 1))  # +1 for direction
                start_row = 0
            
        for row in range(start_row, finish_row + 1, 2):
            # If row outside world at the bottom
            if row >= self.rows:
                data.extend(-1 for x in range(self.cols + 1))  # +1 for direction
                continue
            
            # the row's trains direction
            # default is 1:right. Returning default means the row has no
            # train or it is the goal row. Row with no train can happen when using
            # create_random_train with very low prob. Setting default to left/right won't
            # have any effect bcoz the row is empty, no train is coming. The agent can
            # even learn to take a rest and accumulate some reward there :)
            direction = trains_directions.get(row, 1)
            data.append(direction)
            
            # The row's trains
            for col in range(self.cols):
                position = col, row
                if position in trains_positions or position in blocks_positions:
                    data.append(1)
                else:
                    data.append(0)
        
        # Player position
        col = round(self.player.col / self.cols, 3)
        row = round(self.player.row / (self.rows - 1), 3)
        
        data.append(col)
        data.append(row)
        data.append(self.player_lives/PLAYER_LIVES)  # lives
        
        return np.array(data, dtype=np.float32)

    def _render_frame(self, player_death_rect=None):
        if self.window is None and self.render_mode == 'human':
            self.window = pg.display.set_mode((self.width, self.height))
            pg.display.set_caption(self.caption)
            self.clock = pg.time.Clock()
            
        if self.surface is None or self.bg is None:
            self.surface = pg.Surface((self.width, self.height))
            self._create_background()
        
        if not pg.font.get_init():
            pg.font.init()
            self.fonts = pg.font.SysFont('comicsans', 20)
        
        self.surface.blit(self.bg, (0, 0))
        self.all_sprites_grp.draw(self.surface)
        self.player.mark_me(self.surface)
        
        if player_death_rect:
            rect = player_death_rect.scale_by(3)
            rect.clamp_ip(self.bg_rect)
            pg.draw.rect(self.surface, PLAYER_COLOR, rect)
            
        self._render_texts()
        
        if self.render_mode == 'human':
            self.window.blit(self.surface, (0, 0))
            pg.display.flip()
            self.clock.tick(CrossRoad.metadata['render_fps'])
        else:  # rgb_array
            array = np.transpose(
                np.array(pg.surfarray.pixels3d(self.surface)), axes=(1, 0, 2)
            )
            return array
    
    def render(self):
        if self.render_mode == 'rgb_array':
            return self._render_frame()
    
    def _render_texts(self):
        episode_text = self.fonts.render('Episode: ' + str(self.episode), 1, TEXTS_COLOR)
        lives_text =  self.fonts.render('Lives: ' + str(self.player_lives), 1, TEXTS_COLOR)
        
        x, y = 5, 5
        self.surface.blit(episode_text, (x, y))
        
        y = episode_text.get_rect().bottom + 5
        self.surface.blit(lives_text, (x, y))
        
    def _soft_reset(self):
        self.trains_grp = pg.sprite.Group()
        self.obstacles_grp = pg.sprite.Group()
        self.all_sprites_grp = pg.sprite.Group()
        
        goal_blocks = self.goal_blocks_grp.sprites()
        self.all_sprites_grp.add(*goal_blocks)
        self.obstacles_grp.add(*goal_blocks)
        
        col = self.np_random.integers(self.cols)
        row = self.rows - 1
        x = col * CELL_SIZE
        y = row * CELL_SIZE
        self.player = PlayerBlock(x, y, col, row, self.all_sprites_grp)
        self._create_trains()
     
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.goal_blocks_grp = pg.sprite.Group()
        
        self._soft_reset()
        
        self.player_lives = PLAYER_LIVES
        self.episode += 1
        
        if self.render_mode == 'human':
            self._render_frame()
        
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info
        
    def step(self, action):
        if self.render_mode == 'human':
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    self.close()
                    sys.exit()
                
        player_death_rect = None
        step_reward = 0
        
        if action == 0:
            action = 'right'
        elif action == 1:
            action = 'up'
        elif action == 2:
            action = 'left'
        elif action == 3:
            action = 'down'
        elif action == 4:
            action = 'idle'

        self.all_sprites_grp.update(action=action)
        
        #step_reward = ((self.rows - 1) - self.player.row) / 10
        
        for _ in pg.sprite.spritecollide(self.player, self.obstacles_grp, 0):
            self.player.kill()
            #step_reward = -step_reward // 2
            step_reward -= 1
            self.player_lives -= 1
            player_death_rect = self.player.rect
            self._soft_reset() # last thing here
            
         
        # Must be after checking for collision with trains, else
        # the just dropped block will kill the player.
        # Drop, then soft_reset.
        player_at_goal = self.player.row == 0
        if self.player.alive() and player_at_goal:
            self.player.drop_block(self.goal_blocks_grp, self.obstacles_grp, self.all_sprites_grp)
            step_reward += 5
            self._soft_reset()
        
        finished = len(self.goal_blocks_grp) >= self.cols
        if finished:
            step_reward += 10
            
        terminated = self.player_lives <= 0 or finished
        info = self._get_info()
        observation = self._get_observation()
        reward = step_reward
        truncated = False
        
        if self.render_mode == 'human':
            self._render_frame(player_death_rect=player_death_rect)
        
        return observation, reward, terminated, truncated, info

    def close(self):
        if self.render_mode == 'human':
            pg.display.quit()
            pg.quit()
