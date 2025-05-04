from Module.Initialization.DefaultLogger import getLogger
from Module.Initialization.ModuleInterface import Module


class GlobalWorkspace(Module):
    def __init__(self):
        super().__init__()
        self.logger = getLogger(self.__class__.__name__).logger

    def addCoalition(self, coalition):
        pass

    def addBroadcastTrigger(self, trigger):
        pass

    def getBroadcastSentCount(self):
        pass

    def getTickAtLastBroadcast(self):
        pass

    def setCoalitionDecayStrategy(self, decay_strategy):
        pass

    def getCoalitionDecayStrategy(self):
        pass

    def __getstate__(self):
        pass

    def notify(self, module):
        pass