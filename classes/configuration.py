import os.path
import configparser
import utils.handyfunctions as HF

class Configuration():
    ' Object that can initialise, change and inform about App configuration'
    def __init__(self, Arguments=None, ScriptPath=None):
        # The path of the appdata and ini file
        ConfigPath = os.path.join(
            os.environ.get('APPDATA') or
            os.environ.get('XDG_CONFIG_HOME') or
            os.path.join(os.environ['HOME'], '.config'),
            "SIMIMG"
        )
        self.IniPath = os.path.join(ConfigPath, 'SIMIMG.ini')

        # dict to store all settings
        self.ConfigurationDict = {
            'CmdLineArguments':Arguments,
            'IconPath':os.path.join(ScriptPath, 'icons'),
            'DATABASENAME':os.path.join(ConfigPath,'SIMIMG.db')
        }
        self.setDefaultConfiguration()
        self.readConfiguration()

    def setDefaultConfiguration(self):
        'Default configuration parameters'
        # not yet? configurable
        self.ConfigurationDict['ThumbBorderWidth'] = 3
        self.ConfigurationDict['MaxThumbnails'] = 300
        # can be overwritten from ini file
        self.ConfigurationDict['doRecurse'] = True
        self.ConfigurationDict['doConfirmDelete'] = True
        self.ConfigurationDict['doSaveSettings'] = True
        self.ConfigurationDict['ThumbImageSize'] = (150, 150)
        self.ConfigurationDict['MainGeometry'] = '1200x800+0+0'
        self.ConfigurationDict['ViewerGeometry'] = '1200x800+50+0'

    def readConfiguration(self):
        '''Function to get configurable parameters from SimImg.ini.'''
        # SearchInSubFolders [True]
        # confirm delete [True]
        # savesettings [True]
        # thumbsize [150]
        # windowposition [1200x800+0+0]
        # viewerposition [1200x800+50+0]
        config = configparser.ConfigParser()
        if config.read(self.IniPath):
            default = config['SIMIMG']
            doRecursive = default.get('searchinsubfolders', 'yes')
            doConfirmDelete = default.get('confirmdelete', 'yes')
            doSaveSettings = default.get('savesettings', 'yes')
            thumbSize = default.getint('thumbnailsize', 150)
            finderGeometry = default.get('finderposition', '1200x800+0+0')
            viewerGeometry = default.get('viewerposition', '1200x800+50+0')
            # store read values in ConfigurationDict
            self.ConfigurationDict['doRecurse'] = HF.str2bool(doRecursive, default=True)
            self.ConfigurationDict['doConfirmDelete'] = HF.str2bool(doConfirmDelete, default=True)
            self.ConfigurationDict['doSaveSettings'] = HF.str2bool(doSaveSettings, default=True)
            self.ConfigurationDict['ThumbImageSize'] = (thumbSize, thumbSize)
            self.ConfigurationDict['MainGeometry'] = finderGeometry
            self.ConfigurationDict['ViewerGeometry'] = viewerGeometry

    def writeConfiguration(self):
        'save configuration info'

        # save settings disabled
        if not self.ConfigurationDict['doSaveSettings']:
            return

        config = configparser.ConfigParser()
        config['SIMIMG'] = {
            'searchinsubfolders':self.ConfigurationDict['doRecurse'],
            'confirmdelete':self.ConfigurationDict['doConfirmDelete'],
            'savesettings':self.ConfigurationDict['doSaveSettings'],
            'thumbnailsize':self.ConfigurationDict['ThumbImageSize'][0],
            'finderposition':self.ConfigurationDict['MainGeometry'],
            'viewerposition':self.ConfigurationDict['ViewerGeometry']
        }
        with open(self.IniPath, 'w') as configfile:
            config.write(configfile)

    def get(self, parameter):
        'Return one value of the configuration'
        if parameter in self.ConfigurationDict:
            return self.ConfigurationDict[parameter]
        else:
            return None

    def set(self, param, value):
        'Add/Change a configuration parameter'
        self.ConfigurationDict[param] = value
