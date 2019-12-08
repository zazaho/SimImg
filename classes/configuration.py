''' Class related to all configuration options '''
import os.path

class Configuration(object):
    ' Object that can initialise, change and inform about App configuration'
    def __init__(self, Arguments=None, ScriptPath=None, IconPath=None):
        self.Arguments = Arguments
        self.ScriptPath = ScriptPath
        self.IconPath = IconPath
        self.ConfigurationDict = {}
        self.readConfiguration()

    def readConfiguration(self):
        'Get the configuration parameters'
        # for now hard coded
        self.ConfigurationDict['doRecurse'] = True
        self.ConfigurationDict['DATABASENAME'] = os.path.expanduser('~/.config/SimImg/SimImg.db')
        self.ConfigurationDict['nx_grid'] = 5
        self.ConfigurationDict['ny_grid'] = 4
        self.ConfigurationDict['ThumbImageSize'] = (150, 150)
        self.ConfigurationDict['ThumbBorderWidth'] = 3
        self.ConfigurationDict['CmdLineArguments'] = self.Arguments
        self.ConfigurationDict['ScriptPath'] = self.ScriptPath
        self.ConfigurationDict['IconPath'] = self.IconPath

    def writeConfiguration(self):
        'save configuration info'
        pass

    def get(self, parameter):
        'Return one value of the configuration'
        if parameter in self.ConfigurationDict:
            return self.ConfigurationDict[parameter]
        else:
            return None

    def set(self, param, value):
        'Add/Change a configuration parameter'
        self.ConfigurationDict[param] = value
