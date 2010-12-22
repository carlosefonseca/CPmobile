function presentAutocomplete(field, out) { //both JQuery objects
	var txt = field.val();
	if (txt.length == 0) {
		presentFavorites(field, out);
	} else {
		db.transaction(function(tx){
			tx.executeSql("SELECT * FROM estacoes WHERE n LIKE '"+txt+"%' LIMIT 10", [], function(tx, results){
				insertAcWords(field, out, results.rows);
			});
		})
	}
}


function insertAcWords(field, out, rs, fav) {
	var l = rs.length;
	if (fav) { out.html("★ "); } else {	out.empty(); }
	
	if (l == 0) {
		if (fav) { out.text("★ Estações + usadas aparecerão aqui")} else {
		out.text("Não há estações com esse nome."); }
		out.slideDown("fast");
		return;
	}
	
	for (var i = 0 ; i < l ; i++) {
		e = rs.item(i).n;
		$(document.createElement('span')).text(e).click(function(){
			autocomplete(field, out, this.innerText)
			}).appendTo(out);
	}
	out.slideDown("fast");
}


function presentFavorites(field, out) {
	db.transaction(function(tx) {
		tx.executeSql('SELECT n FROM estacoes WHERE u>0 ORDER BY u DESC LIMIT 6',[],function(tx, results) {insertAcWords(field, out, results.rows, true)});
	})	
}


function autocomplete(field, out, txt) {
	//console.log("Autocompleting "+field.attr("id")+" with "+txt);
	var next = field.val(txt).attr("tabindex");
	out.slideUp("fast");
//	$("#theform input[tabindex="+(next*1+1)+"]").click();	
}

function acBluring(field, out) {
	if (out.children().length == 1) {
		autocomplete(field, out, out[0].children[0].innerText);
	}
	out.slideUp("fast")
}


function createHours(curr) {
	var sel = $("#hour");
	var opt = sel.children(":first");
	for (var i = 1 ; i < 24 ; i++) {
		opt.clone().text(i+"h").val(i).appendTo(sel);
	}
	sel.attr("selectedIndex",curr);
	opt.clone().text("qq").val("").prependTo(sel);
}

function dothesearch(){
	var dayFormat = /201[01]-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])/;

	if ($("#departure").val() == "" || $("#arrival").val() == "") {
		alert("Por favor preencha as estações de partida e de chegada.");
		return false;
	}
	if (!$("#day").val().match(dayFormat)) {
		alert("A data tem que estar no formato YYYY-MM-DD.");
		$("#day").focus();
		return false;
	}
	if (!($("#hour").val() < 24)) {
		alert("A hora está errada.");
		$("#hour").focus();
		return false;
	}
	$("#spinner").fadeIn();
	window.scrollTo(0,0);
	
	console.log("Requesting data: "+$("#theform").serialize());
	$.getJSON('getdata.php', $("#theform").serialize() , function(data,t) {fillTrainHours(data)});
	incStationUsage($("#departure").val());
	incStationUsage($("#arrival").val());
	return false;
};


function fillTrainHours(data) {
	//console.log("Data receiveid: "+data);
	if (data.length == 0) { $("#spinner").fadeOut(); alert("Não foram encontrados resultados."); return; }
	var rows = $("#trainhours #results");
	$("li:not(:first)",rows).remove();
	var first = $("li:first", rows);
	var nrows = $("li", rows).length;
	var now = new Date();
	var considerTime = (defaultDate == $("#theform #day").val());

	for (var r in data) {	// cada comboio
		if (r>nrows) {
			$(first).clone().attr("id", "t"+r).removeClass().appendTo(rows);
		}
		var row = $("#t"+r, rows);
		for (c in data[r]) {
			$(".t"+c,row).text(data[r][c]);
		}

		//time of trains  // valido se dia de pesquisa = hoje
		if (considerTime) {
			var split = data[r]["d"].split('h');
			var traintime = new Date();
			traintime.setHours(split[0]);
			traintime.setMinutes(split[1]);
			var timeto = new Date(traintime-now);
	
			//console.log(timeto.valueOf());
	
			if (timeto.valueOf() < 0) {					// passado
				row.addClass("lostTrain");
			} else if (timeto.valueOf() < 3600000) {	// presente
				$(".t2",row).text("("+timeto.getMinutes()+"min)");
			} else {
				$(".t2",row).text("");
			}
		}
	}
	$("#spinner").fadeOut();
	jQT.goTo("#trainhours","slide");
}



function incStationUsage(st) {
	console.log("A incrementar '"+st+"'");
	db.transaction(function(tx){
		tx.executeSql('UPDATE estacoes SET u=(u+1) WHERE n="'+st+'"');
	})
}


function initDb() {
	if (db) {
		db.transaction(function(tx) {
			tx.executeSql('CREATE TABLE IF NOT EXISTS estacoes (n unique,u,lat,lng)');
			tx.executeSql('CREATE TABLE IF NOT EXISTS opcoes (key unique,val)');
			tx.executeSql("SELECT val FROM opcoes WHERE key = 'estacoes'",[], function(tx,results){verificaEstacoes(results.rows)});
		});
	}
}


function verificaEstacoes(rows) {
	if (rows.length == 0 || (rows.length == 1 && rows.item(0).val < 500)) {
		console.log("A descarregar todas as estações");
		var estacoes = $.getJSON("estacoes.php",function(data, ts){insertEstacoes(data)});
	} else {
		console.log("db contem "+rows.item(0).val+" estacoes");
		db.transaction(function(tx) {
			tx.executeSql("SELECT val FROM opcoes WHERE key = 'usage'",[],function(tx,results){verificaUsage(results.rows)});
		})
	}
}

function verificaUsage(rows) {
	if (rows.length == 0 || (rows.length == 1 && rows.item(0).val != 1)) {
		console.log("A actualizar a DB para as estatisticas de uso");
		db.transaction(function(tx) {
			tx.executeSql('UPDATE estacoes SET u=0 WHERE u is null');
			tx.executeSql('INSERT INTO opcoes (key, val) VALUES ("usage", 1)');
		})
	}
}


function insertEstacoes(estacoes) {
//	console.log(estacoes);
	db.transaction(function(tx) {
		tx.executeSql('DELETE FROM estacoes WHERE 1=1');
		for (var i = 0 ; i < estacoes.length-1 ; i++) {
			est = estacoes[i];
			tx.executeSql('INSERT INTO estacoes (n, u) VALUES ("'+est+'", 0)');
		}
		est = estacoes[i];
		tx.executeSql('INSERT INTO estacoes (n) VALUES ("'+est+'")', [], function(){updateCountEstacoes()});
		tx.executeSql('INSERT INTO opcoes (key, val) VALUES ("estacoes", (SELECT count(n) FROM estacoes))');
		tx.executeSql('INSERT INTO opcoes (key, val) VALUES ("usage", 1)');
	});
}

function updateCountEstacoes() {
	console.log("updating");
	db.transaction(function(tx){
		tx.executeSql('UPDATE opcoes SET val (SELECT count(n) FROM estacoes) WHERE key="estacoes"', [],
			function(tx,r){console.log("updated")}
		);
	});
}

function theMonth(d) { 	var m = d.getMonth()+1;  return m<10?"0"+m:m; }
