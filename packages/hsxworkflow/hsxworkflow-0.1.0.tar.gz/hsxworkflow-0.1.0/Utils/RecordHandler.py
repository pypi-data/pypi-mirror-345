import os.path

from DataRecorder import Recorder, DBRecorder


class FileRecord:

    def __init__(self, recorder_type: str = "db", file_save: str = "one", **kwargs):
        self.recorder_type = recorder_type
        self.recorder = None
        self.save_type = file_save
        self.init_recorder(**kwargs)

    def record_path(self, **kwargs):
        if not kwargs.get('path'):
            kwargs['path'] = os.path.join('./fileRecord', f'workflow.{self.recorder_type}')

        path = kwargs.get('path', "")
        if self.save_type == "one":
            if os.path.exists(path):
                os.remove(path)
        elif self.save_type == "many":
            if os.path.exists(path):
                pass
            else:
                os.makedirs(path)

    def init_recorder(self, **kwargs):

        if self.recorder_type == "db":
            self.recorder = DBRecorder(**kwargs)
        elif self.recorder_type in ["csv", "xlsx", "json", 'txt']:
            self.recorder = Recorder(**kwargs)
        else:
            raise ValueError("recorder_type must be csv, xlsx, json, txt , sqlite")


class DBRecord:
    pass
