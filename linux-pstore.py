#!/usr/bin/python3
# arekm@maven.pl

import datetime
import os
import re
import socket
import shutil
import subprocess
import sys
import time

uptime = True
try:
    import psutil
except ModuleNotFoundError as e:
    uptime = False

pstoredir = '/sys/fs/pstore'
archivedir = '/var/log/pstore'

os.umask(0o077)

def mount_pstore():
    try:
        if not os.path.isfile('/bin/mount') or open('/proc/self/mounts', 'r').read().find('/sys/fs/pstore') >= 0:
            return
        subprocess.run(["/bin/mount", "none", "/sys/fs/pstore", "-t", "pstore", "-o", "nosuid,nodev,noexec"],
                       timeout=60, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print("%s: %s\nstdout=%s\nstderr=%s" % (sys.argv[0], e, e.stdout, e.stderr), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("%s: %s" % (sys.argv[0], e), file=sys.stderr)
        sys.exit(1)

tdate = datetime.datetime.now().strftime("%Y-%m-%d")
tdir = os.path.join(archivedir, tdate)

mount_pstore()

files = sorted(os.listdir(pstoredir))

if len(files) and not os.path.isdir(tdir):
    os.mkdir(tdir)

msg =  "Hostname:           %s\n" % socket.getfqdn()
if uptime:
    msg += "Uptime:             %s\n" % str(datetime.timedelta(seconds=time.time()-psutil.boot_time()))
msg += "Files in pstore:    %d\n" % len(files)

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
        msg += "(content compressed which usually means it is compressed with different\ncompressor than currently configured in kernel for pstore)\n\n"
        fdata = re.sub(r'[^\x20-\x7E\n\t\r]+', lambda m: '.' * len(m.group()), fdata)

    msg += fdata
    msg += "\n\n"

if len(files):
    print(msg)
