<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require("modules/shorewall/includes/shorewall-xmlrpc.inc.php");
require("modules/shorewall/shorewall/localSidebar.php");
require("graph/navbar.inc.php");

// Rules list display

$ajax = new AjaxFilter(urlStrRedirect("shorewall/shorewall/ajax_" . $page));
$ajax->display();

$p = new PageGenerator(_T("Port forwarding rules", "shorewall"));
$p->setSideMenu($sidemenu);
$p->display();

$ajax->displayDivToUpdate();

// Handle form return

if (isset($_POST['badd'])) {
    if (isset($_POST['service'])) {
        $service = $_POST['service'];
        if ($service) {
            $src_ip = $_POST['src_ip'];
            $dest_ip = $_POST['dest_ip'];
            $dest_port = $_POST['dest_port'];
            if ($service == "custom") {
                if (!$_POST['proto'] || !$_POST['port']) {
                    new NotifyWidgetFailure(_T("Protocol and port must be specified."));
                    header("Location: " . urlStrRedirect("shorewall/shorewall/" . $page));
                }
                else {
                    $action = "DNAT";
                    $proto = $_POST['proto'];
                    $port = $_POST['port'];
                }
            }
            else {
                $action = "DNAT/" . $service;
                $proto = "";
                $port = "";
            }
            foreach(getZones($src) as $zone)
                foreach(getZones($dst) as $dest) {
                    if ($src_ip)
                        $src = $src . ':' . $src_ip;
                    if ($dest_port)
                        $dst =  $dest . ":" . $dest_ip . ":" . $dest_port;
                    else
                        $dst =  $dest . ":" . $dest_ip;
                    addRule($action, $src, $dst, $proto, $port);
                }
            new NotifyWidgetSuccess(_T("Rule added."));
        }
    }
    else {
        new NotifyWidgetFailure(_T("Service must be specified."));
    }
    header("Location: " . urlStrRedirect("shorewall/shorewall/" . $page));
}

// Add rule form

print '<script type="text/javascript" src="modules/shorewall/includes/functions.js"></script><br />';

$t = new TitleElement(_T("Add port forwarding rule"), 2);
$t->display();

$f = new ValidatingForm();
$f->push(new Table());

$macros = getServices();
$services = array("", _T("Custom...")) + $macros;
$servicesVals = array("", "custom") + $macros;
$serviceTpl = new SelectItem("service", "toggleCustom");
$serviceTpl->setElements($services);
$serviceTpl->setElementsVal($servicesVals);

$f->add(new TrFormElement(_T("Service"), $serviceTpl));
$f->pop();

$customDiv = new Div(array("id" => "custom"));
$customDiv->setVisibility(false);
$f->push($customDiv);
$f->push(new Table());

$protoTpl = new SelectItem("proto");
$protoTpl->setElements(array("", "TCP", "UDP"));
$protoTpl->setElementsVal(array("", "tcp", "udp"));

$f->add(new TrFormElement(_T("Protocol"), $protoTpl));
$f->add(
        new TrFormElement(_T("Port(s)"), new InputTpl("port", "/^[0-9:,]+$/"), 
                          array("tooltip" => _T("You can specify multiple ports using ',' as separator (eg: 22,34,56). Port ranges can be defined with ':' (eg: 3400:3500 - from port 3400 to port 3500)."))),
        array("value" => "")
);

$f->pop();
$f->pop();
$f->push(new Table());

$f->add(
        new TrFormElement(_T("Source IP(s)"), new InputTpl("src_ip"), 
                          array("tooltip" => _T("Allow connection from IP(s) address(es) (separate IPs with ',')."))),
        array("value" => "")
);

$f->add(
        new TrFormElement(_T("Destination IP"), new InputTpl("dest_ip"), 
                          array("tooltip" => _T("The computer IP in the internal network where the request will be transfered."))),
        array("value" => "", "required" => true)
);
$f->add(
        new TrFormElement(_T("Destination port(s)"), new InputTpl("dest_port", "/^[0-9]+$/"),
                          array("tooltip" => _T("If not specified, destination port(s) will be the same as the incoming port(s)"))),
        array("value" => "")
);

$f->pop();
$f->addButton("badd", _T("Add rule"));
$f->display();

?>
