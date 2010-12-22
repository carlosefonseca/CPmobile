<?php

$fin = "estacoes.txt";
$fout= "estacoes.js";

$json;

if (!file_exists($fout) || isset($_GET["reload"])) {
	$fp = fopen($fin, "r");
	$txt = fread($fp, filesize($fin));
	fclose($fp);

	$arr = explode("\n", $txt);
	$json = json_encode($arr);
	
	$fp = fopen($fout, "w+");
	fwrite($fp, $json);
	fclose($fp);
} else {
	$fp = fopen($fout, "r");
	$json = fread($fp, filesize($fout));
	fclose($fp);
}

echo $json;

?>