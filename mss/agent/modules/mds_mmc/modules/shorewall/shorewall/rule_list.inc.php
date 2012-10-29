<?php

$ids[] = array('id' => $index, 'page' => $page);

$action = explode('/', $rule[0]);
if (count($action) > 1) {
    $decision[] = $action[0];
    $service[] = $action[1];
    $proto[] = "";
    $port[] = "";
}
else {
    $decision[] = $action[0];
    $service[] = "";
    $proto[] = $rule[3];
    $port[] = $rule[4];
}
$actionsDelete[] = $deleteAction;

?>
