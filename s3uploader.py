import os
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from progressbar import * 

class S3Uploader:
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

    def __init__(self, settings):
        self.key = settings['key']
        self.secret = settings['secret']
        self.bucket = settings['bucket']
        
        self.conn = S3Connection(self.key, self.secret)

    def simplecount(self, filename):
        lines = 0
        for line in open(filename):
            lines += 1
        return lines
    
    def upload(self, changes):
        count = self.simplecount(changes)

        if count == 0:
            return # No need to do anything

        p = ProgressBar(widgets=['Uploading Changes[', CounterWidget(),']: ', Percentage(), ' ', Bar(marker='#',left='[',right=']')], maxval=count)
        p.start()

        changes = open(changes)
        cwd = os.getcwd()

        bucket = self.conn.lookup(self.bucket)
        bucket.set_acl('public-read')
        k = Key(bucket)

        for i, line in enumerate(changes):
            filename = line.replace(cwd + '/', '').replace('\n','')
            k.key = filename
            k.set_contents_from_filename(filename)
            k.set_acl('public-read')
            p.update(i)

        p.finish()

    def upload_static(self, outfolder):
        count = len(self.static_files)

        p = ProgressBar(widgets=['Uploading Static: ', Percentage(), ' ', Bar(marker='#',left='[',right=']')], maxval=count)
        p.start()

        cwd = os.getcwd()

        bucket = self.conn.lookup(self.bucket)
        bucket.set_acl('public-read')
        k = Key(bucket)

        for i, line in enumerate(self.static_files):
            filename= outfolder + '/' + line
            k.key = filename
            k.set_contents_from_filename(filename)
            k.set_acl('public-read')
            p.update(i)

        p.finish()

