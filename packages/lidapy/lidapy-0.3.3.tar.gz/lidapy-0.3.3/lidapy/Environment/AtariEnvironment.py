import gym


from Environment.Environment import Environment
from Environment.FrozenLakeEnvironment import ActionMap
from MotorPlanExecution.MotorPlanExecution import MotorPlanExecution


class AtariEnvironment(Environment):
    def __init__(self):
        super().__init__()
        self.env = gym.make('Assault-v4')
        self.state = None

    def reset(self):
        self.state = self.env.reset()

    def step(self, action):
        self.state = self.env.step(action)

    def get_stimuli(self):
        return {"text" : {{"content" : self.state}, {"id" : 1},
                          {"position": None}}}

    def notify(self, module):
        if isinstance(module, MotorPlanExecution):
            action = ActionMap[module.send_motor_plan()]
            if not self.state["done"]:
                self.step(action)
            else:
                self.close()