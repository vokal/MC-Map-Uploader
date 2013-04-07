import StringIO
import os
import shutil
import tempfile
import time
from gslib.third_party.oauth2_plugin import oauth2_plugin

import boto
from progressbar import * 
from uploader import Uploader

GOOGLE_STORAGE = 'gs'

class GSUploader(Uploader):
    def __init__(self, settings):
        self.bucket = settings['bucket']

    def upload_file(self, filenames):
        for filename in filenames:
            contents = file(filename.replace('\n',''), 'r')

            dst_uri = boto.storage_uri(
                    self.bucket + '/' + filename, GOOGLE_STORAGE)

            dst_uri.new_key().set_contents_from_file(contents)
            contents.close()

            self.p.update(self.p.currval + 1)

    def upload(self, changelist):
        self.changelist = changelist
        count = self.simplecount(self.changelist)

        if count == 0:
            return # No need to do anything

        self.p = ProgressBar(widgets=['Uploading Changes[', CounterWidget(),']: ', Percentage(), ' ', Bar(marker='#',left='[',right=']')], maxval=count)
        self.p.start()

        changes = open(self.changelist)

        t1 = time.time()
        while True:
            lines = changes.readlines(100000)
            if not lines:
                break
            for chunk in self.chunks(lines, 10000):
                self.upload_file(chunk) 
        t2 = time.time()
        print '%s took %0.3f ms' % ('Concurrent upload', (t2-t1)*1000.0)

        self.p.finish()

    def upload_static(self, outfolder):
        print 'Static!'
        pass
