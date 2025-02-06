import gymnasium as gym
from gymnasium.utils.play import play
import pygame as pg

if __name__ == '__main__':
    env = gym.make('crossroad_envs:CrossRoad', render_mode='rgb_array', fps=5)
    print(env.observation_space.shape[0])
    print(env.action_space.n)
    
    play(env, keys_to_action={
                              (pg.K_RIGHT,):0,
                              (pg.K_UP,):1,
                              (pg.K_LEFT,):2,
                              (pg.K_DOWN,):3},
                              noop=4)