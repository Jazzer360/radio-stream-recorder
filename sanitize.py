from stream_recorder import sanitize_stream

station_folder = 'KRCL'
program_name = 'Little Bit Louder Now'
program_date = '2016-12-20'

if __name__ == '__main__':
    sanitize_stream(
        '{}/{}/{} {}.stream'.format(
            station_folder, program_name, program_name, program_date),
        'mp3',
        artist=station_folder + ' Radio',
        album_artist=station_folder + ' Radio',
        album=program_name)
