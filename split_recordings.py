import subprocess
import os

DT = 'KRCL/Drive Time/Drive Time {date}.mp3'
LBLN = 'KRCL/Little Bit Louder Now/Little Bit Louder Now {date}.mp3'


def track_meta(show, date):
    return {
        'title': '{} {}'.format(show, date),
        'artist': 'KRCL Radio',
        'album_artist': 'KRCL Radio',
        'album': show
    }


def mix_audio(segments, output, metadata=None):
    with open('concat.txt', 'w+') as filelist:
        for index, segment in enumerate(segments):
            cmd = 'ffmpeg -y '
            start, dur, filename = segment
            if start:
                cmd += '-ss {} '.format(start)
            if dur:
                cmd += '-t {} '.format(dur)
            cmd += '-i "{}" '.format(filename)
            cmd += '-c copy {}.mp3'.format(index)
            subprocess.call(cmd)
            filelist.write('file {}.mp3\n'.format(index))
    cmd = 'ffmpeg -y -f concat -i concat.txt '
    if metadata:
        cmd += '-id3v2_version 3 -write_id3v1 1 '
        for key, val in metadata.items():
            cmd += '-metadata "{}={}" '.format(key, val)
    cmd += '-c copy "{}"'.format(output)
    subprocess.call(cmd)
    with open('concat.txt') as filelist:
        for line in filelist.readlines():
            if line:
                os.remove(line[5:-1])
    os.remove('concat.txt')


##### Fixed the Drive Time and LBLN for 1-18 to 1-23 of 2016 #####
# dates = ['2016-01-{}'.format(n) for n in range(18, 23)]

# for date in dates:
#     segments = [
#         ('2:00:00', None, DT.format(date=date)),
#         (None, '1:00:00', LBLN.format(date=date))
#     ]
#     mix_audio(segments,
#               'Little Bit Louder Now {}.mp3'.format(date),
#               track_meta('Little Bit Louder Now', date))
#     mix_audio([(None, '2:00:00', DT.format(date=date))],
#               'Drive Time {}.mp3'.format(date),
#               track_meta('Drive Time', date))

date = '2016-09-07'
segments = [
    (None, '0:11:11', LBLN.format(date=date)),
    ('0:27:58', '0:29:21', LBLN.format(date=date)),
    ('1:17:23', None, LBLN.format(date=date))
]
mix_audio(segments,
          'Little Bit Louder Now {}.mp3'.format(date),
          track_meta('Little Bit Louder Now', date))