import json
from progressbar import * 
from mcdownloader import MCDownloader 
from s3uploader import S3Uploader
from gsuploader import GSUploader
from subprocess import call

def load_overviewer_settings(settings):
    location = settings['overviewer']['location']
    parser = location + 'configParser.py'

def run_overviewer_gen(settings):
    generate = 'skip_generate' not in settings or settings['skip_generate'] == False
    retcode = 0
    try:
        if generate:
            ovset = settings['overviewer']
            cmd = "python %s --config=\"%s\"" % (ovset['location'] + 'overviewer.py', ovset['config'])
            retcode = call(cmd, shell=True)
            return retcode == 0
    except OSError as e:
        print >>sys.stderr, "Execution failed:", e

    return False

def run_overviewer_poi(settings):
    poi = 'skip_poi' not in settings or settings['skip_poi'] == False
    retcode = 0

    if not poi:
        return

    try:
        ovset = settings['overviewer']
        cmd = "python %s --config=\"%s\" --genpoi" % (ovset['location'] + 'overviewer.py', ovset['config'])
        retcode = call(cmd, shell=True)
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal", -retcode
    except OSError as e:
        print >>sys.stderr, "Execution failed:", e


setting_file = open('config.json')
settings = json.load(setting_file)

if 'skip_ftp' not in settings or settings['skip_ftp'] == False:
    mc = MCDownloader(settings['ftp'])
    mc.download_map()
    mc.unzip()

ovset = settings['overviewer']

if 's3' in settings.keys() and settings['skip_s3'] is not False:
    uploader = S3Uploader(settings['s3'])
elif 'gs' in settings.keys() and settings['skip_s3'] is not False:
    uploader = GSUploader(settings['gs'])

if uploader:
    if settings['skip_generate'] is False:
        run_overviewer_gen(settings) 
        run_overviewer_poi(settings)

    uploader.upload(ovset['changelist'])
    uploader.upload_static(ovset['outdir'])

