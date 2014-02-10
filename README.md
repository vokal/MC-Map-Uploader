MC-Map-Uploader
===============

Python Script to connect Minecraft Overviewer renders to an Amazon S3 instance

Usage
=====

Create a `config.json` in the current folder

Example
````
{
    "ftp": {
        "user": "USERNAME",
        "pass": "PASSWORD",
        "server": "ftp.test.com",
        "port": 21
    },
    "s3": {
        "key": "s3keygoeshere",
        "secret": "thisiswhereyours3secretgoes",
        "bucket": "minecraft-map"
    },
    "overviewer": {
        "location": "/Users/user/Projects/Minecraft-Overviewer/",
        "config": "/Users/user/Projects/Minecraft-Overviewer/vokal_config.py",
        "outdir": "map",
        "changelist": "change.log"
    },
    "skip_ftp": false,
    "skip_generate": false,
    "skip_s3": false,
    "skip_poi": false
}
````

Example Output
````
wmbest2@MacBook-Air.local in ~/Projects/MC-Map-Uploader [master*]
$ ./MC-Map-Uploader
Downloading file from server
Size of world.zip: 403 MBs
Download: 100% [##################################] Time: 00h 04m 08s   1.70 M/s

Unzipping: 100% [############################################] Time: 00h 00m 05s
2012-12-15 21:05:27  Welcome to Minecraft Overviewer!
2012-12-15 21:05:33  Rendering 832 total tiles.
 97% [==========================================  ] 813 74.07t/s eta 00h 00m 00s
2012-12-15 21:05:44  Rendering complete!
Uploading Changes[832]: 100% [######################################################]
2012-12-15 21:09:33  Looking for entities in <RegionSet regiondir='/Users/wmbest2/Projects/MC-Map-Uploader/world/DIM1/region'>
2012-12-15 21:09:33  Done.
2012-12-15 21:09:34  Done scanning regions
2012-12-15 21:09:34  Writing out javascript files
2012-12-15 21:09:34  Done
Uploading Static: 100% [#######################################################]
````
