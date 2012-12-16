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
