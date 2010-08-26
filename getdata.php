<?php
function normalize ($string) {
    $table = array(
        'Š'=>'S', 'š'=>'s', 'Đ'=>'Dj', 'đ'=>'dj', 'Ž'=>'Z', 'ž'=>'z', 'Č'=>'C', 'č'=>'c', 'Ć'=>'C', 'ć'=>'c',
        'À'=>'A', 'Á'=>'A', 'Â'=>'A', 'Ã'=>'A', 'Ä'=>'A', 'Å'=>'A', 'Æ'=>'A', 'Ç'=>'C', 'È'=>'E', 'É'=>'E',
        'Ê'=>'E', 'Ë'=>'E', 'Ì'=>'I', 'Í'=>'I', 'Î'=>'I', 'Ï'=>'I', 'Ñ'=>'N', 'Ò'=>'O', 'Ó'=>'O', 'Ô'=>'O',
        'Õ'=>'O', 'Ö'=>'O', 'Ø'=>'O', 'Ù'=>'U', 'Ú'=>'U', 'Û'=>'U', 'Ü'=>'U', 'Ý'=>'Y', 'Þ'=>'B', 'ß'=>'Ss',
        'à'=>'a', 'á'=>'a', 'â'=>'a', 'ã'=>'a', 'ä'=>'a', 'å'=>'a', 'æ'=>'a', 'ç'=>'c', 'è'=>'e', 'é'=>'e',
        'ê'=>'e', 'ë'=>'e', 'ì'=>'i', 'í'=>'i', 'î'=>'i', 'ï'=>'i', 'ð'=>'o', 'ñ'=>'n', 'ò'=>'o', 'ó'=>'o',
        'ô'=>'o', 'õ'=>'o', 'ö'=>'o', 'ø'=>'o', 'ù'=>'u', 'ú'=>'u', 'û'=>'u', 'ý'=>'y', 'ý'=>'y', 'þ'=>'b',
        'ÿ'=>'y', 'Ŕ'=>'R', 'ŕ'=>'r',
    );
    $string = strtr($string, $table);
    $string = preg_replace("/[^a-zA-Z0-9\s-]/", "", $string);
    return $string;
}



// GET PARAMETERS
if (!isset($_GET["depart"]) && !isset($_GET["arrival"]))
die("depart and arival are required");

$depart = normalize($_GET["departure"]);
$arrival= normalize($_GET["arrival"]);
$day 	= normalize($_GET["day"]);
$hour 	= normalize($_GET["hour"]);

$postData = "depart=$depart&arrival=$arrival&date=$day&timeType=Partida&time=$hour&allServices=allServices&returnDate=&returnTimeType=Partida&returnTime=";

//CONFIGURE AND DOWNLOAD THE PAGE
$ch = curl_init("http://www.cp.pt/cp/searchTimetable.do");

curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($ch, CURLOPT_HEADER, 0);
curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);

$f = curl_exec($ch);
curl_close($ch);


//FILTER JUST THE DATA TABLE
$needleStart = '<table width="606" border="0" cellspacing="0" cellpadding="0" class="fd_content">';
$needleEnd = '<img src="static/images/pix.gif" alt="" width="7" height="10" border="0" /><br />';

$start = strpos($f, $needleStart);
$end = strpos($f, $needleEnd, $start);
$f = substr($f, $start, $end-$start);

//TRANSFORM HTML IN JSON DATA
$rows = explode('<td width="18" align="right"><a href="javascript:toggleLine(', $f);

unset($rows[0]);

$final = array();

//id type departure arrival length
$key2field = array(1=>"i", 2=>"t", 3=>"d", 4=>"a", 5=>"l");

foreach($rows as $r) {
	$cells = explode('<td ', $r,7);
	unset($cells[0], $cells[6]);
	
	$line = array();
	
	foreach($cells as $k => $c) {
		$st = strpos($c, ">")+1;
		$le = strpos($c, "</td", $st)-$st;
		$c = substr($c, $st, $le);
		$line[$key2field[$k]] = $c;
	}
	if (strlen($line['t'])>5) {
		$line["t"] = str_replace('<b class="orange">|</b>', '+', $line["t"]);
	}
	$line["i"] = substr($line["i"], 0 ,-1);
	$final[$line["i"]] = $line;
}

echo json_encode($final);