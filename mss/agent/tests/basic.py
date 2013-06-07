import os
import unittest

from mss.lib.xmlrpc import XmlRpc
from mss.agent.tests.utils import cleanup_tests, setup_modules, \
                                  run_agent, stop_agent, \
                                  run_tests

class TestBasics(unittest.TestCase):

    def setUp(self):
        self.client = XmlRpc(port=8888)
        result = self.client.call('authenticate', 'root', 'mandriva')

    def test_get_modules(self):
        result = self.client.call('get_modules')
        self.assertEqual(len(result), 4)

    def test_get_module_details(self):
        result = self.client.call('get_module_details', 'module1')
        self.assertEqual(result["configured"], False)
        self.assertEqual(result["name"], "Module One")

    def test_get_module_details_notexists(self):
        result = self.client.call('get_module_details', 'foo')
        self.assertEqual(result, False)

    def test_get_modules_details(self):
        result = self.client.call('get_modules_details', ['module1', 'module2'])
        self.assertEqual(len(result), 2)

    def test_get_modules_details_notexists2(self):
        result = self.client.call('get_modules_details', ['module1', 'foo'])
        self.assertEqual(len(result), 1)

    def test_get_modules_details_notexists1(self):
        result = self.client.call('get_modules_details', ['foo'])
        self.assertEqual(len(result), 0)

    def test_get_module_packages(self):
        result = self.client.call('get_packages', 'module1')
        self.assertEqual(result, ['package1', 'package2', 'package3', 'package4'])

    def test_get_module_packages_notexists(self):
        result = self.client.call('get_packages', 'foo')
        self.assertEqual(result, False)

    def test_get_module_packages_no_packages(self):
        result = self.client.call('get_packages', 'module2')
        self.assertEqual(result, [])

    def test_preinstall_modules(self):
        result = self.client.call('preinstall_modules', ['module1'])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["slug"], "module2")
        self.assertTrue(result[0]["dep"])
        self.assertEqual(result[1]["slug"], "module1")
        self.assertFalse(result[1]["dep"])

    def test_preinstall_modules_notexists1(self):
        result = self.client.call('preinstall_modules', ['module2', 'foo'])
        self.assertEqual(len(result), 1)

    def test_preinstall_modules_notexists2(self):
        result = self.client.call('preinstall_modules', ['foo'])
        self.assertEqual(len(result), 0)

    def test_get_repositories(self):
        result = self.client.call('get_repositories', ['module1', 'module2'])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["url"], "http://exemple.mandriva.com")

    def test_get_repositories_already_installed(self):
        result = self.client.call('get_repositories', ['module3'])
        self.assertEqual(len(result), 0)

    def test_get_sections(self):
        result = self.client.call('get_sections')
        self.assertEqual(result, [{'slug': 'test', 'name': 'Test'}])

    def test_get_section(self):
        result = self.client.call('get_section', 'test')
        self.assertEqual(len(result[0]["modules"]), 1)
        self.assertEqual(result[0]["modules"][0]["slug"], "module1")
        self.assertEqual(result[0]["slug"], "other")


if __name__ == '__main__':
    modules = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'basic_modules')
    config = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent.ini')

    cleanup_tests()
    setup_modules(modules)
    process = run_agent(config)
    run_tests(TestBasics, process)
    stop_agent(process)
    cleanup_tests()
