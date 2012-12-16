import json
from progressbar import * 
from mcdownloader import MCDownloader 
from s3uploader import S3Uploader
from subprocess import call

def load_overviewer_settings(settings):

    location = settings['overviewer']['location']

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

upload = 'skip_s3' not in settings or settings['skip_s3'] == False

uploader = S3Uploader(settings['s3'])
if run_overviewer_gen(settings) and upload:
    uploader.upload('changes.log')

run_overviewer_poi(settings)
if upload:
    uploader.upload_static('VOKAL_test')



