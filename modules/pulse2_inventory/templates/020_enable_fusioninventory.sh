#!/bin/sh

#if [ ! -e $config/glpi-reinitialize ]; then
#  exit 0
#fi

echo
echo "#####################################"
echo "Enable GLPI FusionInventory plugin..."
echo "#####################################"
echo

# Define $HOME so mysql can find .my.cnf !!!!!
if [ -z ${home} ] && [ `id -u` -eq 0 ]; then export "HOME=/root"; fi

php /usr/share/glpi/plugins/fusioninventory/tools/cli_install.php
echo

fusioninventoryid=`mysql -N -s -e 'SELECT id FROM glpi_plugins WHERE directory="fusioninventory"' glpi;`
fusinvinventoryid=`mysql -N -s -e 'SELECT id FROM glpi_plugins WHERE directory="fusinvinventory"' glpi;`
fusinvsnmpid=`mysql -N -s -e 'SELECT id FROM glpi_plugins WHERE directory="fusinvsnmp"' glpi;`
fusinvdeployid=`mysql -N -s -e 'SELECT id FROM glpi_plugins WHERE directory="fusinvdeploy"' glpi;`

echo "INSERT INTO glpi_plugin_fusioninventory_profiles VALUES \
     (1,'agent','w',${fusioninventoryid},4), \
     (2,'remotecontrol','w',${fusioninventoryid},4), \
     (3,'configuration','w',${fusioninventoryid},4), \
     (4,'wol','w',${fusioninventoryid},4), \
     (5,'unknowndevice','w',${fusioninventoryid},4), \
     (6,'task','w',${fusioninventoryid},4), \
     (7,'iprange','w',${fusioninventoryid},4), \
     (8,'credential','w',${fusioninventoryid},4), \
     (9,'credentialip','w',${fusioninventoryid},4), \
     (10,'existantrule','w',${fusinvinventoryid},4), \
     (11,'importxml','w',${fusinvinventoryid},4), \
     (12,'blacklist','w',${fusinvinventoryid},4), \
     (13,'ESX','w',${fusinvinventoryid},4), \
     (14,'configuration','w',${fusinvsnmpid},4), \
     (15,'configsecurity','w',${fusinvsnmpid},4), \
     (16,'networkequipment','w',${fusinvsnmpid},4), \
     (17,'printer','w',${fusinvsnmpid},4), \
     (18,'model','w',${fusinvsnmpid},4), \
     (19,'reportprinter','w',${fusinvsnmpid},4), \
     (20,'reportnetworkequipment','w',${fusinvsnmpid},4), \
     (21,'packages','w',${fusinvdeployid},4), \
     (22,'status','w',${fusinvdeployid},4);" | mysql glpi

echo "update glpi_plugin_fusioninventory_configs set value = '/var/lib/glpi/files/_plugins/fusinvdeploy/upload' where value = 'cli_install.php/files/_plugins/fusinvdeploy/upload';" | mysql glpi

echo "update glpi_plugin_fusioninventory_configs set value = 'http://127.0.0.1/glpi' where type = 'agent_base_url';" | mysql glpi

chown -R apache /var/lib/glpi/_plugins/fusi*


### Add a few blacklists
echo "INSERT INTO glpi_plugin_fusinvinventory_blacklists (plugin_fusioninventory_criterium_id, value) VALUES ('2', '00020003-0004-0005-0006-000700080009');" | mysql glpi
echo "INSERT INTO glpi_plugin_fusinvinventory_blacklists (plugin_fusioninventory_criterium_id, value) VALUES ('2', 'Not Settable');" | mysql glpi
echo "INSERT INTO glpi_plugin_fusinvinventory_blacklists (plugin_fusioninventory_criterium_id, value) VALUES ('1', 'Not Applicable');" | mysql glpi
echo "INSERT INTO glpi_plugin_fusinvinventory_blacklists (plugin_fusioninventory_criterium_id, value) VALUES ('1', '-');" | mysql glpi
echo "INSERT INTO glpi_plugin_fusinvinventory_blacklists (plugin_fusioninventory_criterium_id, value) VALUES ('1', 'To be filled by O.E.M.');" | mysql glpi


### Two new rules for computers linking

# Update other rules ranking
echo "UPDATE glpi_rules SET ranking = ranking+2 WHERE ranking > 2 AND sub_type = 'PluginFusioninventoryRuleImportEquipment'" | mysql glpi

# Insert two new rules
echo "INSERT INTO glpi_rules VALUES('',0,'PluginFusioninventoryRuleImportEquipment',3,'Computer mac + no serial + no uuid','','AND',1,'',NOW(),0);" | mysql glpi
echo "INSERT INTO glpi_rules VALUES('',0,'PluginFusioninventoryRuleImportEquipment',4,'Computer uuid + mac','','AND',1,'',NOW(),0);" | mysql glpi

# Get these rules ids
maxid=`echo "SELECT MAX(id) FROM glpi_rules" | mysql -s glpi`
maxidmin=`expr ${maxid} - 1`

# Insert criterias for rules #3
echo "INSERT INTO glpi_rulecriterias VALUES('','${maxidmin}','serial',9,'1')" | mysql glpi
echo "INSERT INTO glpi_rulecriterias VALUES('','${maxidmin}','uuid',9,'1')" | mysql glpi
echo "INSERT INTO glpi_rulecriterias VALUES('','${maxidmin}','itemtype',0,'Computer')" | mysql glpi
echo "INSERT INTO glpi_rulecriterias VALUES('','${maxidmin}','mac',10,'1')" | mysql glpi
echo "INSERT INTO glpi_rulecriterias VALUES('','${maxidmin}','mac',8,'1')" | mysql glpi

# Insert criterias for rules #4
echo "INSERT INTO glpi_rulecriterias VALUES('','${maxid}','uuid',10,'1')" | mysql glpi
echo "INSERT INTO glpi_rulecriterias VALUES('','${maxid}','uuid',8,'1')" | mysql glpi
echo "INSERT INTO glpi_rulecriterias VALUES('','${maxid}','itemtype',0,'Computer')" | mysql glpi
echo "INSERT INTO glpi_rulecriterias VALUES('','${maxid}','mac',10,'1')" | mysql glpi
echo "INSERT INTO glpi_rulecriterias VALUES('','${maxid}','mac',8,'1')" | mysql glpi

# Insert actions for rules #3 and #4
echo "INSERT INTO glpi_ruleactions VALUES('','${maxidmin}','assign','_fusion',0)" | mysql glpi
echo "INSERT INTO glpi_ruleactions VALUES('','${maxid}','assign','_fusion',0)" | mysql glpi

# Fix default entity rule to use id = 1 instead of 0 (root)
echo "UPDATE glpi_ruleactions SET value = 1 WHERE rules_id IN ( SELECT id FROM glpi_rules WHERE sub_type = 'PluginFusinvinventoryRuleEntity' );" | mysql glpi
