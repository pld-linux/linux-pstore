#!/usr/bin/python3
# arekm@maven.pl

import datetime
import os
import re
import shutil

pstoredir = '/sys/fs/pstore'
archivedir = '/var/log/pstore'

os.umask(0o077)

tdate = datetime.datetime.now().strftime("%Y-%m-%d")
tdir = os.path.join(archivedir, tdate)

files = sorted(os.listdir(pstoredir))

if len(files) and not os.path.isdir(tdir):
    os.mkdir(tdir)

msg = "Found %d files in pstore fs directory: \n\n" % len(files)

for file in files:
    fpath = os.path.join(pstoredir, file)
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(fpath))

    msg += "File: [%s], Last modified: [%s], Contents:\n\n" % (file, mtime.strftime("%Y-%m-%d %H:%M:%S"))

    mv = True
    fdata = ""
    try:
        fdata = open(fpath, "rt", errors='ignore').read()
    except Exception as e:
        msg += "(reading contents of [%s] failed: %s)\n\n" % (file, e)
        mv = False

    try:
        shutil.copy2(fpath, tdir)
    except Exception as e:
        msg += "(copying [%s] to [%s] dir failed: %s)\n\n" % (file, tdir, e)
        mv = False
    
    if mv:
        os.unlink(fpath)

    if file.endswith(".z"):
        msg += "(content compressed which usually means it is corrupted for pstore)\n\n"
        fdata = re.sub(r'[^\x20-\x7E\n\t\r]+', lambda m: '.' * len(m.group()), fdata)

    msg += fdata
    msg += "\n\n"

if len(files):
    print(msg)
