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

$src = explode(':', $rule[1]);
if ($src[1])
    $src_ip[] = $src[1];
else
    $src_ip[] = "All";

$dest = explode(':', $rule[2]);
$dest_tmp = $dest[1];
if (isset($dest[2]))
    $dest_tmp .= ":" . $dest[2];
$dest_ip[] = $dest_tmp;

$actionsDelete[] = $deleteAction;

?>
