import logging

from PySide2 import QtCore, QtGui

log = logging.getLogger(__name__)

class Settings(QtCore.QSettings):
    """
    Wrap QSettings

    ``__default_settings__``
        Default values of settings
    """

    __default_settings__ = {
        'app/language': 'en',
        'tagging/autotag_title': 0,
        'tagging/autotag_title_format': 'Sermon {}-{}-{}',
        'tagging/default_title': '',
        'tagging/default_artist': '',
        'tagging/default_genre': '',
        'tagging/default_album': '',
        'effects/normalize': 1,
        'effects/normalize_value': -6,
        'export/default_folder': '',
        'export/export_based_on_autotag': 0
    }

    __file_path__ = 'sermoncut.ini'

    def __init__(self, *args):
        log.debug("Setting up .ini file")
        QtCore.QSettings.__init__(self,'sermoncut.ini', Settings.IniFormat)
    def setup_defaults(self):
        for key, value in self.__default_settings__.items():
            if not self.contains(key):
                log.debug("Key: {} is not set in ini file. Setting default value: {}".format(key, value))
                self.setValue(key, value)
