import logging
import argparse
import sys
import os
from PySide2 import QtCore, QtWidgets, QtGui
from sermoncut.settings import Settings
from sermoncut.mainwindow import MainWindow
log = logging.getLogger(__name__)

class SermonCut(QtWidgets.QApplication):
    def run(self):
        self.setWindowIcon(QtGui.QIcon('images/SermonCut.ico'))

        settings = Settings()
        settings.setIniCodec("UTF-8")
        settings.setup_defaults()

        log.debug("Loading language")
        self.translator = QtCore.QTranslator(self)
        if self.translator.load('i18n/'+settings.value("app/language"), os.path.dirname(__file__)) == True:
            self.installTranslator(self.translator)
            log.debug("Languange: {}, loaded successfully.".format(settings.value("app/language")))
        else:
            log.error("Failed to load language: {}".format(settings.value("app/language")))

        self.main_window = MainWindow()

        self.main_window.show()
        return self.exec_()
def parse_options(args=None):
    """
    Parse the command line arguments

    :param args: list of command line arguments
    :return: a tuple of parsed options of type optparse.Value and a list of remaining argsZ
    """
    # Set up command line options.
    parser = argparse.ArgumentParser(prog='sermoncut')
    parser.add_argument('-l', '--log-level', dest='loglevel', default='debug', metavar='LEVEL',
                        help='Set logging to LEVEL level. Valid values are "debug", "info", "warning".')
    parser.add_argument('rargs', nargs='?', default=[])
    # Parse command line options and deal with them. Use args supplied pragmatically if possible.
    return parser.parse_args(args) if args else parser.parse_args()


def set_up_logging():
    """
    Setup our logging using log_path
    """
    log_path = 'sermoncut.log'
    logfile = logging.FileHandler(str(log_path), 'w', encoding='UTF-8')
    logfile.setFormatter(logging.Formatter('%(asctime)s %(name)-55s %(levelname)-8s %(message)s'))
    log.addHandler(logfile)
    if log.isEnabledFor(logging.DEBUG):
        print('Logging to: {name}'.format(name=log_path))

def exception_hook(exc_type, exc_value, exc_traceback):
    log.error(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    old_hook(exc_type, exc_value, exc_traceback)

old_hook = sys.excepthook
sys.excepthook = exception_hook

def main(args=None):
    args = parse_options(args)
    qt_args = []
    if args and args.loglevel.lower() in ['d', 'debug']:
        log.setLevel(logging.DEBUG)
    elif args and args.loglevel.lower() in ['w', 'warning']:
        log.setLevel(logging.WARNING)
    else:
        log.setLevel(logging.INFO)

    set_up_logging()

    application = SermonCut()
    #translator = QtCore.QTranslator(application)
    #translator.load('i18n/sv', os.path.dirname(__file__))
    #application.installTranslator(translator)
    application.setOrganizationName('SermonCut')
    application.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    application.setAttribute(QtCore.Qt.AA_DontCreateNativeWidgetSiblings, True)
    application.setApplicationName('SermonCut')
    application.run()




