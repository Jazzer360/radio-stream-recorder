from datetime import datetime, time, timedelta
from importlib import import_module
from time import sleep
import argparse
import logging
import os
import requests
import socket
import subprocess
import threading
import wx
import wx_console
import yaml


class Config(object):
    def __init__(self, filename):
        with open(filename) as fin:
            cfg = yaml.load(fin.read())
        stream_module, stream_func = cfg['stream_generator'].rsplit('.', 1)
        self.stream = getattr(import_module(stream_module), stream_func)
        self.stream_type = cfg['stream_type']
        self.stream_name = cfg['stream_name']
        self.programs = []
        for program in cfg['programs']:
            self.programs.append(
                Program(stream_name=self.stream_name, **program))


class Program(object):
    DAYMAP = {'M': 0, 'T': 1, 'W': 2, 'Th': 3, 'F': 4, 'S': 5, 'Su': 6}

    def __init__(self, **kwargs):
        self.stream_name = kwargs['stream_name']
        self.name = kwargs['name']
        self.start = time(hour=kwargs['start'] // 60,
                          minute=kwargs['start'] % 60)
        self.duration = timedelta(hours=kwargs['duration'] // 60,
                                  minutes=kwargs['duration'] % 60)
        self.days = map(lambda x: self.DAYMAP[x], kwargs['days'].split(' '))
        self.genre = kwargs.get('genre')

    def latest_air_segment(self):
        now = datetime.now()
        day = now.date()
        while True:
            if day.weekday() in self.days:
                start = datetime.combine(day, self.start)
                if start <= now:
                    return start, start + self.duration
            day -= timedelta(days=1)

    @property
    def metadata(self):
        metadata = {
            'artist': self.stream_name,
            'album_artist': self.stream_name,
            'album': self.name}
        if self.genre:
            metadata['genre'] = self.genre
        return metadata


class RecordingThread(threading.Thread):
    def __init__(self, config, log):
        super(RecordingThread, self).__init__()
        self.config = config
        self.log = log
        self._stop = threading.Event()

    def record(self, program):
        start, end = program.latest_air_segment()
        file_path = (program.stream_name + '\\' +
                     program.name + '\\' +
                     program.name + ' %Y-%m-%d.stream')
        file_path = start.strftime(file_path)
        make_folder(program.stream_name + '\\' + program.name)
        with open(file_path, 'ab') as f:
            for block in self.config.stream():
                f.write(block)
                if datetime.now() >= end or self.stopped():
                    return file_path

    def current_program(self):
        now = datetime.now()
        for program in self.config.programs:
            start, end = program.latest_air_segment()
            if now >= start and now < end:
                return program
        return None

    def run(self):
        self.log.info('%s recording started', self.config.stream_name)
        while True:
            if self.stopped():
                return
            program = self.current_program()
            if not program:
                sleep(5)
                continue
            try:
                self.log.info('Starting to record %s', program.name)
                filename = self.record(program)
                self.log.info('%s has finished', program.name)
                if not self.stopped():
                    sanitize_stream(filename, self.config.stream_type,
                                    **program.metadata)
            except (requests.exceptions.Timeout, socket.timeout) as e:
                self.log.error('Connection to host timed out', exc_info=e)
                sleep(5)
            except requests.exceptions.ConnectionError as e:
                self.log.error('Unable to connect to host', exc_info=e)
                sleep(5)
            except socket.error as e:
                self.log.error('Connection was lost unexpectedly', exc_info=e)
                sleep(5)
            finally:
                self.log.info('Recording of %s stopped', program.name)

    def stopped(self):
        return self._stop.isSet()

    def stop(self):
        self._stop.set()


def make_folder(name):
    path = '{}/{}'.format(os.getcwd(), name)
    if not os.path.exists(path):
        os.makedirs(path)


def reencode_thread(infile, intype, **metadata):
    outfile = '{}.mp3'.format(infile.rsplit('.', 1)[0])
    if 'title' not in metadata:
        metadata['title'] = os.path.split(infile)[1].rsplit('.', 1)[0]
    command = ['ffmpeg', '-f', intype, '-i', infile,
               '-id3v2_version', '3', '-write_id3v1', '1']
    for key, value in metadata.iteritems():
        command += ['-metadata', '{}={}'.format(key, value)]
    command.append(outfile)
    log.info('Sending %s to ffmpeg', infile)
    subprocess.check_call(command)
    log.info('%s cleaned', outfile)
    if os.path.exists(outfile):
        os.remove(infile)


def sanitize_stream(stream, stream_type, **metadata):
    threading.Thread(target=reencode_thread,
                     args=(stream, stream_type),
                     kwargs=metadata).start()


if __name__ == '__main__':
    # Build config from args
    parser = argparse.ArgumentParser(
        description='Record streamed radio programs')
    parser.add_argument('config', help='Configuration file')
    args = parser.parse_args()
    config = Config(args.config)

    # Setup wx log frame
    app = wx.App(False)
    title = '{} Recording'.format(config.stream_name)
    wxlog = wx_console.LoggingFrame(None, title=title, icon='record.png')

    # Setup logger
    log = logging.getLogger('Stream recorder')
    log.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    fh = logging.FileHandler(args.config.rsplit('.', 1)[0] + '.log')
    fh.setFormatter(formatter)
    log.addHandler(fh)
    wxlog.handler.setFormatter(formatter)
    log.addHandler(wxlog.handler)

    # Start recording thread
    recording_thread = RecordingThread(config, log)
    recording_thread.start()

    app.MainLoop()
    recording_thread.stop()
