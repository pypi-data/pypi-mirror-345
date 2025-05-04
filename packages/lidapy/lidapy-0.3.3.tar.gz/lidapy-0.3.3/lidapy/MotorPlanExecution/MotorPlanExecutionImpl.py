import random
from time import sleep


from Module.Initialization.DefaultLogger import getLogger
from MotorPlanExecution.MotorPlanExecution import MotorPlanExecution
from SensoryMemory.SensoryMemory import SensoryMemory
from SensoryMotorMemory.SensoryMotorMemory import SensoryMotorMemory
from Sockets.Publisher import Publisher


class MotorPlanExecutionImpl(MotorPlanExecution):
    def __init__(self):
        super().__init__()
        self.motor_plans = {}
        self.state = None
        self.publisher = None
        self.connection = None
        self.schemes = None
        self.logger = getLogger(__class__.__name__).logger

    def start(self):
        self.logger.debug("Initialized Motor Plan Execution")

    def send_motor_plan(self):
        if self.motor_plans and self.state in self.motor_plans:
            motor_plans = self.motor_plans[self.state]
            return random.choice(motor_plans)

    def send_motor_plans(self):
        return self.motor_plans[self.state]

    def receive_motor_plan(self, state, motor_plan):
        if not self.motor_plans or state not in self.motor_plans:
            self.motor_plans[state] = []
            self.motor_plans[state].append(motor_plan)
        else:
            if motor_plan not in self.motor_plans[state]:
                self.motor_plans[state].append(motor_plan)

    def receive_motor_plans(self, state, motor_plans):
        for motor_plan in motor_plans:
            self.receive_motor_plan(state, motor_plan)


    def notify(self, module):
        if isinstance(module, SensoryMemory):
            cue = module.get_sensory_content(module)["cue"]
            for node in cue:
                content = node.getLabel()
                if isinstance(content, dict):
                    for key, value in content.items():
                        if key != self.schemes[0]:
                            self.state = node
                            self.receive_motor_plan(node, key)
            sleep(0.1)
            self.notify_observers()

        elif isinstance(module, SensoryMotorMemory):
            state = module.get_state()
            self.state = state
            motor_plan = module.send_action_execution_command()
            if len(motor_plan) >= 1:
                for action in motor_plan:
                    self.receive_motor_plan(state, action)
            self.notify_observers()

    def send_action_request(self):
        if self.publisher is None:
            self.publisher = Publisher()
        action = self.send_motor_plan()
        if action:
            request = self.publisher.create_request(data={'event':
                                {'type': 'action',
                                'agent': self.publisher.id,
                                'value': action}
                                })
            self.connection = self.publisher.connection
            reply = self.publisher.send(self.connection, request)
        return action