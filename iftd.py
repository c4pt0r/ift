#!/usr/bin/env python
import os, sys
import time
import toml

from daemon import Daemon
from distutils.dir_util import mkpath

RESOURCE_PATH = '/var/ift'

def load_profiles():
    profiles_dir = os.path.join(RESOURCE_PATH, 'profiles')
    mkpath(profiles_dir)
    profiles = []
    for fn in os.listdir(profiles_dir):
        if not profile_fn.endswith('.toml'):
            continue
        profile_fn = os.path.join(profiles_dir, fn)
        with open(profile_fn) as fp:
            config = toml.loads(fp.read())
            print profile_fn, config
            profiles.append(config)
    return profiles

def main_loop():
    load_profiles()
    while True:
        time.sleep(1)

def daemon():
    class _daemon(Daemon):
        def run(self): main_loop()

    daemon = _daemon('/tmp/ift.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
    
if __name__ == '__main__':
    #run_as_daemon()
    main_loop()
