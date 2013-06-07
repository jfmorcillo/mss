
import os
import unittest

from mss.lib.xmlrpc import XmlRpc
from mss.agent.tests.utils import cleanup_tests, setup_modules, \
                                  run_agent, stop_agent, \
                                  run_tests

class TestConfigValidation(unittest.TestCase):

    def setUp(self):
        self.client = XmlRpc(port=8888)
        self.client.call('authenticate', 'root', 'mandriva')

    def test_fqdn_validation(self):
        config_result = self.client.call('valid_config', ['module1'], {"module1_fqdn": "foo"})
        self.assertTrue(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertIn("error", module1_config[0])
        config_result = self.client.call('valid_config', ['module1'], {"module1_fqdn": "foo.a"})
        self.assertTrue(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertIn("error", module1_config[0])
        config_result = self.client.call('valid_config', ['module1'], {"module1_fqdn": "foo.local"})
        self.assertFalse(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertNotIn("error", module1_config[0])

    def test_network_validation(self):
        config_result = self.client.call('valid_config', ['module1'], {"module1_network_text": "foo"})
        self.assertTrue(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertIn("error", module1_config[1])
        config_result = self.client.call('valid_config', ['module1'], {"module1_network_text": [("192.168.0.0", "255.255.255.0")]})
        self.assertFalse(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertNotIn("error", module1_config[1])
        config_result = self.client.call('valid_config', ['module1'], {"module1_network_0_ip": "foo"})
        self.assertTrue(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertIn("error", module1_config[2])
        config_result = self.client.call('valid_config', ['module1'], {"module1_network_0_ip": "192.168.0.45"})
        self.assertTrue(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertIn("error", module1_config[2])
        config_result = self.client.call('valid_config', ['module1'], {"module1_network_0_ip": "340.45.30", "module1_network_0_mask": "255.0.0.0"})
        self.assertTrue(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertIn("error", module1_config[2])
        config_result = self.client.call('valid_config', ['module1'], {"module1_network_0_mask": "255.0.0.0"})
        self.assertTrue(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertIn("error", module1_config[2])
        config_result = self.client.call('valid_config', ['module1'], {"module1_network_0_mask": "400.500.0.0"})
        self.assertTrue(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertIn("error", module1_config[2])
        config_result = self.client.call('valid_config', ['module1'], {"module1_network_0_ip": "192.168.0.0", "module1_network_0_mask": "255.255.255.0"})
        self.assertFalse(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertNotIn("error", module1_config[2])

    def test_ip_validation(self):
        config_result = self.client.call('valid_config', ['module1'], {"module1_ip": "foo"})
        self.assertTrue(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertIn("error", module1_config[3])
        config_result = self.client.call('valid_config', ['module1'], {"module1_ip": "300.400.0.0"})
        self.assertTrue(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertIn("error", module1_config[3])
        config_result = self.client.call('valid_config', ['module1'], {"module1_ip": "192.168.30.34"})
        self.assertFalse(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertNotIn("error", module1_config[3])

    def test_custom_validation(self):
        config_result = self.client.call('valid_config', ['module1'], {"module1_custom": "bar"})
        self.assertTrue(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertEqual(module1_config[4]["error"], "Value is not foo")
        config_result = self.client.call('valid_config', ['module1'], {"module1_custom": "foo"})
        self.assertFalse(config_result[0]["errors"])
        module1_config = config_result[0]["config"]
        self.assertNotIn("error", module1_config[4])

    def test_multi_required(self):
        config_result = self.client.call('valid_config', ['module2'], {"module2_field1_0_field": ""})
        self.assertTrue(config_result[0]["errors"])
        module2_config = config_result[0]["config"]
        self.assertEqual(module2_config[0]["error"], "This field can't be empty.")
        config_result = self.client.call('valid_config', ['module2'], {"module2_field1_0_field": "foo"})
        self.assertFalse(config_result[0]["errors"])
        module2_config = config_result[0]["config"]
        self.assertNotIn("error", module2_config[0])


if __name__ == '__main__':
    modules = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'validation_modules')
    config = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent.ini')

    cleanup_tests()
    setup_modules(modules)
    process = run_agent(config)
    run_tests(TestConfigValidation, process)
    stop_agent(process)
    cleanup_tests()
