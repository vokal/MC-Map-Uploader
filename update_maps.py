# coding=utf-8

import zipfile
import os
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from ftplib import FTP
from overviewer_core.progressbar import * 
from subprocess import call

class MCDownloader:
    widgets =['Download: ', Percentage(), ' ',
                   Bar(marker='#',left='[',right=']'),
                   ' ', ETA(), ' ', FileTransferSpeed()] 
    downloaded = 0

    def write_file(self, block):
        self.f.write(block)
        self.downloaded = self.downloaded + len(block)
        self.p.update(self.downloaded)

    def download_map(self):
        self.f = open('world.zip', 'wb')

        ftp = FTP()
        ftp.connect('##############################','####')
        ftp.login('##################', '#######')

        ## TODO check to see if hash's are different?
        ftp.sendcmd("TYPE i")    # Switch to Binary mode
        size = int(ftp.size('world.zip'))

        print 'Downloading file from server'
        print 'Size of world.zip: %s MBs' % (size / (1024*1024))
        self.p = ProgressBar(widgets=self.widgets, maxval=size)
        self.p.start()
        ftp.retrbinary('RETR world.zip', self.write_file) 
        self.p.finish()

        ftp.quit()

        self.f.close();

    def unzip(self):
        zf = zipfile.ZipFile(r'world.zip')

        uncompress_size = sum((file.file_size for file in zf.infolist()))

        self.p = ProgressBar(widgets=['Unzipping: ', Percentage(), ' ', Bar(marker='#',left='[',right=']'), ' ', ETA()], maxval=uncompress_size)
        self.p.start()

        extracted_size = 0
        for file in zf.infolist():
            extracted_size += file.file_size
            self.p.update(extracted_size)
            zf.extract(file)

        self.p.finish()

class S3Uploader:

    file_prefix = 'VOKAL'
    static_files = [
        'backbone.js',
        'baseMarkers.js',
        'bed.png',
        'compass_lower-left.png',
        'compass_lower-right.png',
        'compass_upper-left.png',
        'compass_upper-right.png',
        'control-bg-active.png',
        'control-bg.png',
        'index.html',
        'markers.js',
        'markersDB.js',
        'index.html',
        'overviewer.css',
        'overviewer.js',
        'overviewerConfig.js',
        'regions.js',
        'signpost_icon.png',
        'signpost-shadow.png',
        'signpost.png',
        'underscore.js']

    conn = S3Connection('####################', '########################################')

    def simplecount(self, filename):
        lines = 0
        for line in open(filename):
            lines += 1
        return lines
    
    def upload(self):
        count = self.simplecount('changes.log')

        p = ProgressBar(widgets=['Uploading Changes: ', Percentage(), ' ', Bar(marker='#',left='[',right=']')], maxval=count)
        p.start()

        changes = open('changes.log')
        cwd = os.getcwd()

        bucket = self.conn.lookup('vokal-minecraft')
        bucket.set_acl('public-read')
        k = Key(bucket)

        for i, line in enumerate(changes):
            filename = line.replace(cwd + '/', '').replace('\n','')
            k.key = filename
            k.set_contents_from_filename(filename)
            k.set_acl('public-read')
            p.update(i)

        p.finish()

    def upload_static(self):
        count = len(self.static_files)

        p = ProgressBar(widgets=['Uploading Static: ', Percentage(), ' ', Bar(marker='#',left='[',right=']')], maxval=count)
        p.start()

        cwd = os.getcwd()

        bucket = self.conn.lookup('vokal-minecraft')
        bucket.set_acl('public-read')
        k = Key(bucket)

        for i, line in enumerate(self.static_files):
            filename= self.file_prefix + '/' + line
            k.key = filename
            k.set_contents_from_filename(filename)
            k.set_acl('public-read')
            p.update(i)

        p.finish()

mc = MCDownloader()
mc.download_map()
mc.unzip()

uploader = S3Uploader()
try:
    retcode = call("python" + " overviewer.py --config=\"vokal_config.py\"", shell=True)
    if retcode < 0:
        print >>sys.stderr, "Child was terminated by signal", -retcode
    elif retcode == 0:
        uploader.upload()
    else:
        print >>sys.stderr, "Child returned", retcode
except OSError as e:
    print >>sys.stderr, "Execution failed:", e

try:
    retcode = call("python" + " overviewer.py --config=\"vokal_config.py\" --genpoi", shell=True)
    if retcode < 0:
        print >>sys.stderr, "Child was terminated by signal", -retcode
    elif retcode == 0:
        uploader.upload_static()
    else:
        print >>sys.stderr, "Child returned", retcode
except OSError as e:
    print >>sys.stderr, "Execution failed:", e

