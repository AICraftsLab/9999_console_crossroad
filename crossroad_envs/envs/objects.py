import pygame as pg
from enum import Enum

from crossroad_envs.envs.constants import *

class Direction(Enum):
    Right = 0
    Up = 1
    Left = 2
    Down = 3


class Block(pg.sprite.Sprite):
    image = None
    bg_rect = None
    def __init__(self, x, y, col, row, *groups):
        super().__init__(*groups)
        self.col = col
        self.row = row
        
        if not Block.image:
            image_width = CELL_SIZE
            image_height = CELL_SIZE
            image = pg.Surface((image_width, image_height))
            
            x_, y_ = 0, 0
            pg.draw.rect(image, CHARACTER_BORDER_COLOR, (x_, y_, CELL_SIZE, CELL_SIZE))
            x_ += CELL_BORDER_WIDTH
            y_ += CELL_BORDER_WIDTH
            pg.draw.rect(image, CHARACTER_INNER_BORDER_COLOR, (x_, y_, CELL_MIDDLE_SIZE, CELL_MIDDLE_SIZE))
            x_ += CELL_INNER_BORDER_WIDTH
            y_ += CELL_INNER_BORDER_WIDTH
            pg.draw.rect(image, CHARACTER_INNER_COLOR, (x_, y_, CELL_INNER_SIZE, CELL_INNER_SIZE))
            
            Block.image = image
            
        self.rect = self.image.get_rect().move(x, y)
            
    def move(self, direction):
        if direction == Direction.Right:
            self.col += 1
            self.rect.move_ip((CELL_SIZE, 0))
        elif direction == Direction.Up:
            self.row -= 2
            self.rect.move_ip((0, -CELL_SIZE * 2))
        elif direction == Direction.Left:
            self.col -= 1
            self.rect.move_ip((-CELL_SIZE, 0))
        elif direction == Direction.Down:
            self.row += 2
            self.rect.move_ip((0, CELL_SIZE * 2))
        
class PlayerBlock(Block):
    inflated_bg_rect = None
    def __init__(self, x, y, col, row, *groups):
        super().__init__(x, y, col, row, *groups)
        
    def update(self, **kwargs):
        action = kwargs.get('action')
        if action is None:
            raise Exception('Action parameter passed to player update method is none')
        
        if action == 'right':
            self.move(Direction.Right)
        elif action == 'up':
            self.move(Direction.Up)
        elif action == 'left':
            self.move(Direction.Left)
        elif action == 'down':
            self.move(Direction.Down)
        elif action == 'idle':
            pass
            
        if not PlayerBlock.inflated_bg_rect.contains(self.rect):
            self.rect.clamp_ip(Block.bg_rect)
            self.reverse_move(action)
            
    def reverse_move(self, action):
        if action == 'right':
            self.col -= 1
        elif action == 'up':
            self.row += 2
        elif action == 'left':
            self.col += 1
        elif action == 'down':
            self.row -= 2
            
    def mark_me(self, surface, center=True):
        if center:
            border = CELL_BORDER_WIDTH + CELL_INNER_BORDER_WIDTH
            x = self.rect.x + border
            y = self.rect.y + border
            rect = (x, y, CELL_INNER_SIZE, CELL_INNER_SIZE)
        else:
            rect = self.rect
        pg.draw.rect(surface, PLAYER_COLOR, rect)
        
    def drop_block(self, *groups):
        Block(self.rect.x, self.rect.y, self.col, self.row, *groups)

class TrainBlock(Block):
    """
    This represents a the body of a train. It acts as the obstacle for the player.
    """
    def __init__(self, x, y, col, row, direction, *groups):
        super().__init__(x, y, col, row, *groups)
        
        self.direction = direction
        
    def update(self, **kwargs):
        if self.direction == Direction.Right:
            if self.rect.right >= Block.bg_rect.right:
                self.rect.right = Block.bg_rect.left
                self.col = -1
        else:
            if self.rect.left <= Block.bg_rect.left:
                self.rect.left = Block.bg_rect.right
                self.col = self.rect.left // CELL_SIZE
        
        self.move(self.direction)


class Train:
    """
    A train is all the block running on a row. It is created from a list of 0's and 1's
    with 0's as empty/passable cells and 1's as train body (obstacle). Each body is a
    TrainBlock object.
    """
    def __init__(self, body, x, y, row, direction, *groups):
        for i, block in enumerate(body):
            if block == 0:
                continue
            x_ = x + CELL_SIZE * i  # block x pos
            col = i
            
            TrainBlock(x_, y, col, row, direction, *groups)
            