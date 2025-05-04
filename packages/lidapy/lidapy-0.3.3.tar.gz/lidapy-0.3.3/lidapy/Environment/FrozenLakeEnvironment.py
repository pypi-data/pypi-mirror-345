#LIDA Cognitive Framework
#Pennsylvania State University, Course : SWENG480
#Authors: Katie Killian, Brian Wachira, and Nicole Vadillo
import random
from time import sleep
import gymnasium as gym

from Environment.Environment import Environment
from Module.Initialization.DefaultLogger import getLogger
from MotorPlanExecution.MotorPlanExecution import MotorPlanExecution

"""
The environment is essential for receiving, processing, and
integrating all sensory information, enabling the agent to interact 
effectively.
Sends Sensory information to the Sensory Memory.
"""

ActionMap = {
        "up": 3,
        "right": 2,
        "down" : 1,
        "left" : 0
    }

class FrozenLakeEnvironment(Environment):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}
    def __init__(self, render_mode="human"):
        super().__init__()
        self.map_size = "8x8"
        # generating the frozen lake environment
        self.env = gym.make(
            'FrozenLake-v1',
            desc=None,
            is_slippery=False,
            map_name=self.map_size,
            render_mode=render_mode)

        self.action_space = self.env.action_space  # action_space attribute
        self.state = None
        self.row = 0
        self.col = 0
        self.steps = 0
        self.id = random.randint(1, 101)
        self.logger = getLogger(__class__.__name__).logger
        self.stimuli = {}
        self.action_plan = []

    # Reseting the environment to start a new episode
    def reset(self):
        self.logger.debug(f"Initialized {__class__.__name__} Environment")
        # interacting with the environment by using Reset()
        state, info = self.env.reset()
        surrounding_tiles = self.get_surrounding_tiles(self.row, self.col)

        self.state = {"state": state, "info": info, "done": False,
                      "outcome": surrounding_tiles}
        self.logger.info(f"state: {state}, " + f"info: {info}, " +
                         f"done: False")

        self.form_external_stimuli(surrounding_tiles)
        self.form_internal_stimuli(state)
        sleep(0.5)
        self.notify_observers()

    # perform an action in environment:
    def step(self, action):
        # perform and update
        state, reward, done, truncated, info = self.env.step(action)
        self.steps += 1
        self.update_position(action)
        surrounding_tiles = self.get_surrounding_tiles(self.row, self.col)

        self.state = {"state": state, "info": info, "done": done,
                      "outcome": surrounding_tiles}
        self.logger.info(f"state: {state}, " + f"info: {info}, " +
                         f"done: {done}, " + f"action: {action}")

        self.form_external_stimuli(surrounding_tiles)
        self.form_internal_stimuli(state)
        sleep(0.5)
        self.notify_observers()

    def recursive_step(self, action_plan):
        if action_plan is not None:
            for action in action_plan:
                if not self.state["done"] and self.steps < 1000:
                    state, reward, done, truncated, info = self.env.step(
                        action)
                    sleep(0.5)
                    self.steps += 1
                    self.update_position(action)
                    surrounding_tiles = self.get_surrounding_tiles(self.row,
                                                                    self.col)
                    self.state = {"state": state, "info": info,
                                  "done": done,
                                  "outcome": surrounding_tiles}
                    self.logger.info(
                        f"state: {state}, " + f"info: {info}, " +
                        f"done: {done}, " + f"action: {action}")

                    self.form_external_stimuli(surrounding_tiles)
                    self.form_internal_stimuli(state)
                    self.notify_observers()


    # render environment's current state:
    def render(self):
        self.env.render()

    def get_state(self):
        return self.state

    def get_stimuli(self):
        return {"text" : self.stimuli}

    def notify(self, module):
        if isinstance(module, MotorPlanExecution):
            action = ActionMap[module.send_motor_plan()]
            if not self.state["done"]:
                self.step(action)
            else:
                self.close()

    def update_position(self, action):
        if action == 3:  # up
            self.row = max(self.row - 1, 0)
        elif action == 2:  # Right
            self.col = min(self.col + 1, self.env.unwrapped.desc.shape[1] - 1)
        elif action == 1:  # down
            self.row = min(self.row + 1, self.env.unwrapped.desc.shape[0] - 1)
        elif action == 0:  # Left
            self.col = max(self.col - 1, 0)

    def get_surrounding_tiles(self, row, col):
        # gathering information about the tiles surrounding the agent
        desc = self.env.unwrapped.desc
        surrounding_tiles = {}
        directions = {
            "up": (max(row - 1, 0), col),
            "right": (row, min(col + 1, desc.shape[1] - 1)),
            "down": (min(row + 1, desc.shape[0] - 1), col),
            "left": (row, max(col - 1, 0)),
        }
        for direction, (r, c) in directions.items():
            surrounding_tiles[direction] = desc[r, c].decode(
                'utf-8')  # Decode byte to string
        return surrounding_tiles

    def form_external_stimuli(self, surrounding_tile):
        directions = {
            'up': 3,
            'right': 2,
            'down' : 1,
            'left' : 0
        }
        self.stimuli["content"] = {}
        for direction, tile in surrounding_tile.items():
            if tile == 'H':
                self.stimuli["content"][direction] = 'hole'
            elif tile == 'S':
                self.stimuli["content"][direction] = 'start'
            elif tile == 'G':
                self.stimuli["content"][direction] = 'goal'
            else:
                self.stimuli["content"][direction] = 'safe'

    def form_internal_stimuli(self, state):
        self.stimuli["position"] = [self.row, self.col]
        self.stimuli["id"] = state

    def get_position(self):
        return {"row": self.row, "col" : self.col}

    # close the environment:
    def close(self):
        self.env.close()