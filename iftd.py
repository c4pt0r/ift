#!/usr/bin/env python
"""ift daemon

if ... then ... else ...

Usage:
    iftd start [--log=<logfile>] [--pid=<pidfile>] [--foreground]
    iftd restart [--log=<logfile>] [--pid=<pidfile>]
    iftd stop

Options:
    --log=<logfile>   log file [default: /tmp/iftd.log]
    --pid=<pidfile>   pid file [default: /tmp/iftd.pid]
"""
import os, sys
import time
import toml
import logging
import gevent

from daemon import Daemon
from distutils.dir_util import mkpath
from docopt import docopt

logging.basicConfig(level=logging.INFO,
    format='[%(asctime)s] [%(filename)s:%(lineno)d] [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

RESOURCE_PATH = '/var/ift'

class Profile:
    def __init__(self, conf):
        self._conf = conf
        self._name = conf['profile']

    def exec_if(self):
        pass

    def exec_then(self):
        pass

    def exec_else(self):
        pass

    def loop(self):
        while True:
            logger.info("checking %s ..." % self._name)
            if self.exec_if():
                logger.info("checking ok, running then-script %s ..." % 
                        self._name)
                self.exec_then()
            else:
                logger.info("checking fail, running else-script %s ..." % 
                        self._name)
                self.exec_else()
            gevent.sleep(5)

def load_profiles():
    profiles_dir = os.path.join(RESOURCE_PATH, 'profiles')
    mkpath(profiles_dir)
    profiles = []
    for fn in os.listdir(profiles_dir):
        if not fn.endswith('.toml'):
            continue
        profile_fn = os.path.join(profiles_dir, fn)
        with open(profile_fn) as fp:
            config = toml.loads(fp.read())
            profiles.append(config)
    return profiles

def main_loop():
    logger.info("start main loop")
    profile_confs = load_profiles()
    profiles = []
    for p in profile_confs:
        profile = Profile(p)
        profiles.append(gevent.spawn(profile.loop))

    gevent.joinall(profiles)

def daemon(action, pidfile, logfile):
    class _daemon(Daemon):
        def run(self): main_loop()

    daemon = _daemon(pidfile, stdout=logfile, stderr=logfile)
    if action == 'start':
        daemon.start()
    elif action == 'stop':
        daemon.stop()
    elif action == 'restart':
        daemon.restart()
    
if __name__ == '__main__':
    
    arguments = docopt(__doc__, version='ift 0.1')
    if arguments['--foreground']:
        main_loop()
    else:
        if arguments['start']:
            daemon('start', arguments['--pid'], arguments['--log'])
        elif arguments['stop']:
            daemon('stop', arguments['--pid'], arguments['--log'])
        elif arguments['restart']:
            daemon('restart', arguments['--pid'], arguments['--log'])
