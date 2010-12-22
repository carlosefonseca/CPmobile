<script type="text/javascript">

	var now = new Date();
	var reqdate = new Date().parse("2010-10-07");
	var considerTime = (now == reqdate);
document.write(">"+reqdate+" "+now);	

function theMonth() {
	var m = now.getMonth()+1;
	return m<10?"0"+m:m;
}

nowstr = now.getFullYear()+"-"+theMonth()+"-"+now.getDate()
document.write(nowstr);
document.write("2010-08-27" == nowstr);


</script>