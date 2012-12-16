import zipfile
from ftplib import FTP
from progressbar import * 

class MCDownloader:
    widgets =['Download: ', Percentage(), ' ',
                   Bar(marker='#',left='[',right=']'),
                   ' ', ETA(), ' ', FileTransferSpeed()] 
    downloaded = 0
    user = None
    password = None
    filename = 'world.zip'

    def __init__(self, settings):
        if 'user' in settings:
            self.user = settings['user']
        if 'pass' in settings:
            self.password = settings['pass']

        if 'filename' in settings:
            self.filename = settings['filename']

        self.server = settings['server']
        self.port = settings['port']

    def write_file(self, block):
        self.f.write(block)
        self.downloaded = self.downloaded + len(block)
        self.p.update(self.downloaded)

    def download_map(self):
        print 'Downloading file from server'
        ftp = FTP()
        ftp.connect(self.server, self.port)
        ftp.login(self.user, self.password)

        self.f = open('world.zip', 'wb')
        ## TODO check to see if hash's are different?
        ftp.sendcmd("TYPE i")    # Switch to Binary mode
        size = int(ftp.size(self.filename))

        print 'Size of %s: %s MBs' % (self.filename, size / (1024*1024))
        self.p = ProgressBar(widgets=self.widgets, maxval=size)
        self.p.start()
        ftp.retrbinary('RETR %s' % self.filename, self.write_file) 
        self.p.finish()

        ftp.quit()

        self.f.close();
        print ""

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
