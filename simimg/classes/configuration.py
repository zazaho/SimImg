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
        self.ConfigurationDict = {}
        self.set('cmdlinearguments', sys.argv[1:])
        self.set('iconpath', os.path.join(ScriptPath, 'icons'))
        self.set('databasename', os.path.join(ConfigPath,'simimg.db'))

        self._setDefaultConfiguration()
        self._readConfiguration()

        try:
            import imagehash
            self.set('haveimagehash', True)
        except ModuleNotFoundError:
            self.set('haveimagehash', False)

    def _setDefaultConfiguration(self):
        'Default configuration parameters'
        # not yet? configurable
        self.set('thumbnailborderwidth', 3)
        self.set('maxthumbnails', 300)
        # can be overwritten from ini file
        self.set('searchinsubfolders', False)
        self.set('confirmdelete', True)
        self.set('gzipinsteadofdelete', False)
        self.set('savesettings', True)
        self.set('showbuttons', True)
        self.set('thumbnailsize', 150)
        self.set('startupfolder', '')
        self.set('findergeometry', '1200x800+0+0')
        self.set('viewergeometry', '1200x800+50+0')

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
            self.set('searchinsubfolders', HF.str2bool(doRecursive, default=True))
            self.set('confirmdelete', HF.str2bool(confirmdelete, default=True))
            self.set('gzipinsteadofdelete', HF.str2bool(doGzip, default=True))
            self.set('savesettings', HF.str2bool(savesettings, default=True))
            self.set('showbuttons', HF.str2bool(showbuttons, default=True))
            self.set('thumbnailsize', thumbSize)
            self.set('startupfolder', startupDir)
            self.set('findergeometry', finderGeometry)
            self.set('viewergeometry', viewerGeometry)

    def writeConfiguration(self):
        'save configuration info'

        # save settings disabled
        if not self.get('savesettings'):
            return

        config = configparser.ConfigParser()
        config['simimg'] = {
            'searchinsubfolders':self.get('searchinsubfolders'),
            'confirmdelete':self.get('confirmdelete'),
            'gzipinsteadofdelete':self.get('gzipinsteadofdelete'),
            'savesettings':self.get('savesettings'),
            'showbuttons':self.get('showbuttons'),
            'thumbnailsize':self.get('thumbnailsize'),
            'startupfolder':self.get('startupfolder'),
            'findergeometry':self.get('findergeometry'),
            'viewergeometry':self.get('viewergeometry')
        }
        with open(self.IniPath, 'w') as configfile:
            config.write(configfile)

    def get(self, parameter):
        'Return one value of the configuration'
        if not parameter in self.ConfigurationDict:
            return None
        return self.ConfigurationDict[parameter]

    def set(self, param, value):
        'Add/Change a configuration parameter'
        self.ConfigurationDict[param] = value
