import pydub
import logging
from PySide2 import QtCore
from sermoncut.settings import Settings
from pathlib import Path
import os

settings = Settings()
log = logging.getLogger(__name__)

class ExportThread(QtCore.QThread):
    signalStatus = QtCore.Signal(int)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        log.debug("Starting export. Inputfile: {}".format(self.input_file))

        # if settings.value("export/ffmpeg"):
        #     ffmpeg_path = Path(settings.value("export/ffmpeg")).joinpath("ffmpeg.exe")
        #     pydub.AudioSegment.converter = str(ffmpeg_path)
        #     ffprobe_path = Path(settings.value("export/ffmpeg")).joinpath("ffprobe.exe")
        #     pydub.AudioSegment.ffprobe = str(ffprobe_path)
        #
        #     log.debug("Setting custom encoder from ini-file: ".format(settings.value("export/ffmpeg")))
        ffmpeg_path = Path.cwd().joinpath("ffmpeg.exe")
        pydub.AudioSegment.converter = str(ffmpeg_path)
        try:
            #input = str(Path(self.input_file))
            output = pydub.AudioSegment.from_file(self.input_file)
            log.debug("Cutting audio. Start: {}, End: {}".format(self.startCut, self.endCut))
            output = output[self.startCut:self.endCut]  # Cut audio

            if int(self.normalize) == 2:
                log.debug("Normalizing audio. Normalize Value: {}".format(self.normalizeValue))
                if int(self.normalizeValue) > 0:
                    log.debug("Normalizing Audio to value: {}".format(int(self.normalizeValue)))
                    output = pydub.audio_segment.effects.normalize(output, int(self.normalizeValue))
            log.debug("Exporting audio to {}".format(self.export_file))
            self.export_path = Path(self.export_file)
            if self.export_path.suffix.lower() != ".mp3":
                raise ValueError("Export file does not end with .mp3")
            output.export(self.export_path, format="mp3", tags=self.tags)
            self.signalStatus.emit(1)
        except pydub.exceptions.CouldntDecodeError as err:
            log.exception(str(err))
            self.signalStatus.emit(-1)
        except:
            log.exception("Unexpected error.")
            self.signalStatus.emit(-1)
