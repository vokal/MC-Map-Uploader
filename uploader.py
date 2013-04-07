class Uploader(object):
    static_files = [
        'activity.js',
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

    def simplecount(self, filename):
        lines = 0
        for line in open(filename):
            lines += 1
        return lines
        
    def chunks(self, l, n):
        return [l[i:i+n] for i in range(0, len(l), n)]
