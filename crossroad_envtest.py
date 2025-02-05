import gymnasium as gym
import crossroad_envs
from itertools import count

def pretty_print_obs(obs, env):
    print("Player Pos:", env.player.col, env.player.row)
    step = env.cols + 1  # +1 for row direction
    for i in range(0, len(obs), step):
        try:
            print(obs[i:i+step])
        except IndexError:
            print(obs[i:])

if __name__ == '__main__':
    #size=(33, 26)
    env = gym.make('CrossRoad', size=(10, 21), fps=1, fov=2, render_mode='human')
    print(env.observation_space.shape[0])
    print(env.action_space.n)
    seed = None
    for i in count():
        done = False
        observation, info = env.reset(seed=seed)
        pretty_print_obs(observation, env.unwrapped)
        env.action_space.seed(seed)
        episode_reward = 0
        while not done:
            action = env.action_space.sample()
            observation, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            episode_reward += reward
        
        print('Episode:', i, 'Reward:', episode_reward, info)
    env.close()