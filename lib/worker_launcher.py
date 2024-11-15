from PyQt5.QtCore import QThread, pyqtSignal

from lib.utils import join_path, build_alert_box
from lib.worker import DownloadWorker


class WorkerLauncher(QThread):

    file_downloaded = pyqtSignal(bool)
    download_finished = pyqtSignal(bool)

    def __init__(self, download_widget):
        self.download_widget = download_widget

        QThread.__init__(self)

    def run(self):
        self.thread_list = []

        self.download_widget.workers_count = self.download_widget.parent.settings_widget.workers_spinbox.value()
        self.download_widget.max_retries = self.download_widget.parent.settings_widget.retries_spinbox.value()

        for _ in range(self.download_widget.workers_count):
            thread = DownloadWorker(self.download_widget.download_queue,
                                    self.download_widget.fingerprint['sha'], self.download_widget.assets_host,
                                    self.download_widget.enable_compression_checkbox.isChecked(),
                                    join_path(self.download_widget.parent.settings_widget.folder_path_input.text(),
                                              self.download_widget.fingerprint['sha']),
                                    self.download_widget.max_retries
                                    )

            self.thread_list.append(thread)
            thread.file_downloaded.connect(self.emit_file_downloaded)
            thread.max_retries_reached.connect(self.max_retries_reached)
            thread.start()

        self.download_widget.download_queue.join()

        self.stop()
        self.download_finished.emit()

    def emit_file_downloaded(self, update_status):
        self.file_downloaded.emit(update_status)

    def max_retries_reached(self, boolean):
        if boolean == True:
            self.stop()
            print("Max retries reached")
            self.download_finished.emit(False)

    def stop(self):
        for thread in self.thread_list:
            thread.stop()
