from mmc.plugins.shorewall import get_zones, get_zones_types, \
    ShorewallPolicies

internal_zones = get_zones(get_zones_types()[0])
external_zones = get_zones(get_zones_types()[1])

policies = ShorewallPolicies()
last_policy_idx = len(policies.get_conf()) - 1
# insert VPN policies before the last one
policies.add_line(['vpn', 'fw', 'DROP'], last_policy_idx)
for zone in internal_zones + external_zones:
    policies.add_line(['vpn', zone, 'DROP'], last_policy_idx)
    policies.add_line([zone, 'vpn', 'DROP'], last_policy_idx)

policies.write()
