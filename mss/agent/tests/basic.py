import unittest
from mss.lib.xmlrpc import XmlRpc

class TestBasics(unittest.TestCase):

    def setUp(self):
        self.client = XmlRpc()
        err, result = self.client.call('load')

    def test_get_modules(self):
        err, result = self.client.call('get_modules')
        self.assertFalse(err)
        self.assertEqual(len(result), 4)

    def test_get_module_details(self):
        err, result = self.client.call('get_module_details', 'module1')
        self.assertFalse(err)
        self.assertEqual(result["configured"], False)
        self.assertEqual(result["name"], "Module One")

    def test_get_module_details_notexists(self):
        err, result = self.client.call('get_module_details', 'foo')
        self.assertFalse(err)
        self.assertEqual(result, False)

    def test_get_modules_details(self):
        err, result = self.client.call('get_modules_details', ['module1', 'module2'])
        self.assertFalse(err)
        self.assertEqual(len(result), 2)

    def test_get_modules_details_notexists2(self):
        err, result = self.client.call('get_modules_details', ['module1', 'foo'])
        self.assertFalse(err)
        self.assertEqual(len(result), 1)

    def test_get_modules_details_notexists1(self):
        err, result = self.client.call('get_modules_details', ['foo'])
        self.assertFalse(err)
        self.assertEqual(len(result), 0)

    def test_get_module_packages(self):
        err, result = self.client.call('get_packages', 'module1')
        self.assertFalse(err)
        self.assertEqual(result, ['package1', 'package2', 'package3', 'package4'])

    def test_get_module_packages_notexists(self):
        err, result = self.client.call('get_packages', 'foo')
        self.assertEqual(err, False)
        self.assertFalse(err)
        self.assertEqual(result, False)

    def test_get_module_packages_no_packages(self):
        err, result = self.client.call('get_packages', 'module2')
        self.assertFalse(err)
        self.assertEqual(result, [])

    def test_preinstall_modules(self):
        err, result = self.client.call('preinstall_modules', ['module1'])
        self.assertFalse(err)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["slug"], "module2")
        self.assertTrue(result[0]["dep"])
        self.assertEqual(result[1]["slug"], "module1")
        self.assertFalse(result[1]["dep"])

    def test_preinstall_modules_notexists1(self):
        err, result = self.client.call('preinstall_modules', ['module2', 'foo'])
        self.assertFalse(err)
        self.assertEqual(len(result), 1)

    def test_preinstall_modules_notexists2(self):
        err, result = self.client.call('preinstall_modules', ['foo'])
        self.assertFalse(err)
        self.assertEqual(len(result), 0)

    def test_get_repositories(self):
        err, result = self.client.call('get_repositories', ['module1', 'module2'])
        self.assertFalse(err)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["url"], "http://exemple.mandriva.com")

    def test_get_repositories_already_installed(self):
        err, result = self.client.call('get_repositories', ['module3'])
        self.assertFalse(err)
        self.assertEqual(len(result), 0)

    def test_get_sections(self):
        err, result = self.client.call('get_sections')
        self.assertFalse(err)
        self.assertEqual(result, [{'slug': 'test', 'name': 'Test'}])

    def test_get_section(self):
        err, result = self.client.call('get_section', 'test')
        self.assertFalse(err)
        self.assertEqual(len(result[0]["modules"]), 1)
        self.assertEqual(result[0]["modules"][0]["slug"], "module1")
        self.assertEqual(result[0]["slug"], "other")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasics)
    unittest.TextTestRunner(verbosity=2).run(suite)
