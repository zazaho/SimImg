import sys
import os.path
import configparser
import simimg.utils.handyfunctions as HF

class Configuration():
    ' Object that can initialise, change and inform about App configuration'
    def __init__(self, ScriptPath=None):
        # The path of the appdata and ini file
        ConfigPath = os.path.join(
            os.environ.get('APPDATA') or
            os.environ.get('XDG_CONFIG_HOME') or
            os.path.join(os.environ['HOME'], '.config'),
            "simimg"
        )
        self.IniPath = os.path.join(ConfigPath, 'simimg.ini')

        # dict to store all settings
        self.ConfigurationDict = {
            'cmdlinearguments':sys.argv[1:],
            'iconpath':os.path.join(ScriptPath, 'icons'),
            'databasename':os.path.join(ConfigPath,'simimg.db')
        }
        self._setDefaultConfiguration()
        self._readConfiguration()

        try:
            import imagehash
            self.ConfigurationDict['haveimagehash']=True
        except ModuleNotFoundError:
            self.ConfigurationDict['haveimagehash']=False
            
    def _setDefaultConfiguration(self):
        'Default configuration parameters'
        # not yet? configurable
        self.ConfigurationDict['thumbnailborderwidth'] = 3
        self.ConfigurationDict['maxthumbnails'] = 300
        # can be overwritten from ini file
        self.ConfigurationDict['searchinsubfolders'] = False
        self.ConfigurationDict['confirmdelete'] = True
        self.ConfigurationDict['gzipinsteadofdelete'] = False
        self.ConfigurationDict['savesettings'] = True
        self.ConfigurationDict['showbuttons'] = True
        self.ConfigurationDict['thumbnailsize'] = 150
        self.ConfigurationDict['startupfolder'] = ''
        self.ConfigurationDict['findergeometry'] = '1200x800+0+0'
        self.ConfigurationDict['viewergeometry'] = '1200x800+50+0'

    def _readConfiguration(self):
        '''Function to get configurable parameters from SimImg.ini.'''
        config = configparser.ConfigParser()
        if config.read(self.IniPath):
            default = config['simimg']
            doRecursive = default.get('searchinsubfolders', 'yes')
            confirmdelete = default.get('confirmdelete', 'yes')
            doGzip = default.get('gzipinsteadofdelete', 'no')
            savesettings = default.get('savesettings', 'yes')
            showbuttons = default.get('showbuttons', 'yes')
            thumbSize = default.getint('thumbnailsize', 150)
            startupDir = default.get('startupfolder', '.')
            finderGeometry = default.get('findergeometry', '1200x800+0+0')
            viewerGeometry = default.get('viewergeometry', '1200x800+50+0')
            # store read values in ConfigurationDict
            self.ConfigurationDict['searchinsubfolders'] = HF.str2bool(doRecursive, default=True)
            self.ConfigurationDict['confirmdelete'] = HF.str2bool(confirmdelete, default=True)
            self.ConfigurationDict['gzipinsteadofdelete'] = HF.str2bool(doGzip, default=True)
            self.ConfigurationDict['savesettings'] = HF.str2bool(savesettings, default=True)
            self.ConfigurationDict['showbuttons'] = HF.str2bool(showbuttons, default=True)
            self.ConfigurationDict['thumbnailsize'] = thumbSize
            self.ConfigurationDict['startupfolder'] = startupDir
            self.ConfigurationDict['findergeometry'] = finderGeometry
            self.ConfigurationDict['viewergeometry'] = viewerGeometry

    def writeConfiguration(self):
        'save configuration info'

        # save settings disabled
        if not self.ConfigurationDict['savesettings']:
            return

        config = configparser.ConfigParser()
        config['simimg'] = {
            'searchinsubfolders':self.ConfigurationDict['searchinsubfolders'],
            'confirmdelete':self.ConfigurationDict['confirmdelete'],
            'gzipinsteadofdelete':self.ConfigurationDict['gzipinsteadofdelete'],
            'savesettings':self.ConfigurationDict['savesettings'],
            'showbuttons':self.ConfigurationDict['showbuttons'],
            'thumbnailsize':self.ConfigurationDict['thumbnailsize'],
            'startupfolder':self.ConfigurationDict['startupfolder'],
            'findergeometry':self.ConfigurationDict['findergeometry'],
            'viewergeometry':self.ConfigurationDict['viewergeometry']
        }
        with open(self.IniPath, 'w') as configfile:
            config.write(configfile)

    def get(self, parameter):
        'Return one value of the configuration'
        if parameter in self.ConfigurationDict:
            return self.ConfigurationDict[parameter]

    def set(self, param, value):
        'Add/Change a configuration parameter'
        self.ConfigurationDict[param] = value
