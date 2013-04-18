
import os
import unittest

from mss.lib.xmlrpc import XmlRpc
from mss.agent.tests.utils import cleanup_tests, setup_modules, \
                                  run_agent, stop_agent, \
                                  run_tests

class TestConfigValidation(unittest.TestCase):

    def setUp(self):
        self.client = XmlRpc(port=8888)
        err, result = self.client.call('authenticate', 'root', 'mandriva')

    def test_fqdn_validation(self):
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_fqdn": "foo"})
        self.assertFalse(err)
        self.assertTrue(config_err)
        module1_config = config_result[0]
        self.assertIn("error", module1_config[0])
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_fqdn": "foo.a"})
        self.assertFalse(err)
        self.assertTrue(config_err)
        module1_config = config_result[0]
        self.assertIn("error", module1_config[0])
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_fqdn": "foo.local"})
        self.assertFalse(err)
        self.assertFalse(config_err)
        module1_config = config_result[0]
        self.assertNotIn("error", module1_config[0])

    def test_network_validation(self):
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_network_text": "foo"})
        self.assertFalse(err)
        self.assertTrue(config_err)
        module1_config = config_result[0]
        self.assertIn("error", module1_config[1])
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_network_text": [("192.168.0.0", "255.255.255.0")]})
        self.assertFalse(err)
        self.assertFalse(config_err)
        module1_config = config_result[0]
        self.assertNotIn("error", module1_config[1])
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_network_0_ip": "foo"})
        self.assertFalse(err)
        self.assertTrue(config_err)
        module1_config = config_result[0]
        self.assertIn("error", module1_config[2])
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_network_0_ip": "192.168.0.45"})
        self.assertFalse(err)
        self.assertTrue(config_err)
        module1_config = config_result[0]
        self.assertIn("error", module1_config[2])
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_network_0_ip": "340.45.30", "module1_network_0_mask": "255.0.0.0"})
        self.assertFalse(err)
        self.assertTrue(config_err)
        module1_config = config_result[0]
        self.assertIn("error", module1_config[2])
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_network_0_mask": "255.0.0.0"})
        self.assertFalse(err)
        self.assertTrue(config_err)
        module1_config = config_result[0]
        self.assertIn("error", module1_config[2])
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_network_0_mask": "400.500.0.0"})
        self.assertFalse(err)
        self.assertTrue(config_err)
        module1_config = config_result[0]
        self.assertIn("error", module1_config[2])
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_network_0_ip": "192.168.0.0", "module1_network_0_mask": "255.255.255.0"})
        self.assertFalse(err)
        self.assertFalse(config_err)
        module1_config = config_result[0]
        self.assertNotIn("error", module1_config[2])

    def test_ip_validation(self):
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_ip": "foo"})
        self.assertFalse(err)
        self.assertTrue(config_err)
        module1_config = config_result[0]
        self.assertIn("error", module1_config[3])
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_ip": "300.400.0.0"})
        self.assertFalse(err)
        self.assertTrue(config_err)
        module1_config = config_result[0]
        self.assertIn("error", module1_config[3])
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_ip": "192.168.30.34"})
        self.assertFalse(err)
        self.assertFalse(config_err)
        module1_config = config_result[0]
        self.assertNotIn("error", module1_config[3])

    def test_custom_validation(self):
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_custom": "bar"})
        self.assertFalse(err)
        self.assertTrue(config_err)
        module1_config = config_result[0]
        self.assertEqual(module1_config[4]["error"], "Value is not foo")
        err, (config_err, config_result) = self.client.call('valid_config', ['module1'], {"module1_custom": "foo"})
        self.assertFalse(err)
        self.assertFalse(config_err)
        module1_config = config_result[0]
        self.assertNotIn("error", module1_config[4])


if __name__ == '__main__':
    modules = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'validation_modules')
    config = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent.ini')

    cleanup_tests()
    setup_modules(modules)
    process = run_agent(config)
    run_tests(TestConfigValidation, process)
    stop_agent(process)
    cleanup_tests()
