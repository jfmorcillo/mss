"""
A MSS XML-RPC client example
"""

import logging
from mss.lib.xmlrpc import XmlRpc;
client = XmlRpc();

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

err, result = client.call("authenticate", "root", "mandriva")
if result:
    logger.debug("Getting mds_mmc module details")
    err, result = client.call("get_module_details", "mds_mmc")
    if not err:
        logger.debug(result)
    logger.debug("Getting mds_mmc module configuration description")
    err, result = client.call("get_config", ["mds_mmc"])
    if not err:
        logger.debug(result)
else:
    logger.error("Authentication failed")
