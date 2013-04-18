import os
import unittest
from subprocess import Popen
import time

from mss.lib.xmlrpc import XmlRpc
from mss.agent.tests.utils import cleanup_tests, setup_modules

class TestModuleConfiguration(unittest.TestCase):

    def setUp(self):
        self.client = XmlRpc(port=8888)
        err, result = self.client.call('load')

    def test_get_config_module_unavailable(self):
        err, result = self.client.call('get_config', ['foo'])
        self.assertEqual(result, [])

    def test_get_valid_config(self):
        err, result = self.client.call('get_config', ['module1'])
        self.assertFalse(err)
        self.assertEqual(len(result[0]["config"]), 2)
        #[{'config': [{u'default': u'foo', 'slug': u'module1', u'type': u'text', u'name': u'option1', u'label': u'option one'},
        #             {'slug': u'module1', u'type': u'check', u'name': u'option2', u'label': u'option two'}],
        #  'slug': u'module1'}]
        # Fill the configuration
        config = {"module1_option1": "bar", "module1_option2": "on"}
        # Validate the configuration
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], config)
        self.assertFalse(err)
        self.assertFalse(config_err)
        module1_config = config_result[0]
        self.assertEqual(module1_config[0]["default"], "bar")
        self.assertEqual(module1_config[1]["default"], "on")

    def test_required_field(self):
        config = {"module2_option2": "foo"}
        # Validate the configuration
        err, (config_err, config_result) = self.client.call('valid_config', ['module2'], config)
        self.assertFalse(err)
        self.assertTrue(config_err)
        module2_config = config_result[0]
        self.assertIn("error", module2_config[0])
        self.assertNotIn("error", module2_config[1])


if __name__ == '__main__':
    modules = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config_modules')
    config = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent.ini')

    cleanup_tests()
    setup_modules(modules)

    print "### RUNNING MSS-AGENT"
    process = Popen(['/usr/sbin/mss-agent', '-d', '--config', config])
    time.sleep(2)

    print "### RUNNING TESTS"
    suite = unittest.TestLoader().loadTestsFromTestCase(TestModuleConfiguration)
    unittest.TextTestRunner(verbosity=2).run(suite)

    print "### STOPPING MSS-AGENT"
    process.terminate()

    cleanup_tests()
