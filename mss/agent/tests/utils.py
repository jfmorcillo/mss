import os
import shutil
from subprocess import Popen
import time
import unittest

modules_dir = "/tmp/mss_modules/"
log_file = "/tmp/mss-agent.log"
db_file = "/tmp/mss-agent.db"

def cleanup_tests():
    # Cleanup before running the tests
    if os.path.isdir(modules_dir):
        shutil.rmtree(modules_dir)
    if os.path.exists(log_file):
        os.unlink(log_file)
    if os.path.exists(db_file):
        os.unlink(db_file)

def setup_modules(src_dir):
    # Setup modules dir for tests
    if os.path.isdir(modules_dir):
        shutil.rmtree(modules_dir)
    shutil.copytree(src_dir, modules_dir)

def run_agent(config):
    print "### RUNNING MSS-AGENT"
    process = Popen(['/usr/sbin/mss-agent', '-d', '--config', config])
    time.sleep(2)
    return process

def stop_agent(process):
    print "### STOPPING MSS-AGENT"
    process.terminate()

def run_tests(test_case, process):
    print "### RUNNING TESTS"
    try:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
        unittest.TextTestRunner(verbosity=2).run(suite)
    except KeyboardInterrupt:
        process.terminate()
