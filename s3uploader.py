from gevent import monkey; monkey.patch_all()
import gevent
import os
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from progressbar import * 
from uploader import Uploader

class S3Uploader(Uploader):
    def __init__(self, settings):
        self.key = settings['key']
        self.secret = settings['secret']
        self.bucket = settings['bucket']
        
        self.conn = S3Connection(self.key, self.secret)

    def upload_file(self, bucket, filename):
        try:
            k = Key(bucket)
            k.key = filename
            k.set_contents_from_filename(filename)
            k.set_acl('public-read')

            self.p.update(self.p.currval + 1)
        except:
            changes = open(self.changelist, 'a')
            changes.write(filename + '\n')
            changes.close()
            
    def upload_concurrent(self, bucket, changes):
        greenlets = []
        cwd = os.getcwd()
        from gevent.pool import Pool
        p = Pool(100)
        for i,line in enumerate(changes):
            filename = line.replace(cwd + '/', '').replace('\n','')

            greenlets.append(p.spawn(self.upload_file, bucket, filename))

        gevent.joinall(greenlets)
    
    def upload(self, changelist):
        self.changelist = changelist
        count = self.simplecount(self.changelist)

        if count == 0:
            return # No need to do anything

        self.p = ProgressBar(widgets=['Uploading Changes[', CounterWidget(),']: ', Percentage(), ' ', Bar(marker='#',left='[',right=']')], maxval=count)
        self.p.start()

        changes = open(self.changelist)

        bucket = self.conn.lookup(self.bucket)
        bucket.set_acl('public-read')

        t1 = time.time()
        while True:
            lines = changes.readlines(100000)
            if not lines:
                break
            for chunk in self.chunks(lines, 10000):
                self.upload_concurrent(bucket, chunk) 
        t2 = time.time()
        print '%s took %0.3f ms' % ('Concurrent upload', (t2-t1)*1000.0)

        self.p.finish()

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

