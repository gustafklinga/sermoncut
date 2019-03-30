from PySide2.QtWidgets import QMainWindow,QShortcut, QFileDialog
from PySide2.QtCore import QUrl, QTranslator, QCoreApplication
from PySide2.QtGui import QKeySequence
from PySide2.QtMultimedia import QMediaPlayer, QMediaContent

import pydub
import pydub.utils
import pydub.exceptions

from sermoncut import utils
from sermoncut.ui.main_ui import Ui_MainWindow
from sermoncut.settings import Settings
from sermoncut.export import ExportThread
from sermoncut.version import Version

import logging
import os
import sys
from pathlib import PurePath

log = logging.getLogger(__name__)
settings = Settings()
settings.setIniCodec("UTF-8")

class MainWindow(QMainWindow, Ui_MainWindow):
    player = QMediaPlayer()
    player.setNotifyInterval(10)
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.connectUI()

        self.export_thread = ExportThread()
        self.export_thread.signalStatus.connect(self.export_handler)

        self.startCut = 0
        self.endCut = 0
        #Show version in statusbar when starting.
        version = Version().get_version()
        self.statusbar.showMessage(self.tr("Current version: {}").format(version), 50000)
    def connectUI(self):

        #Connect buttons
        self.playButton.clicked.connect(self.player.play)
        self.pauseButton.clicked.connect(self.player.pause)

        self.fileButton.clicked.connect(self.open_file)

        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.timeSlider.valueChanged.connect(self.player.setPosition)

        self.forwardButton.clicked.connect(lambda: self.jumpTime(30000))
        self.backButton.clicked.connect(lambda: self.jumpTime(-30000))

        self.startButton.clicked.connect(self.setStartCut)
        self.endButton.clicked.connect(self.setEndCut)

        self.exportButton.clicked.connect(self.start_export)

        #Menu bar
        self.actionExit.triggered.connect(self.close)
        self.actionSet_export.triggered.connect(self.set_export_folder)

        #Keyboard shortcuts
        self.shortcut_forward5 = QShortcut(QKeySequence("Right"), self)
        self.shortcut_forward5.activated.connect(lambda: self.jumpTime(5000))
        self.shortcut_back5 = QShortcut(QKeySequence("Left"), self)
        self.shortcut_back5.activated.connect(lambda: self.jumpTime(-5000))

        self.shortcut_forward10 = QShortcut(QKeySequence("Shift+Right"), self)
        self.shortcut_forward10.activated.connect(lambda: self.jumpTime(10000))
        self.shortcut_back10 = QShortcut(QKeySequence("Shift+Left"), self)
        self.shortcut_back10.activated.connect(lambda: self.jumpTime(-10000))

        self.shortcut_forward30 = QShortcut(QKeySequence("Ctrl+Right"), self)
        self.shortcut_forward30.activated.connect(lambda: self.jumpTime(30000))
        self.shortcut_back30 = QShortcut(QKeySequence("Ctrl+Left"), self)
        self.shortcut_back30.activated.connect(lambda: self.jumpTime(-30000))

        self.shortcut_startcut = QShortcut(QKeySequence("s"), self)
        self.shortcut_startcut.activated.connect(self.setStartCut)
        self.shortcut_endcut = QShortcut(QKeySequence("e"), self)
        self.shortcut_endcut.activated.connect(self.setEndCut)

        self.shortcut_play = QShortcut(QKeySequence("Space"), self)
        self.shortcut_play.activated.connect(lambda: self.playpause())


        # Setup default tagging options.
        self.titleEdit.setText(settings.value("tagging/default_title"))
        self.artistEdit.setText(settings.value("tagging/default_artist"))
        self.albumEdit.setText(settings.value("tagging/default_album"))
        self.genreEdit.setText(settings.value("tagging/default_genre"))

        # Setup default normalizing settings
        self.normalizeCheckbox.setChecked(bool(settings.value("effects/normalize")))
        self.normalizeEdit.setValue(int(settings.value("effects/normalize_value")))

    def playpause(self):
        if self.player.state() == 1: #Audio is playing
            self.player.pause()
        else:
            self.player.play()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Audio files (*.mp3 *.wav)")

        if path:
            self.player.setMedia(
                QMediaContent(
                    QUrl.fromLocalFile(path)
                )
            )
            self.fileEdit.setText(path)
            self.positionLabel.setText("0:00:00")

        # Import title from file if configured.
        if(int(settings.value("tagging/autotag_title")) == 1):
            log.debug("Starting autotag_title")

            mediainfo = pydub.utils.mediainfo(self.fileEdit.text()).get('TAG', None)
            if mediainfo: #Check if there is any mediainfo
                log.debug("Fetched title tag: {} from file: {}".format(mediainfo.get('title'), self.fileEdit.text()))

                date = mediainfo.get('title').split()
                date = date[1].split('/') #Split into month/date/year
                self.year = date[2]
                self.month = date[0]
                self.day = date[1]
                self.titleEdit.setText(settings.value("tagging/autotag_title_format").format(self.year, self.month, self.day))
            else:
                log.debug("Autotag_title: No metadata found")

        #Autofill export_folder
        if settings.value("export/default_folder"):
            exportpath = settings.value("export/default_folder")
        else:
            exportpath = os.path.abspath(os.path.dirname(sys.argv[0]))
            exportpath = exportpath.replace("\\", "/")

        #Fetches export-title based on date extracted from input mp3.
        if settings.value("export/export_based_on_autotag") == "1":
            date = self.year + "-" + self.month + "-" + self.day
            exportpath += "/" + date + ".mp3"
        else:
            #Defaults to inputfile name
            exportpath += "/{}.mp3".format(PurePath(self.fileEdit.text()).stem)
        self.exportEdit.setText(exportpath)

    def jumpTime(self, time):
        self.timeSlider.setValue(self.timeSlider.value()+time)
        self.timeSlider.update()


    def setStartCut(self):
        self.startCut = self.player.position()

        self.startEdit.setText(utils.hhmmss(self.startCut))
        self.update()

    def setEndCut(self):
        self.endCut = self.player.position()
        self.endEdit.setText(utils.hhmmss(self.endCut))
        self.update()

    def update_position(self, *args):
        position = self.player.position()
        if position >= 0:
            self.positionLabel.setText(utils.hhmmss(position))

        self.timeSlider.blockSignals(True)
        self.timeSlider.setValue(position)
        self.timeSlider.blockSignals(False)


    def update_duration(self, mc):
        self.timeSlider.setMaximum(self.player.duration())
        duration = self.player.duration()

        if duration >= 0:
            self.timeLabel.setText(utils.hhmmss(duration))

    def erroralert(self, *args):
        print(args)

    def start_export(self):
        title = self.titleEdit.text()
        artist = self.artistEdit.text()
        album = self.albumEdit.text()
        genre = self.genreEdit.text()
        exporttags = {'title': title, 'artist': artist, 'album': album, 'genre': genre}

        self.export_thread.input_file = self.fileEdit.text()
        self.export_thread.tags = exporttags
        self.export_thread.startCut = self.startCut
        self.export_thread.endCut = self.endCut
        self.export_thread.normalize = self.normalizeCheckbox.checkState()
        self.export_thread.normalizeValue = self.normalizeEdit.value() * -1 #Convert to positive value due to pydub.
        self.export_thread.export_file = self.exportEdit.text()
        log.debug("Starting thread to export.")
        self.export_thread.start()

        self.statusbar.showMessage(self.tr("Working on export. This can take some time. Please wait..."))

    def export_handler(self, message):
        if message == 1:
            self.statusbar.showMessage(self.tr("Export finished"))
        elif message == -1:
            self.statusbar.showMessage(self.tr('Encoding failed. See log for details.'))

    def set_export_folder(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOptions(QFileDialog.ShowDirsOnly)
        export_folder = dialog.getExistingDirectory(self, 'Choose Directory', os.path.curdir)
        settings.setValue("export/default_folder", export_folder)
        settings.sync()
        self.statusbar.showMessage(self.tr("Default export folder changed."), 2000)