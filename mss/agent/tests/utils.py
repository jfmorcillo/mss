import os
import shutil

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
