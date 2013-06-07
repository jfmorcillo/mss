import os
import unittest

from mss.lib.xmlrpc import XmlRpc
from mss.agent.tests.utils import cleanup_tests, setup_modules, \
                                  run_agent, stop_agent, \
                                  run_tests

class TestModuleConfiguration(unittest.TestCase):

    def setUp(self):
        self.client = XmlRpc(port=8888)
        self.client.call('authenticate', 'root', 'mandriva')

    def test_get_config_module_unavailable(self):
        result = self.client.call('get_config', ['foo'])
        self.assertEqual(result, [])

    def test_get_valid_config(self):
        result = self.client.call('get_config', ['module1'])
        self.assertEqual(len(result[0]["config"]), 2)
        #[{'config': [{u'default': u'foo', 'slug': u'module1', u'type': u'text', u'name': u'option1', u'label': u'option one'},
        #             {'slug': u'module1', u'type': u'check', u'name': u'option2', u'label': u'option two'}],
        #  'slug': u'module1'}]
        # Fill the configuration
        config = {"module1_option1": "bar", "module1_option2": "on"}
        # Validate the configuration
        (config_err, config_result) = self.client.call('valid_config', ['module1'], config)
        self.assertFalse(config_err)
        module1_config = config_result[0]
        self.assertEqual(module1_config[0]["default"], "bar")
        self.assertEqual(module1_config[1]["default"], "on")

    def test_required_field(self):
        config = {"module2_option2": "foo"}
        # Validate the configuration
        (config_err, config_result) = self.client.call('valid_config', ['module2'], config)
        self.assertTrue(config_err)
        module2_config = config_result[0]
        self.assertIn("error", module2_config[0])
        self.assertNotIn("error", module2_config[1])


if __name__ == '__main__':
    modules = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config_modules')
    config = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent.ini')

    cleanup_tests()
    setup_modules(modules)
    process = run_agent(config)
    run_tests(TestModuleConfiguration, process)
    stop_agent(process)
    cleanup_tests()
