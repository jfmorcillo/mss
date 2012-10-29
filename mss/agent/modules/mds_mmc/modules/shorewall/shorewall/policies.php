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

$p = new PageGenerator(_T("Firewall policies", "shorewall"));
$p->setSideMenu($sidemenu);
$p->display();

echo '<p>' . _T("Default policies applies if no rule match the request.") . '</p>';

// Handle form return

if (isset($_POST['bsave'])) {
    foreach(getPolicies() as $policy) {
        if (isset($_POST[$policy[0] . "_" . $policy[1] . "_policy"])) {
            $new = $_POST[$policy[0] . "_" . $policy[1] . "_policy"];
            $old = $policy[2];
            if ($new != $old) {
                changePolicies($policy[0], $policy[1], $new, $policy[3]);
            }
        }
    }
    new NotifyWidgetSuccess(_T("Firewall policies changed."));
    header("Location: " . urlStrRedirect("shorewall/shorewall/policies"));
}

// Policies form

$f = new ValidatingForm();
$f->push(new Table());

foreach(getPolicies() as $policy) {
    if (startsWith($policy[0], "lan") || startsWith($policy[0], "wan")) {
        $label = sprintf("%s (%s) → %s (%s)", getZoneType($policy[0]), $policy[0], getZoneType($policy[1]), $policy[1]);
        $decisionTpl = new SelectItem($policy[0] . "_" . $policy[1] . "_policy");
        $decisionTpl->setElements(array(_T("Accept"), _T("Drop"), _T("Reject")));
        $decisionTpl->setElementsVal(array("ACCEPT", "DROP", "REJECT"));
        $decisionTpl->setSelected($policy[2]);
        $f->add(new TrFormElement($label, $decisionTpl));
    }
}

$f->pop();
$f->addButton("bsave", _T("Save"));
$f->display();

function getZoneType($zoneName) {
    if (startsWith($zoneName, "lan"))
        return _T("Internal");
    if (startsWith($zoneName, "wan"))
        return _T("External");
    if ($zoneName == "fw")
        return _T("Server");
    if ($zoneName == "all")
        return _T("All");
    return _T("Unknow");
}

function startsWith($haystack, $needle) {
    return !strncmp($haystack, $needle, strlen($needle));
}

?>
