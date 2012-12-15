import json
from progressbar import * 
from mcdownloader import MCDownloader 
from s3uploader import S3Uploader
from subprocess import call

setting_file = open('config.json')
settings = json.load(setting_file)

mc = MCDownloader(settings['ftp'])
mc.download_map()
mc.unzip()

uploader = S3Uploader(settings['s3'])
#try:
    #retcode = call("python" + " overviewer.py --config=\"vokal_config.py\"", shell=True)
    #if retcode < 0:
        #print >>sys.stderr, "Child was terminated by signal", -retcode
    #elif retcode == 0:
        #uploader.upload()
    #else:
        #print >>sys.stderr, "Child returned", retcode
#except OSError as e:
    #print >>sys.stderr, "Execution failed:", e

#try:
    #retcode = call("python" + " overviewer.py --config=\"vokal_config.py\" --genpoi", shell=True)
    #if retcode < 0:
        #print >>sys.stderr, "Child was terminated by signal", -retcode
    #elif retcode == 0:
        #uploader.upload_static()
    #else:
        #print >>sys.stderr, "Child returned", retcode
#except OSError as e:
    #print >>sys.stderr, "Execution failed:", e

