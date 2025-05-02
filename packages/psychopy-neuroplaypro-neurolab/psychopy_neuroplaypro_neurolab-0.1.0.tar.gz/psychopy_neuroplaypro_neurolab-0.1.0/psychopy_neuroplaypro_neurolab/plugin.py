from psychopy.plugins import Plugin
from psychopy.experiment.components import registerComponent
from psychopy_neuroplaypro_neurolab.components.neuroplay.neuroplay import NeuroPlayComponent

class NeuroPlayPlugin(Plugin):
    def onLoad(self):
        registerComponent("neuroplay", NeuroPlayComponent)
        print("NeuroPlay plugin loaded")
