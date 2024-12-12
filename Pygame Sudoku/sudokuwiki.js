/*-----------------------------------------------------------------------
	This script is NOT freeware. Please email if you want to re-use it.
	Your comments on how it could be improved would be appreciated
	Andrew Stuart, 23 May 2005, andrew@str8ts.com
-----------------------------------------------------------------------*/
"use strict";
let WebSudoku = undefined;
let stage = 0, laststage = 0;
let print_version=false;
let showhints=true;
let steps=0;
let save_dstring='';
let bunched=false;
let some_changes=false;
let firsttime=true;
let savehelp = '';
let some_saved=false;
let cordX,cordY;
const rcbname=["Row","Col","Box"];
const abety="ABCDEFGHJ";
const abetx="123456789";
let editmode=0;
let enterclues = true;
let enteroddeven = false;
let MAX_STRAT = strat_list.length+5;
let coordmode=1;
let cnv, jg=null;
const which_box=[[0,0,0,1,1,1,2,2,2],[0,0,0,1,1,1,2,2,2],[0,0,0,1,1,1,2,2,2],[3,3,3,4,4,4,5,5,5],[3,3,3,4,4,4,5,5,5],[3,3,3,4,4,4,5,5,5],[6,6,6,7,7,7,8,8,8],[6,6,6,7,7,7,8,8,8],[6,6,6,7,7,7,8,8,8]];
const gexSUD=[
"300967001040302080020000070070000090000873000500010003004705100905000207800621004", // Easiest
"000004028406000005100030600000301000087000140000709000002010003900000507670400000", // Gentle
"720096003000205000080004020000000060106503807040000000030800090000702000200430018", // Moderate */
"309000400200709000087000000750060230600904008028050041000000590000106007006000104", // Tough
"000704005020010070000080002090006250600070008053200010400090000030060090200407000", // Diabolical
"000041000060000200000000000320600000000050041700000000000200300048000000501000000", // Easy 17 Clue
"002090300805000000100000000090060040000000058000000001070000200300500000000100000", // Hard 17 Clue
"000000000001900500560310090100600028004000700270004003040068035002005900000000000", // Naked Triples
"300000000970010000600583000200000900500621003008000005000435002000090056000000001", // Hidden Triple
"000705006000040081000030050041000008060000020500000430000070000978050000300201000", // Hidden Quad
"000921003009000060000000500080403006007000800500700040003000000020000700800195000", // Intersection Removeal
"007010000000800500180009064600000003071080640400000005840600031005002000000030700", // x-wing example # .....456..6...3.....46..3.998..4.....472.695.....7..834.6..28.....4...1..298.....
"000000060002705000500013009704500003003040100900007405600920004000301800080000000", // Simple Colouring Rule 2
"090010030800300009070006005080003000052000370000400080900800040600009008010050090", // Simple Colouring Rule 4
"645010893738459621219638745597060184481975000326841579902080010803190000164020908", // y-wing example
"030609020000280000100000009000000653720060091365000000200000007000016000010507040", // RE
"050030602642895317037020800023504700406000520571962483214000900760109234300240170", // SwordFish
"300000000600000048507006300080700100100603002005008060003100906790000005000000003", // XYZ-Wing
"000000000890632004002090800070000600900005008001000030003010200600873019000000000", // X-Cycle (weak link)
"000000020005080400400100800090002000037000560000970000004008605006040700080000000", // X-Cycle (strong link)
"040005800700010900003007100400700000050908040000002008009500700000020005004100090", // X-Cycle (off-chain)
"902060300850000060000000000170850000009207600000016050000000000030000078004090200", // XY-Chain x 16
"093824560085600002206075008321769845000258300578040296850016723007082650002507180", // 3D Medusa Rule 1
"503682140214597836680300500305200904000050001108409750000000010706100290031925000", // 3D Medusa Rule 2
"050020000192000004004600000000008005006941800900700000000006300300000621000080090", // 3D Medusa Rule 3
"587412693206037800100008200002001748050724900714800500005240109001085400420170305", // 3D Medusa Rule 4
"080276049000000000200309008001000060007000800090000500900608003000000000520904000", // 3D Medusa Rule 5
"900060500001000040300700008000058400060000080002040300100005009020000800007030002", // 3D Medusa Rule 6
"400100000002000004008090100006403800080000010007906200003070000200000605000002001", // Jelly-Fish
"016098020020000784000000000007009500000307000005100400000000000681000050050670810", // UR type 1
"900082030000000040000090100700031004090000080200540306005060000070000000010450003", // UR type 2
"000000600300006410000480700000050100040802050002070000006729000094600007001000000", // UR type 2b
"100020050000730200300400008005608000002000400000100700800006000001007000030010002", // UR type 2c
"070000000060020040801000300004203700200040006003806400002000807090030010000000060", // UR type 3
"000604001028000050000075300000020005006501900100000000005160000060000120300908000", // UR type 3b
"900500081000802500005000020030001050100040003050600090080000900006709000790008004", // UR type 4
"090208001620000090800000000008027000003000400000350100000000502070000034200401060", // UR type 4b
"000030000073420060000006403387961245124080639965342817701658000050093080000004000", // UR type 5
"120300000340000100005000000602400500000060070000008006004200300000070009000009080", // SK Loop - puzzle called 'cigarette'
"020310700300090000805000200000230000500000009000769000009000107000000003001053020", // EUR type 1
"800000002020800040005007900000040800640509031002010000006900200090005060500000003", // EUR type 4
"002701030000503000009000580030000090408000703010000060046000100000409000090108600", // HUR type 1
"650040000000000200300006008060800300000020000041009060200100007003000400000070031", // HUR type 2
"800001060021040000000506700069000240000000000072000130003609000000020390010400006", // HUR type 2b
"000020000500400008031006090040809037000000000980203050060700480200004006000000000", // WXYZ-Wing
"000138000503900400700050000079002010000000000080500960000090003006003107000641000", // APE
"003902000070006800980000000300270005000000000600035007400000069006300070000809400", // GXC	(Strong link)
"130060209005030000000800006000080503050000020803010000300002000000040600407050031", // GXC	(Weak link)
"000700000620000000004052300057030028090000010130070060005490600000000032000000000", // GXC	(off chain)
"050000070003060800060100300900607001000203000500409007005008040008020700010000050", // FSF
"006301000190000006004090100059600040000030000060004920007050600300000015000408300", // FSF Sashimi
"000024090000301070400005008007000054004000300210000900800700002040109000050480000", // AIC (Strong)
"190000005804000000000800790000720000000904200000065000048003000002000608300000027", // AIC (Weak)
"000000900600103005001290600000000008028040360700000000007019400500306007009000000", // AIC (off chain)
"008050600940000000250300079000600000020010040000007000360008057000000016007020400", // Dual CFC
"020000050000403000906005800800020490000000000094080061007300906000102000050000030", // Sue-De-Coq
"105000009000080501040000060080067000000809000000350026060000050403070000900000302", // CFC
"000004065007000003800310400006070000700109008000050200003068009000000800520900000", // Nishio
"600097030000020400300600007003000050500000002080000900700806001009010000010300005", // ALS
"000002000035100870800300009090015000002000600000620040900001003013006520000700000", // POM
"000000700007109000680070010001090600000300020040000003008060100500000040000002005", // Exocet unsolvable no 218
"000000605000300090080004001040020970000000000031080060900600020010007000504000000", // Riddle of Sho
"100007090030020008009600500005300900010080002600004000300000010041000007007000300", // ESCARGOT
"000001002003000040050060700000800070007003800900050001006080200040600007200009060", // Shining Mirror
"100000002090400050006000700050903000000070000000850040700000600030009080002000001", // Easter Monster
"800000000003600000070090200050007000000045700000100030001000068008500010090000400"]; // Arto Inkala

const gexSDX=[
"400805200000000000080070000000208907000000004105300000000000010000000000001007006", // 18 clue moderate
"000000010000000200030000405000000000000000000000006000000070000602000080000340000", // 12 clue tough
"700020080000000900000309051000070000008450100000060000000500000000000000010080002",  // Tough Strategies
"000008100700090056005000700000000070080000000060000000608000400040010003001800000",  // Big Hidden Quad */
"209006003000020600007000200008070020700682005052031867026040900074060002100200006",  // Y-Wing / X-Wing
"010200050009000400000100000000467090001508600090301000000002000008000900070005040",  // SwordFish
"000006000070000000630010074160000008020908040400000029790000081000000060000700000",  // Simple Colouring
"862719354051023700030850100200087005500001000000560003000045030024108500005000841",  // Y-Wing
"500060002002000300000054006020000047000506000850000030000340000004000200900020004",  // Jelly-Fish
"000090050890502030400080070009600003000000000600008500070060005060205047010040000",  // X-Cycle on 7
"000300796376190840490000310600020000000613000000080601130000084504031967067000103",  // UR 1
"009000000312890700800000002000980000700040009000052000900000005005019267000000100",  // UR 4
"625371849834060712791080356350020000400153008100090035047010003083040000216030504",  // XYZ-Wings
"000106025102705006560802000009520008280960000306481209600208004920614507840309002",  // APE
"000002040803000010009010020700030000005000000000060003050040600040000105000900000",  // Finned X-Wing
"000000400020310000000000001700023090002090800030450006000000000060082050009000000",  // Extreme Extreme
"000378000000104000000000000930000054100030002420000013000000000000801000000596000"]; // Unsolveable

// Get the solution count module
var Module = {
	onRuntimeInitialized: function () {
		WebSudoku = Module;
	}
};
const jigsaw_boxes = ["111222333111222333111222333444555666444555666444555666777888999777888999777888999"]; // 0 = SUDOKU
const sudokux_col = "211111112121111121112111211111212111111121111111212111112111211121111121211111112";
const sudokux_map = "100000002010000020001000200000102000000030000000201000002000100020000010200000001";
let gurthmap = [0,0,0,0,0,0,0,0,0];
let UsesGurth = false;
const evens = 170; // Sum of bits of all even numbers
const odds = 341; // Sum of bits of all odd numbers
/*---------------------------------------------------------------------*/
/* Draws the content of a square on the board							*/
/*---------------------------------------------------------------------*/
function set_square(x, y, val, setup)
{
	let t, s;
	const sq_siz=['8pt','16pt','16pt','16pt','8pt','18pt','18pt','18pt'];

	// Get the table cell name out using the coordinates
	t=document.getElementById("a"+y+x);
	if( (setup===0 && showhints) || setup > 0 )
		 t.innerHTML=val;	// Assign the new value to the cell
	else t.innerHTML='&nbsp;';	// Assign the new value to the cell
	if( print_version ) {
		g.c(y,x).color='black';
		t.style.fontSize='20pt';
	} else {
		t.style.fontSize=sq_siz[setup];
	}
	t.style.backgroundColor = g.backgroundColor(y,x);
	t.style.color = g.c(y,x).color;
	t.style.textShadow = (setup == 2) ? '0 0 10px #FF0000' : 'none';
	if (print_version) return;
	s="D" + y.toString()+x.toString();
	if( val == "&nbsp;" )
		document.forms.DataEntry.elements[s].value='';
	else if( setup ) document.forms.DataEntry.elements[s].value=val;
}
/*----------------------------------------------------------------------*/
/* Converts the bit array to a string of numbers for display			*/
/*----------------------------------------------------------------------*/
function lable_square( y, x, deduct )
{
	let lable='', c=0, i, modfact=3, cel;
	g.c(y,x).mask -= deduct;
	g.c(y,x).show = deduct;
	if( bunched )
	{
		if( g.bcmask(y,x) < 5 ) modfact=2;
		for( i=0;i<9;i++ ) {
			if( g.mask(y,x) & (1 << i) )	// i=0 to 8 so first shift is 0 bits
			{
				if( lable.length > 0 ) lable=lable + "&nbsp;";

				if( c && (c % modfact) === 0 ) lable=lable + "<br>";
				lable=lable + (i+1);
				c++;	// <br> it every three numbers
			}
		}
	}
	else
	{
		lable = '<table id="cl' + y + x + '" class="candtb" cellspacing=0 align=center>';
		for( i=0;i<9;i++ )
		{
			if( (i % modfact) == 0 )
				lable=lable + "<tr>";
			cel = '<td id="w' + y + x + i + '"';
			if( g.mask(y,x) & (1 << i) )	// i=0 to 8 so first shift is 0 bits
			{
				if( g.show(y,x) & (1 << i) )
					lable=lable + cel + ' class="fsh">' + (i+1) + '</td>';
				else
					lable=lable + cel + '>' + (i+1) + "</td>";
			}
			else
			{
				if( g.show(y,x) & (1 << i) )
					lable=lable + cel + ' class="fsh">' + (i+1) + '</td>';
				else lable=lable + cel + '>&nbsp;</td>';
			}
			if( (i % modfact) == 2 )
				lable=lable + "</tr>";
		}
		lable=lable + "</table>";
	}
	some_changes=true;
	set_square(x,y,lable,0);
}

/*----------------------------------------------------------------------*/
/* Functions for loading, saving puzzles and the board 					*/
/*----------------------------------------------------------------------*/
function initialize_board()
{
	reset_yes_no( strat_list, 2 );

	laststage=stage=0;

	document.getElementById("backstep").className='GButton';
	document.getElementById("takestep").onclick=take_step;
	document.getElementById("takestep").className = 'SButton';
	if( cookie.read(cookiename) )
	{
		document.getElementById("reload").className="SButton";
		some_saved=true;
	}
	else document.getElementById("reload").className="GButton";

	cnv = document.getElementById("myCanvas");
	if( !jg ) jg = new jsGraphics(cnv);
	jg.clear();
	backgroundList('');
	setKnown();

	detect_gurth(0);
}
function sudokuFromList(loadanyway)
{
	let i,j,v;
	let choose = document.forms.DataEntry.elements["Example"].selectedIndex;
	if( loadanyway && choose == 0 ) { document.forms.DataEntry.elements["Example"].selectedIndex = 1; choose++; }
	if( choose==0 ) return false;
	sudokuWipe();
	choose--;
	for(j=0;j<9;j++)
		for(i=0;i<9;i++) {
			switch (puztype) {
			case 'Sudoku' :
				v=gexSUD[choose].charAt((j*9)+i)*1; break;
			case 'Sudoku X':
				v=gexSDX[choose].charAt((j*9)+i)*1;
			}
			g.c(j,i).clue=g.c(j,i).val=(IsNumeric(v))?v:0;
			g.c(j,i).orig=g.c(j,i).mask=(g.c(j,i).val) ? 0 : 511;
		}
	writeToResults('Puzzle loaded from list, number ' + choose + ' chosen');
	return true;
}
function importPackedString( astr ) {
	let i, j, v;
	let p2 = astr.match(/.{1,2}/g);
	if (p2.length != 81) return false;
	for (j = 0; j < 9; j++)
		for (i = 0; i < 9; i++) {
			v = parseInt(p2[j * 9 + i], 32);
			g.c(j, i).clue = (v & 1) ? 1 : 0;
			v = v >> 1;
			if (bit_count(v) == 1) {
				g.c(j, i).val = bit2int(v) + 1;
				g.c(j, i).orig = g.c(j, i).mask = 0;
			} else {
				g.c(j, i).val = 0;
				g.c(j, i).orig = g.c(j, i).mask = v;
			}
		}
	return true;
}
function sudokuFromSolvePath(thedata) {
	importPackedString(thedata);
	writeToResults('Puzzle loaded from Solve Path output');
	populateBoard(false);
	initialize_board();
}
function sudokuFromURLPacked() {
	const urlParams = new URLSearchParams(window.location.search);
	if( !urlParams.has('bd') ) return false;
	let bd = urlParams.get('bd')
	if (bd.length != 162) return false;
	importPackedString(bd);
	writeToResults('Puzzle loaded from URL with candidates');
	return true;
}
function sudokuFromURLSpecial()
{
	let i,j,v;
	let bd=location.search;
	if( bd.substring(0,3)!=="?n=" ) return false;
	let p1 = bd.split("=");
	let p2 = p1[1].split(",");
	if( p2.length != 81 ) return false;
	for(j=0;j<9;j++)
		for(i=0;i<9;i++) {
			v = p2[j*9+i]*1;
			if( bit_count(v)==1 ) {
				g.c(j,i).clue=g.c(j,i).val=bit2int(v)+1;
				g.c(j,i).orig=g.c(j,i).mask=0;
			} else {
				g.c(j,i).clue=g.c(j,i).val=0;
				g.c(j,i).orig=g.c(j,i).mask=v;
			}
		}
	firsttime = true;
	writeToResults('Puzzle loaded from URL using old candidate format');
	return true;
}
function sudokuFromURL()
{
	let i,j,v;
	const urlParams = new URLSearchParams(window.location.search);
	if( !urlParams.has('bd') ) return false;
	let bd = urlParams.get('bd')
	if( bd.length!=81 || !firsttime ) return false;
	for(j=0;j<9;j++)
		for(i=0;i<9;i++) {
			v = (IsNumeric(bd.charAt((j*9)+i))) ? bd.charAt((j*9)+i) : 0;
			g.c(j,i).clue=g.c(j,i).val=v;
			g.c(j,i).orig=g.c(j,i).mask=(g.c(j,i).val) ? 0 : 511;
		}
	firsttime = true;
	writeToResults('Puzzle loaded from URL');
	return true;
}
function sudokuFromImport(actualstr)
{
	if( actualstr.length!=81 ) return;
	for(let j=0;j<9;j++)
		for(let i=0;i<9;i++)
		{
			g.c(j,i).clue=g.c(j,i).val=parseInt(actualstr.charAt((j*9)+i),10);
			g.c(j,i).orig=g.c(j,i).mask=(g.c(j,i).val) ? 0 : 511;
		}
}
function sudokuFromCookie(cookie_name)
{
	let i,j,arr,isclue;
	let x = cookie.read(cookie_name);
	if (!x) return false;
	arr = x.split(',');
	for( j=0;j<9;j++ )
		for( i=0;i<9;i++ )
		{
			let cc = g.c(j,i);
			isclue = false;
			cc.orig=0;
			let v = parseInt(arr[(j*9)+i],10);
			if( v < 0 ) {
				isclue = true;
				v = -v;
			}
			if( bit_count(v) == 1 ) {
				cc.val=bit2int(v)+1;
				cc.orig=cc.mask=0;
				cc.clue = ( isclue ) ? bit2int(v)+1 :0;
			} else {
				cc.orig=cc.mask=v;
				cc.clue=cc.val=0;
			}
		}
	return true;
}
function writeToResults(astr) {
	let doc;
	if (!document.ifrm) {
		if( document.getElementById("ifrm") )
			doc = document.getElementById("ifrm").contentDocument;
	}
	else doc = document.ifrm.document;
	if( !doc ) return;
	doc.body.innerHTML = astr;
}
function populateBoard(isBB) {
	for(let j=0;j<9;j++)
		for(let i=0;i<9;i++)
		{
			let cc = g.c(j,i);
			cc.box = jigsaw_boxes[0].charAt(j * 9 + i) - 1;
			cc.jb = 5;
			if (puztype == 'Sudoku X') {
				cc.jb = parseInt(sudokux_col.charAt(j * 9 + i), 10);
				cc.diag = parseInt(sudokux_map.charAt(j * 9 + i), 10);
			}
			cc.row = parseInt(rmap.charAt(j*9+i),10);
			cc.col = parseInt(cmap.charAt(j*9+i),10);
			cc.box = parseInt(bmap.charAt(j*9+i),10);
			cc.backgroundColor=cc.jbcol();

			if( cc.val > 0 ) {
				cc.color = (cc.clue) ? sq_col[1] : sq_col[2];

				set_square(i,j,g.val(j,i),1);
			}
			else {
				cc.color=sq_col[0];
				if( isBB && !document.getElementById("autoclear").checked ) {
					set_square(i,j,"&nbsp;",0);
				}
				else {
					lable_square( j,i,0 );
					document.forms.DataEntry.elements['D'+j+i].value='';
				}
			}
		}
}
function load_board()
{
	let x,y;

	cordX=new Array(81);
	cordY=new Array(81);

	if( !sudokuFromURL() )
		if (!sudokuFromURLSpecial())
			if (!sudokuFromURLPacked())
				if( !sudokuFromCookie(cookieauto) )
					if( !sudokuFromList(true) ) return;

	document.getElementById('solvepathdiv').innerHTML = "";

	populateBoard(false);

	initialize_board();
}
function save_board(cookie_name)
{
	let i,j,s='';
	for( j=0;j<9;j++ )
		for( i=0;i<9;i++ ) {
			if( s.length ) s += ',';
			if( g.c(j,i).clue ) s += '-';
			s = s + (g.val(j,i) ? g.valbit(j,i) : g.mask(j,i));
		}
	some_saved=true;
	cookie.create(cookie_name,s,7);
}
function save_my_board()
{
	save_board(cookiename);
	document.getElementById("reload").className="SButton";
	alert("Current Board Saved (as a cookie)");
}
function load_by_list()
{
	if( !sudokuFromList(false) ) return;

//	document.getElementById('solvepathdiv').innerHTML = '';
	populateBoard(false);

	initialize_board();
}

function reload_board()
{
	let x = cookie.read(cookiename);
	if (!x)
	{
		alert("No saved board found");
		return;
	}
	sudokuFromCookie(cookiename);

	populateBoard(false);

	initialize_board();
}
function import_sudoku()
{
	let dstring,c,i,actualstr='';

	dstring=window.prompt("Enter a string of 81 numbers (you can express blanks as 0, *, _ or '.')",save_dstring);
	if( dstring === null ) return;
	if( dstring.length === 0 ) return;

	save_dstring=dstring;

	if (dstring.length != 162) {
		for (i = 0; i < dstring.length; i++) {
			c = dstring.charAt(i);
			if (IsNumeric(c) || c == '0')
				actualstr = actualstr + dstring.charAt(i);
			else if (c == '\u2026') // elipsis
				actualstr = actualstr + '000';
			else if (c == '.' || c == '*' || c == '_')
				actualstr = actualstr + '0';
		}
	}
	else actualstr = dstring;

	if (actualstr.length == 81)
		sudokuFromImport(actualstr);
	else if (actualstr.length == 162)
		importPackedString(actualstr);
	else {
		alert("Your submission contained " + actualstr.length + " numbers. Please check it and press 'Import' again");
		return;
	}
//	document.getElementById('solvepathdiv').innerHTML = '';
	populateBoard(false);

	initialize_board();
	sanity_check(true);
	save_board(cookieauto);
	firsttime=false;
}
function blank_board()
{
	sudokuWipe();
//	document.getElementById('solvepathdiv').innerHTML = '';

	populateBoard(true);

	initialize_board();

	writeToResults('Results go here');
}
function clear_board()
{
	sudokuWipe();
}

function load_print_board()
{
	let i,j,t,cc,h,c;
	let ptype='';

	const urlParams = new URLSearchParams(window.location.search);
	ptype = ( urlParams.has('ptype') ) ? urlParams.get('ptype')*1 : 1;

	if (!sudokuFromURLPacked()) {
		if( !sudokuFromURL() )
			if (!sudokuFromURLSpecial())
				alert('No parameters passed to this page');
				return;
			}

	print_version=true;
	let ptitle = document.getElementById("pagetitle");
	if( urlParams.get('jig')==="-1" ) ptitle.innerHTML = "Sudoku X Puzzle";

	let tTable = document.createElement("TABLE");
	let tBody = document.createElement("TBODY");
	tTable.className = "OuterT";

	let myDiv = document.getElementById("puzzleboard");
	myDiv.innerHTML="";

	myDiv.appendChild(tTable);
	tTable.appendChild(tBody);
	//create the table
	for (j = 0; j < 9; j++) {
		let row = document.createElement("tr");
		tBody.appendChild(row);
		for (i = 0; i < 9; i++) {
			let cell = document.createElement("td");
			cell.id = "a" + j + i;
			row.appendChild(cell);
			c = i * 9 + j;
			g.c(j,i).jc = sudokumap.charAt(c) * 1;
		}
	}

	for(j=0;j<9;j++)
		for(i=0;i<9;i++)
		{
			let cell = document.getElementById("a" + j + i);
			cell.style.border = '1px solid #888888';
			if( j>0 && g.jc(j,i) != g.jc(j-1,i) ) cell.style.borderTop = "3px solid black";
			if( j<8 && g.jc(j,i) != g.jc(j+1,i) ) cell.style.borderBottom = "2px solid black";
			if( i>0 && g.jc(j,i) != g.jc(j,i-1) ) cell.style.borderLeft = "2px solid black";
			if( i<8 && g.jc(j,i) != g.jc(j,i+1) ) cell.style.borderRight = "3px solid black";

			// not really the clue flag, 1 note flag in print context
			// swap the solved number into the notes variable
			h = g.val(j,i);
			if( h>0 && g.c(j,i).clue==0 ) {
				g.c(j,i).mask = (1 << (h-1));
				g.c(j,i).val = 0;
			}

			if( g.val(j,i) > 0 ) {
				cell.className = 'InnerBig';
				cell.innerHTML = g.val(j,i);
				//set_square(i,j,,9);
				//cell.style.backgroundColor = '#ffffff';
			}
			else if( showhints )
			{
				cc = '';
				if( ptype == 1 ) {
					cell.className='InnerLittle';
					for (h = 0; h < 9; h++)
						if ((g.mask(j,i) & (1 << h)) > 0)
							cc +=  (h + 1);
					cell.innerHTML = cc;
				}
				else {
					cell.className = 'InnerLittleCenter';
					for (h = 0; h < 9; h++) {
						if (h == 3 || h == 6) cc += '</tr><tr>';
						if ((g.mask(j,i) & (1 << h)) > 0)
							cc += '<td>' + (h + 1) + '</td>';
						else
							cc += '<td>&nbsp;</td>';
					}
					cell.innerHTML = '<table class="candtb" id="cl' + i + j +'" style="margin:0 auto"><tr>'+ cc + '</table>';
				}
			}
			if( urlParams.get('jig')==="-5"
			 && ((i>=1 && i<=3 && j>=1 && j<=3)
			  || (i>=1 && i<=3 && j>=5 && j<=7)
			  || (i>=5 && i<=7 && j>=1 && j<=3)
			  || (i>=5 && i<=7 && j>=5 && j<=7))) {
				cell.style.backgroundColor = '#ddd';
			}
		}
	if( urlParams.get('jig')==="-1" ) {
		for(j=0;j<9;j++) {
			t=document.getElementById("a" + j + j);
			t.style.backgroundColor = '#ddd';
			t=document.getElementById("a" + j + (8-j));
			t.style.backgroundColor = '#ddd';
		}
	}
	psize = 1;
	toggle_size();
}
function toggle_size()
{
	let el;
	psize = (psize)?0:1;
	let btnsetsize = document.getElementById("btnsetsize");
	btnsetsize.value = (psize) ? "Larger" : "Smaller";

	for (let j = 0; j < 9; j++) {
		for (let i = 0; i < 9; i++) {
			el = document.getElementById('a' + i + j);
			if( !el ) continue;
			if( psize ) {
				el.className = (el.className==="InnerLittle") ? "InnerLittleSmall" : "InnerBigSmall";
				el.style.borderRight  = (j==8 || j<8 && g.jc(j,i)!=g.jc(j+1,i)) ? "1px solid #000000" : "0px solid #888888";
				el.style.borderLeft   = (j==0 || j>0 && g.jc(j,i)!=g.jc(j-1,i)) ? "1px solid #000000" : "1px solid #888888";
				el.style.borderTop    = (i==0 || i>0 && g.jc(j,i)!=g.jc(j,i-1)) ? "1px solid #000000" : "1px solid #888888";
				el.style.borderBottom = (i==8 || i<8 && g.jc(j,i)!=g.jc(j,i+1)) ? "1px solid #000000" : "0px solid #888888";
			} else {
				el.className = (el.className==="InnerLittleSmall" || el.className==="InnerLittle") ? "InnerLittle" : "InnerBig";
				el.style.borderRight  = (j==8 || j<8 && g.jc(j,i)!=g.jc(j+1,i)) ? "2px solid #000000" : "1px solid #888888";
				el.style.borderLeft   = (j==0 || j>0 && g.jc(j,i)!=g.jc(j-1,i)) ? "2px solid #000000" : "1px solid #888888";
				el.style.borderTop    = (i==0 || i>0 && g.jc(j,i)!=g.jc(j,i-1)) ? "2px solid #000000" : "1px solid #888888";
				el.style.borderBottom = (i==8 || i<8 && g.jc(j,i)!=g.jc(j,i+1)) ? "2px solid #000000" : "1px solid #888888";
			}
			el = document.getElementById('cl' + i + j);
			if( el) el.className = (psize) ? "candtbSmall" : "candtb";
		}
		el = document.getElementById('ch' + j);
		el.style.height = (psize)?"42px":"64px";
	}
}
function rotate_puzzle(direction)
{
	if(!direction) { // left rotate
		g.rotate_left();
	} else { // right rotate
		g.rotate_right();
	}
	populateBoard(false);

	initialize_board();

	firsttime=false;
}
/*----------------------------------------------------------------------*/
/* First of the analyser functions - simply checks for single values	*/
/* which means a number MUST be the solution for that square			*/
/*----------------------------------------------------------------------*/
function check_for_single()
{
	let i,x,y,done=0;
	for( y=0;y<9;y++ )
		for( x=0;x<9;x++ )	// for every square on the board
		{
			let cc = g.c(y, x);
		    if (cc.val) set_square(x, y, cc.val, 1);	// and draw the number
		    for (i = 0; i < 9; i++)	// if the bit array contains only one bit
				if( cc.mask == (1 << i) )
				{
					cc.val=i+1;		// we have a single number and a solution
					cc.mask=0;		// ...wipe the mask
					cc.color=sq_col[2];
					set_square(x,y,cc.val,2);	// and draw the number
					done++;
				}
		}
	return done;
}
function check_for_one_single( y,x )
{
	for(let n=0;n<9;n++) {
		let cc = g.c(y, x);
		if( cc.mask == (1 << n) )
		{
			cc.val=n+1;		// we have a single number and a solution
			cc.mask=0;		// ...wipe the mask
			cc.color=sq_col[2];
			set_square(x,y,cc.val,2);	// and draw the number
			some_changes=true;
			return true;
		}
	}
	return false;
}
function show_candidates()
{
	let x,y,a,b,h;

	/*----------------------------------------------------------------------*/
	/* check the rows, columns, boxes and windows of each square			*/
	/* and to remove any bits for numbers that are found.  					*/
	/*----------------------------------------------------------------------*/
	for( y=0;y<9;y++ )
		for( x=0;x<9;x++ ) { // for every square on the board
			let cc = g.c(y, x);
			if( cc.val )	// if it is an known square...
			{
				h = cc.vbit();
				for( b=0;b<9;b++ )
					for( a=0;a<9;a++ ) {
						let ab = g.c(b, a);
						if( !ab.val && (
							cc.row==ab.row
						 || cc.col==ab.col
						 || cc.box==ab.box
						 || ((puztype==='Sudoku X') && (cc.diag & ab.diag)) )
						 && (ab.mask & h) )
						{
							ab.mask -= h;
							lable_square( b,a,0 );
							some_changes=true;
						}
					}
			}
			// Clear off highlighted eliminations
			if( cc.mask && cc.show ) {
				cc.show=0;
				lable_square(y,x,0);
			}
		}
}
function on_off_color( cellx, celly, n, strong )
{
	let highlight =  (!strong) ?'fshOFF':'fshON';
	let f = document.getElementById("w"+celly+cellx+n);
	if(f) f.className = highlight;
}
function hidden_singles()
{
	let ax=new Array(12);
	let ay=new Array(12);
	let bb,cc,n,c,i,j;
	let y,x,cr,k,sb,s='';

	for(n=0;n<9;n++) 	// .. check each number
		for(bb=0;bb<9;bb+=3)		// Once more, for each box (9 of them 3 by 3 each)
			for(cc=0;cc<9;cc+=3)
			{
				c=0;
				for(i=bb;i<bb+3 && c<9;i++)	// which means looking in each 3 by 3 box
					for(j=cc;j<cc+3 && c<9;j++)
					{
						if( g.val(i,j)===0 && (g.mask(i,j) & (1 << n)) )
						{
							ax[c]=j;	// Store the coordinates
							ay[c++]=i; // and count how many times this happens
						}
						else if( g.val(i,j)==n+1 ) c=9;	// if that number is known we can ignore it
					}
				if( c==1 )	// If we only have one occurance...
				{
					g.c(ay[0],ax[0]).elim|=(1 << n);
					s += digitise(ay[0],ax[0],(1 << n));
				}
			}

	for(n=0;n<9;n++) 	// .. check each number
		for(y=0;y<9;y++)
			for(x=0;x<9;x++)	// for every square on the board...
				if( !g.val(y,x) )	// if it is an unknown square...
				{
					for(n=0;n<9;n++) if( g.mask(y,x) & (1 << n) ) // For all numbers,if the number is a possible
					{
						for( cc=cr=k=0;k<9;k++)
						{
							if( !g.val(y,k) && (g.mask(y,k) & (1 << n)) ) cr++;  // check the row
							if( !g.val(k,x) && (g.mask(k,x) & (1 << n)) ) cc++;  // check the column
						}
						sb = ( g.c(y,x).elim & (1 << n) ) ? " and Box" : "";
						if( cr==1 && cc==1 )
						{
							strat_add("SINGLE: " + cordit(y,x) + " set to " + abetx.charAt(n) + ", unique in Row and Column" + sb);
						}
						else if( cr==1 )
						{
							strat_add("SINGLE: " + cordit(y,x) + " set to " + abetx.charAt(n) + ", unique in Row" + sb);
						}
						else if( cc==1 )
						{
							strat_add("SINGLE: " + cordit(y,x) + " set to " + abetx.charAt(n) + ", unique in Column" + sb);
						}
						else if( g.c(y,x).elim & (1 << n) )
							strat_add("SINGLE: " + cordit(y,x) + " set to " + abetx.charAt(n) + ", unique in Box");

						if( cr==1 || cc==1 ) {
							s += digitise(y,x,(1 << n));
							g.c(y,x).elim|=(1 << n);
						}
					}
				}


	if( puztype==='Sudoku X' ) {
		for(x=0;x<9;x++)	// for every square on the board...
			if( !g.val(x,x) )	// if it is an unknown square...
				for(n=0;n<9 && !g.val(x,x);n++) if( g.mask(x,x) & (1 << n) ) // For all numbers,if the number is a possible
				{
					for( c=k=0;k<9;k++)  // check the row
						if( !g.val(k,k) && (g.mask(k,k) & (1 << n)) ) c++;
					if( c==1 )
					{
						strat_add("SINGLE: " + cordit(x,x) + " set to " + abetx.charAt(n) + ", unique in Diagonal '\\'");
						s += digitise(x,x,(1 << n));
						g.c(x,x).elim|=(1 << n);
					}
				}
		for(x=0;x<9;x++)	// for every square on the board...
			if( !g.val(x,8-x) )	// if it is an unknown square...
				for(n=0;n<9 && !g.val(x,8-x);n++) if( g.mask(x,8-x) & (1 << n) ) // For all numbers,if the number is a possible
				{
					for( c=k=0;k<9;k++)  // check the row
						if( !g.val(k,8-k) && (g.mask(k,8-k) & (1 << n)) ) c++;
					if( c==1 )
					{
						strat_add("SINGLE: " + cordit(x,8-x) + " set to " + abetx.charAt(n) + ", unique in Diagonal '/'");
						s += digitise(x,8-x,(1 << n));
						g.c(x,8-x).elim|=(1 << n);
					}
				}
	}
	for(y=0;y<9;y++)
		for(x=0;x<9;x++)
			if (bit_count(g.c(y, x).elim) == 1) {
				some_changes = true;
				lable_square(y, x, 0);
				g.c(y, x).mask = g.c(y, x).elim;
			}
	grn_blue_color(s,"fshGrn",0);
	for(y=0;y<9;y++)
		for(x=0;x<9;x++)
			if (bit_count(g.c(y, x).elim) > 1) {
				some_changes = true;
				// this will only occur in multi-solution puzzles but work erroring on
				for (n = 0; n < 9; n++)
					if (g.c(y, x).elim & (1 << n)) on_off_color(x, y, n, false);	// hightlight conflicting squares
				strat_add("<span style=\"color:#990000\"><b>Error: cell has two conflicting singles</b></span>");
			}
}
function apply_new_mask( desc,direction,unit,y,x,h )
{
	let c = g.c(y,x);
	let m = (c.mask & h);
	if( direction == " in row " )
		 strat_add(desc + mask2str(h) + direction + abety.charAt(unit) + ": " + cordit(y,x) + " - " + c.maskStr() + " -> " + mask2str(m));
	else strat_add(desc + mask2str(h) + direction + abetx.charAt(unit) + ": " + cordit(y,x) + " - " + c.maskStr() + " -> " + mask2str(m));
	m -= m & c.elim; // have to ensure previous eliminations are not overwritten by a following hidden
	c.show = c.mask - m;
	//g.c(y,x).mask &= h;
	c.elim = c.mask - m;
	//console.log(x + ' ' + y + ':' + mask2str(g.c(y, x).elim) + ' = ' + g.maskStr(y, x) + '-' + mask2str(m));
	return digitise(y,x,m);
}

/*-------------------------------------------------------------------------*/
/* Purpose of hidden_pairs is to look for pairs of numbers, eg 3-7 and 3-7 */
/* mixed up in the same two squares with other numbers - which can be      */
/* eliminated. 															   */
/*-------------------------------------------------------------------------*/
function hidden_pairs()
{
	let x,y,a,b,n,m,i,bb,cc,box=0,h,s='';
	let pos=new Array(9);

	if( puztype==='Sudoku X' ) {// Diagonal 1

		for(n=0;n<9;n++)	// .. check each number
			for(pos[n]=x=0;x<9;x++)	// which means looking in each row/col
				if( !g.val(x,x) && (g.mask(x,x) & (1 << n)) )
					pos[n] += (1 << x);  // ith position of n

		for(n=0;n<8;n++)
			for(m=n+1;m<9;m++)
				if( bit_count(pos[n] | pos[m]) == 2 && pos[n] && pos[m] )
				{
					h=(1 << n) + (1 << m); // this is our pair
					for(i=x=0;x<9;x++)
						if( (g.mask(x,x) & h) && (g.mask(x,x) - (g.mask(x,x) & h)) ) i++;
					if( !i ) continue;
					for(x=0;x<9;x++)
					{
						a=pos[n] & (1 << x);
						b=pos[m] & (1 << x);
						if( a || b )
							if( g.bcmask(x,x) > ((a>0)+(b>0)) ) {
								s += apply_new_mask( "HIDDEN PAIR: ", " in diagonal ",1,x,x,h );
							} else {
								s += digitise(x,x,g.mask(x,x) );
							}
					}
				}

		for(n=0;n<9;n++)	// .. check each number
			for(pos[n]=x=0;x<9;x++)	// which means looking in each row/col
				if( !g.val(x,8-x) && (g.mask(x,8-x) & (1 << n)) )
					pos[n] += (1 << x);  // ith position of n

		for(n=0;n<8;n++)
			for(m=n+1;m<9;m++)
				if( bit_count(pos[n] | pos[m]) == 2 && pos[n] && pos[m] )
				{
					h=(1 << n) + (1 << m); // this is our pair
					for(i=x=0;x<9;x++)
						if( (g.mask(x,8-x) & h) && (g.mask(x,8-x) - (g.mask(x,8-x) & h)) ) i++;
					if( !i ) continue;
					for(x=0;x<9;x++)
					{
						a=pos[n] & (1 << x);
						b=pos[m] & (1 << x);
						if( a || b )
							if( g.bcmask(x,8-x) > ((a>0)+(b>0)) ) {
								s += apply_new_mask( "HIDDEN PAIR: ", " in diagonal ",2,x,8-x,h );
							} else {
								s += digitise(x,8-x,g.mask(x,8-x) );
							}
					}
				}

	}
	for(bb=0;bb<9;bb+=3)		// Once more, for each box (9 of them 3 by 3 each)
		for(cc=0;cc<9;cc+=3)
		{
			for(n=0;n<9;n++)	// .. check each number
			{
				pos[n]=i=0;
				for(y=bb;y<bb+3;y++)	// which means looking in each 3 by 3 box
					for(x=cc;x<cc+3;x++,i++)
						if( !g.val(y,x) && (g.mask(y,x) & (1 << n)) )
							pos[n] += (1 << i);  // ith position of n
			}
			for(n=0;n<8;n++)
				for(m=n+1;m<9;m++)
					if( bit_count(pos[n] | pos[m]) == 2 && pos[n] && pos[m] )
					{
						h=(1 << n) + (1 << m); // this is our pair
						i=0;
						for(y=bb;y<bb+3;y++)	// check if it implies an elimination
							for(x=cc;x<cc+3;x++)
								if( (g.mask(y,x) & h) && (g.mask(y,x) - (g.mask(y,x) & h)) )
									i++;
						if( !i ) continue;
						i=0;
						for(y=bb;y<bb+3;y++)	// which means looking in each 3 by 3 box
							for(x=cc;x<cc+3;x++,i++)
							{
								a=pos[n] & (1 << i);
								b=pos[m] & (1 << i);
								if( a || b ) {
									if( g.bcmask(y,x) > ((a>0)+(b>0)) ) {
										s += apply_new_mask( "HIDDEN PAIR: ", " in box ",box,y,x,h );
									} else {
										s += digitise(y,x,g.mask(y,x) );
									}
								}
							}
					}
			box++;
		}

	/*-------------------------------------------------------------------------*/
	/* Checking in the box will get most hidden pairs, but some are aligned    */
	/* over two box but still on the same row or columns				       */
	/*-------------------------------------------------------------------------*/
	for(y=0;y<9;y++)
	{
		for(n=0;n<9;n++)	// .. check each number
			for(pos[n]=x=0;x<9;x++)	// which means looking in each row/col
				if( !g.val(y,x) && (g.mask(y,x) & (1 << n)) )
					pos[n] += (1 << x);  // ith position of n

	/*	for(n=0;n<8;n++)
			for(m=n+1;m<9;m++)
				if( bit_count(pos[n])==2 && pos[n] == pos[m] )
					for(x=0;x<9;x++)	// which means looking in each row/col
						if( pos[n] & (1 << x) && g.bcmask(y,x) > 2 )
						{
							h=(1 << n) + (1 << m);
							s += apply_new_mask( "HIDDEN PAIR: ", " in row ",y,y,x,h );
						} */


		for(n=0;n<8;n++)
			for(m=n+1;m<9;m++)
				if( bit_count(pos[n] | pos[m]) == 2 && pos[n] && pos[m] )
				{
					h=(1 << n) + (1 << m); // this is our pair
					for(i=x=0;x<9;x++)
						if( (g.mask(y,x) & h) && (g.mask(y,x) - (g.mask(y,x) & h)) ) i++;
					if( !i ) continue;
					for(x=0;x<9;x++)
					{
						a=pos[n] & (1 << x);
						b=pos[m] & (1 << x);
						if( a || b )
							if( g.bcmask(y,x) > ((a>0)+(b>0)) ) {
								s += apply_new_mask( "HIDDEN PAIR: ", " in row ",y,y,x,h );
							} else {
								s += digitise(y,x,g.mask(y,x) );
							}
					}
				}
	}
	for(x=0;x<9;x++)
	{
		for(n=0;n<9;n++)	// .. check each number
			for(pos[n]=y=0;y<9;y++)	// which means looking in each row/col
				if( !g.val(y,x) && (g.mask(y,x) & (1 << n)) )
					pos[n] += (1 << y);  // ith position of n

		for(n=0;n<8;n++)
			for(m=n+1;m<9;m++)
				if( bit_count(pos[n] | pos[m]) == 2 && pos[n] && pos[m] )
				{
					h=(1 << n) + (1 << m); // this is our pair
					for(i=y=0;y<9;y++)
						if( (g.mask(y,x) & h) && (g.mask(y,x) - (g.mask(y,x) & h)) ) i++;
					if( !i ) continue;
					for(y=0;y<9;y++)
					{
						a=pos[n] & (1 << y);
						b=pos[m] & (1 << y);
						if( a || b )
							if( g.bcmask(y,x) > ((a>0)+(b>0)) ) {
								s += apply_new_mask( "HIDDEN PAIR: ", " in col ",x,y,x,h );
							} else {
								s += digitise(y,x,g.mask(y,x) );
							}
					}
				}
	}
	for(y=0;y<9;y++)
		for(x=0;x<9;x++)	// for every square on the board...
			if( g.c(y,x).elim ) {
				lable_square(y,x,g.c(y,x).elim);
				some_changes=true;
			}
	grn_blue_color(s,"fshGrn",0);
	return (s.length>0);
}
function hidden_triples()
{
	let x,y,n,m,p,i,bb,cc,a,b,c,h,box=0,s='';
	let pos=new Array(9);

	if( puztype==='Sudoku X' ) { // Diagonal 1
		for(n=0;n<9;n++)	// .. check each number
			for(pos[n]=x=0;x<9;x++)	// which means looking in each row/col
				if( !g.val(x,x) && (g.mask(x,x) & (1 << n)) )
					pos[n] += (1 << x);  // ith position of n

		for(n=0;n<7;n++)
			for(m=n+1;m<8;m++)
				for(p=m+1;p<9;p++)
					if( bit_count(pos[n] | pos[m] | pos[p]) == 3 && pos[n] && pos[m] && pos[p] ) {
						h=(1 << n) + (1 << m) + (1 << p);
						for(i=x=0;x<9;x++)
							if( (g.mask(x,x) & h) && (g.mask(x,x) - (g.mask(x,x) & h)) ) i++;
						if( !i ) continue;
						for(x=0;x<9;x++) {
							a=pos[n] & (1 << x);
							b=pos[m] & (1 << x);
							c=pos[p] & (1 << x);
							if( a || b || c) {
								if( g.bcmask(x,x) > ((a>0)+(b>0)+(c>0)) ) {
									s += apply_new_mask( "HIDDEN TRIPLE: ", " in diagonal ",1,x,x,h );
								}
								else {
									s += digitise(x,x,g.mask(x,x) );
								}
							}
						}
					}

		// Diagonal 2
		for(n=0;n<9;n++)	// .. check each number
			for(pos[n]=x=0;x<9;x++)	// which means looking in each row/col
				if( !g.val(x,8-x) && (g.mask(x,8-x) & (1 << n)) )
					pos[n] += (1 << x);  // ith position of n

		for(n=0;n<7;n++)
			for(m=n+1;m<8;m++)
				for(p=m+1;p<9;p++)
					if( bit_count(pos[n] | pos[m] | pos[p]) == 3 && pos[n] && pos[m] && pos[p] ) {
						h=(1 << n) + (1 << m) + (1 << p);
						for(i=x=0;x<9;x++)
							if( (g.mask(x,8-x) & h) && (g.mask(x,8-x) - (g.mask(x,8-x) & h)) ) i++;
						if( !i ) continue;
						for(x=0;x<9;x++) {
							a=pos[n] & (1 << x);
							b=pos[m] & (1 << x);
							c=pos[p] & (1 << x);
							if( a || b || c ) {
								if( g.bcmask(x,8-x) > ((a>0)+(b>0)+(c>0)) ) {
									s += apply_new_mask( "HIDDEN TRIPLE: ", " in diagonal ",2,x,8-x,h );
								}
								else {
									s += digitise(x,8-x,g.mask(x,8-x) );
								}
							}
						}
					}
	}
	for(bb=0;bb<9;bb+=3)		// Once more, for each box (9 of them 3 by 3 each)
		for(cc=0;cc<9;cc+=3)
		{
			for(n=0;n<9;n++)	// .. check each number
			{
				pos[n]=i=0;
				for(y=bb;y<bb+3;y++)	// which means looking in each 3 by 3 box
					for(x=cc;x<cc+3;x++,i++)
						if( !g.val(y,x) && (g.mask(y,x) & (1 << n)) )
							pos[n] += (1 << i);  // ith position of n
			}
			for(n=0;n<7;n++)
				for(m=n+1;m<8;m++)
					for(p=m+1;p<9;p++)
						if( bit_count(pos[n] | pos[m] | pos[p]) == 3 && pos[n] && pos[m] && pos[p] )
						{
							h=(1 << n) + (1 << m) + (1 << p); // this is our triple
							i=0;
							for(y=bb;y<bb+3;y++)	// check if it implies an elimination
								for(x=cc;x<cc+3;x++)
									if( (g.mask(y,x) & h) && (g.mask(y,x) - (g.mask(y,x) & h)) )
										i++;
							if( !i ) continue;
							i=0;
							for(y=bb;y<bb+3;y++)	// which means looking in each 3 by 3 box
								for(x=cc;x<cc+3;x++,i++)
								{
									a=pos[n] & (1 << i);
									b=pos[m] & (1 << i);
									c=pos[p] & (1 << i);
									if( a || b || c ) {
										if( g.bcmask(y,x) > ((a>0)+(b>0)+(c>0)) ) {
											s += apply_new_mask( "HIDDEN TRIPLE: ", " in box ",box,y,x,h );
										} else {
											s += digitise(y,x,g.mask(y,x) );
										}
									}
								}
						}
			box++;
		}

	/*-------------------------------------------------------------------------*/
	/* Checking in the box will get most hidden pairs, but some are aligned    */
	/* over two box but still on the same row or columns				       */
	/*-------------------------------------------------------------------------*/
	for(y=0;y<9;y++)
	{
		for(n=0;n<9;n++)	// .. check each number
			for(pos[n]=x=0;x<9;x++)	// which means looking in each row/col
				if( !g.val(y,x) && (g.mask(y,x) & (1 << n)) )
					pos[n] += (1 << x);  // ith position of n

		for(n=0;n<7;n++)
			for(m=n+1;m<8;m++)
				for(p=m+1;p<9;p++)
					if( bit_count(pos[n] | pos[m] | pos[p]) == 3 && pos[n] && pos[m] && pos[p] )
					{
						h=(1 << n) + (1 << m) + (1 << p); // this is our triple
						for(i=x=0;x<9;x++)
							if( (g.mask(y,x) & h) && (g.mask(y,x) - (g.mask(y,x) & h)) ) i++;
						if( !i ) continue;
						for(x=0;x<9;x++)
						{
							a=pos[n] & (1 << x);
							b=pos[m] & (1 << x);
							c=pos[p] & (1 << x);
						//	if( y==4 ) alert( x + ' abc: ' + a + ' ' + b + ' ' + c + ' nmp: ' + n + ' ' + m + ' ' + p );
							if( a || b || c )
								if( g.bcmask(y,x) > ((a>0)+(b>0)+(c>0)) ) {
									s += apply_new_mask( "HIDDEN TRIPLE: ", " in row ",y,y,x,h );
								} else {
									s += digitise(y,x,g.mask(y,x) );
								}
						}
					}
	}
	for(x=0;x<9;x++)
	{
		for(n=0;n<9;n++)	// .. check each number
			for(pos[n]=y=0;y<9;y++)	// which means looking in each row/col
				if( !g.val(y,x) && (g.mask(y,x) & (1 << n)) )
					pos[n] += (1 << y);  // ith position of n

		for(n=0;n<7;n++)
			for(m=n+1;m<8;m++)
				for(p=m+1;p<9;p++)
					if( bit_count(pos[n] | pos[m] | pos[p]) == 3 && pos[n] && pos[m] && pos[p] )
					{
						h=(1 << n) + (1 << m) + (1 << p); // this is our triple
						for(i=y=0;y<9;y++)
							if( (g.mask(y,x) & h) && (g.mask(y,x) - (g.mask(y,x) & h)) ) i++;
						if( !i ) continue;
						for(y=0;y<9;y++)
						{
							a=pos[n] & (1 << y);
							b=pos[m] & (1 << y);
							c=pos[p] & (1 << y);
							if( a || b || c )
								if( g.bcmask(y,x) > ((a>0)+(b>0)+(c>0)) ) {
									s += apply_new_mask( "HIDDEN TRIPLE: ", " in col ",x,y,x,h );
								} else {
									s += digitise(y,x,g.mask(y,x) );
								}
						}
					}
	}
	for(y=0;y<9;y++)
		for(x=0;x<9;x++)
			if( g.c(y,x).elim ) {
				lable_square(y,x,g.c(y,x).elim);
				some_changes=true;
			}
	grn_blue_color(s,"fshGrn",0);
}
function naked_pairs()
{
	let x,y,bb,cc,n,m,i,j,k,a,b,x1,x2,h,cn,s='';
	let mbox=new Array(9);
	let cnt=new Array(9);

	if( puztype==='Sudoku X' ) { // Diagonal 1
		for(x1=0;x1<8;x1++)
			for(x2=x1+1;x2<9;x2++) {
				// This block checks diagonal 1 the pair resides in...
				if( g.bcmask(x1,x1)==2 && g.mask(x1,x1) == g.mask(x2,x2) )
					for(i=0;i<9;i++)
					{
						h=g.mask(i,i) & g.mask(x1,x1);
						if( i!=x1 && i!=x2 && !g.val(i,i) && h )
						{
							strat_add("NAKED PAIR (Diag 1): " + cordit(x1,x1) + "/" + cordit(x2,x2) + " removes " + mask2str(g.mask(i,i) & h) + " from " + cordit(i,i));
							//lable_square( i,i,h );
							g.c(i,i).elim |= h;
							s += digitise(x1,x1,g.mask(x1,x1)) + digitise(x2,x2,g.mask(x2,x2));
						}
					}
			}
		// Diagonal 2
		for(x1=0;x1<8;x1++)
			for(x2=x1+1;x2<9;x2++) {
				// This block checks diagonal 2 the pair resides in...
				if( g.bcmask(x1,8-x1)==2 && g.mask(x1,8-x1) == g.mask(x2,8-x2) )
					for(i=0;i<9;i++)
					{
						h=g.mask(i,8-i) & g.mask(x1,8-x1);
						if( i!=x1 && i!=x2 && !g.val(i,8-i) && h )
						{
							strat_add("NAKED PAIR (Diag 2): " + cordit(x1,8-x1) + "/" + cordit(x2,8-x2) + " removes " + mask2str(g.mask(i,8-i) & h) + " from " + cordit(i,8-i));
							//lable_square( i,8-i,h );
							g.c(i,8-i).elim |= h;
							s += digitise(x1,8-x1,g.mask(x1,8-x1)) + digitise(x2,8-x2,g.mask(x2,8-x2));
						}
					}
			}
	}
	/*----------------------------------------------------------------------*/
	/* Purpose of this pair test is to look for pairs of numbers,			*/
	/* eg 3-7 and 3-7 in the same box. Since both numbers MUST be on both   */
	/* cells they can be eliminated from the rest of the box				*/
	/*----------------------------------------------------------------------*/
	for(bb=0;bb<9;bb+=3)		// Once more, for each box (9 of them 3 by 3 each)
		for(cc=0;cc<9;cc+=3)
		{
			k=0;
			for(i=bb;i<bb+3;i++)	// put the box in a 1D array for ease of use
				for(j=cc;j<cc+3;j++)
				{
					mbox[k]=g.mask(i,j);
					cnt[k]=g.bcmask(i,j);
					cordX[k]=j;
					cordY[k++]=i;
				}
			for(a=0;a<8;a++)	// .. check each pair in the 1D box array
				for(b=a+1;b<9;b++)
				{
					if( cnt[a]==2 && mbox[a] == mbox[b] )  // If same 2 numbers in the same 2 squares
					{
						for(m=0;m<9;m++)	// for all squares in the box
							for(n=0;n<9;n++) // for all numbers
							{
								if( m!=a && m!=b && (mbox[a] & (1 << n)) && (mbox[m] & (1 << n)) )
								{
								//	alert("here n=" + n + " m=" + m + " a=" + a + " mbox[a]=" + mbox[a] + " cnt[m]=" + cnt[m]);
									cn=abetx.charAt(n);
									strat_add("NAKED PAIR (Box): " + cordit(cordY[a],cordX[a]) + "/" + cordit(cordY[b],cordX[b]) + " removes " + cn + " from " + cordit(cordY[m],cordX[m]));
									mbox[m] -= (1 << n); // remove that number
									//lable_square( cordY[m],cordX[m],(1 << n) );
									g.c(cordY[m],cordX[m]).elim |= (1 << n);
									s += digitise(cordY[a],cordX[a],mbox[a]) + digitise(cordY[b],cordX[b],mbox[b]);
								}
							}
					}
				}
		}

	/*----------------------------------------------------------------------*/
	/* Purpose of pair_test2 is to look for pairs of numbers, eg 3-7 and 3-7 */
	/* in the same row/col. Since both numbers MUST be on both cells they 	*/
	/* can be elininated from the rest of the ROW or COLUMN they are		*/
	/* aligned with. How cool is that?										*/
	/*----------------------------------------------------------------------*/
	for(y=0;y<9;y++)
		for(x1=0;x1<8;x1++)	// For every square...
			for(x2=x1+1;x2<9;x2++)
			{
				// This block checks the ROW the pair resides in...
				if( g.bcmask(y,x1)==2 && g.mask(y,x1) == g.mask(y,x2) )
					for(i=0;i<9;i++)
					{
						h=(g.mask(y,i) & g.mask(y,x1));
						if( i!=x1 && i!=x2 && !g.val(y,i) && h )
						{
							strat_add("NAKED PAIR (Row): " + cordit(y,x1) + "/" + cordit(y,x2) + " removes " + mask2str(g.mask(y,i) & h) + " from " + cordit(y,i));
							g.c(y,i).elim |= h;
							s += digitise(y,x1,g.mask(y,x1)) + digitise(y,x2,g.mask(y,x2));
						}
					}

				// This block checks the COLUMN the pair resides in...
				if( g.bcmask(x1,y)==2 && g.mask(x1,y) == g.mask(x2,y) )
					for(i=0;i<9;i++)
					{
						h=(g.mask(i,y) & g.mask(x1,y));
						if( i!=x1 && i!=x2 && !g.val(i,y) && h )
						{
							strat_add("NAKED PAIR (Col): " + cordit(x1,y) + "/" + cordit(x2,y) + " removes " + mask2str(g.mask(i,y) & h) + " from " + cordit(i,y));
							g.c(i,y).elim |= h;
							s += digitise(x1,y,g.mask(x1,y)) + digitise(x2,y,g.mask(x2,y));
						}
					}
			}
	for(y=0;y<9;y++)
		for(x=0;x<9;x++)	// for every square on the board...
			if( g.c(y,x).elim ) {
				lable_square(y,x,g.c(y,x).elim);
				some_changes=true;
			}
	grn_blue_color(s,"fshGrn",0);
	return (s.length>0);
}
function naked_triples()
{
	let bb,cc,i,j,k,x,y,x1,x2,x3,h,off,s='';
	let mbox=new Array(9);
	let cnt=new Array(9);

	if( puztype==='Sudoku X' ) { // Diagonal 1
		for(x1=0;x1<7;x1++)
			for(x2=x1+1;x2<8;x2++)
				for(x3=x2+1;x3<9;x3++)
					// This block checks diagonal 1 the triple resides in...
					if( g.bcmask(x1,x1)>1 && g.bcmask(x2,x2)>1 && g.bcmask(x3,x3)>1 ) {
						h=g.mask(x1,x1) | g.mask(x2,x2) | g.mask(x3,x3);
						if( bit_count(h)==3 )
							for(i=0;i<9;i++)
							{
								off=(g.mask(i,i) & h);
								if( i!=x1 && i!=x2 && i!=x3 && off )
								{
									strat_add("NAKED TRIPLE (Diag 1): " + cordit(x1,x1) + "/" + cordit(x2,x2) + "/" + cordit(x3,x3) + " removes " + mask2str(off) + " from " + cordit(i,i));
									s += digitise(x1,x1,g.mask(x1,x1)) + digitise(x2,x2,g.mask(x2,x2)) + digitise(x3,x3,g.mask(x2,x2));
									g.c(i,i).elim |= off;
								}
							}
					}
		for(x1=0;x1<7;x1++)
			for(x2=x1+1;x2<8;x2++)
				for(x3=x2+1;x3<9;x3++)
					// This block checks diagonal 2 the triple resides in...
					if( g.bcmask(x1,8-x1)>1 && g.bcmask(x2,8-x2)>1 && g.bcmask(x3,8-x3)>1 ) {
						h=g.mask(x1,8-x1) | g.mask(x2,8-x2) | g.mask(x3,8-x3);
						if( bit_count(h)==3 )
							for(i=0;i<9;i++)
							{
								off=(g.mask(i,8-i) & h);
								if( i!=x1 && i!=x2 && i!=x3 && off )
								{
									strat_add("NAKED TRIPLE (Diag 2): " + cordit(x1,8-x1) + "/" + cordit(x2,8-x2) + "/" + cordit(x3,8-x3) + " removes " + mask2str(off) + " from " + cordit(i,8-i));
									s += digitise(x1,8-x1,g.mask(x1,8-x1)) + digitise(x2,8-x2,g.mask(x2,8-x2)) + digitise(x3,8-x3,g.mask(x3,8-x3));
									g.c(i,8-i).elim |= off;
								}
							}
					}
	}
	// LOOK FOR TRIPLES
	for(y=0;y<9;y++)
		for(x1=0;x1<7;x1++)	// For each triple
			for(x2=x1+1;x2<8;x2++)
				for(x3=x2+1;x3<9;x3++)
				{
					// This block checks the ROW the triple resides in...
					if( g.bcmask(y,x1)>1 && g.bcmask(y,x2)>1 && g.bcmask(y,x3)>1 )
					{
						h=g.mask(y,x1) | g.mask(y,x2) | g.mask(y,x3);
						if( bit_count(h)==3 )
							for(i=0;i<9;i++)
							{
								off=(g.mask(y,i) & h);
								if( i!=x1 && i!=x2 && i!=x3 && off )
								{
									strat_add("NAKED TRIPLE (Row): " + cordit(y,x1) + "/" + cordit(y,x2) + "/" + cordit(y,x3) + " removes " + mask2str(off) + " from " + cordit(y,i));
									s += digitise(y,x1,g.mask(y,x1)) + digitise(y,x2,g.mask(y,x2)) + digitise(y,x3,g.mask(y,x3));
									g.c(y,i).elim |= off;
								}
							}
					}
					// This block checks the COLUMN the triple resides in...
					if( g.mask(x1,y)>1 && g.bcmask(x2,y)>1 && g.bcmask(x3,y)>1 )
					{
						h=g.mask(x1,y) | g.mask(x2,y) | g.mask(x3,y);
						if( bit_count(h)==3 )
							for(i=0;i<9;i++)
							{
								off=(g.mask(i,y) & h);
								if( i!=x1 && i!=x2 && i!=x3 && off )
								{
									strat_add("NAKED TRIPLE (Col): " + cordit(x1,y) + "/" + cordit(x2,y) + "/" + cordit(x3,y) + " removes " + mask2str(off) + " from " + cordit(i,y));
									s += digitise(x1,y,g.mask(x1,y)) + digitise(x2,y,g.mask(x2,y))+ digitise(x3,y,g.mask(x3,y));
									g.c(i,y).elim |= off;
								}
							}
					}
				}
	/*----------------------------------------------------------------------*/
	// This block checks the BOX the triple resides in...
	/*----------------------------------------------------------------------*/
	for(bb=0;bb<9;bb+=3)		// Once more, for each box (9 of them 3 by 3 each)
		for(cc=0;cc<9;cc+=3)
		{
			k=0;
			for(i=bb;i<bb+3;i++)	// put the box in a 1D array for ease of use
				for(j=cc;j<cc+3;j++)
				{
					mbox[k]=g.mask(i,j);
					cnt[k]=bit_count(g.mask(i,j));
					cordX[k]=j;
					cordY[k++]=i;
				}
			for(x1=0;x1<7;x1++)	// For each triple
				for(x2=x1+1;x2<8;x2++)
					for(x3=x2+1;x3<9;x3++)
					{
						if( cnt[x1]>1 && cnt[x2]>1 && cnt[x3]>1 )
						{
							h=mbox[x1] | mbox[x2] | mbox[x3];
							if( bit_count(h)==3 )
								for(i=0;i<9;i++)
								{
									off=(mbox[i] & h);
									if( i!=x1 && i!=x2 && i!=x3 && off )
									{
										strat_add("NAKED TRIPLE (Box): " + cordit(cordY[x1],cordX[x1]) + "/" + cordit(cordY[x2],cordX[x2]) + "/" + cordit(cordY[x3],cordX[x3]) + " removes " + mask2str(off) + " from " + cordit(cordY[i],cordX[i]));
										s += digitise(cordY[x1],cordX[x1],mbox[x1]) + digitise(cordY[x2],cordX[x2],mbox[x2]) + digitise(cordY[x3],cordX[x3],mbox[x3]);
										mbox[i] -= off; // remove that number
										g.c(cordY[i],cordX[i]).elim |= off;
									}
								}
						}
					}
		}
	for(y=0;y<9;y++)
		for(x=0;x<9;x++)	// for every square on the board...
			if( g.c(y,x).elim ) {
				lable_square(y,x,g.c(y,x).elim);
				some_changes=true;
			}
	grn_blue_color(s,"fshGrn",0);
}
/*----------------------------------------------------------------------*/
/* Gurths Symmetrical Placement Thoery									*/
/*----------------------------------------------------------------------*/
function detect_gurth(showint)
{
	let x,y,a,b;
	if( puztype==='Sudoku X' ) return;
	if(showint==1)
	{
		for( let rots = 1; rots <= 5; rots++ )
		{
			let goodenough = true;
			for(y=0;y<9;y++) gurthmap[y] = 0;
			for(y=0;y<9;y++)
				for(x=0;x<9;x++)
				{
					a = g.val(y,x);
					switch(rots) {
						// top-right to bottom left diagonal
					case 1 : b = g.val(9-1-x,9-1-y); break;
						// top-left to bottom right diagonal
					case 2 : b = g.val(x,y); break;
						// Rotate 180 degrees
					case 3 : b = g.val(9-1-y,9-1-x); break;
						// 90 degree clockwise rotation
					case 4 : b = g.val(x,9-1-y); break;
						// 90 degree anti-clockwise rotation
					case 5 : b = g.val(9-1-x,y); break;
					}
					if( a && b ) { // opposites both have clues
						if( gurthmap[a-1]!=0 && gurthmap[a-1]!=b ) {
							goodenough = false;
						}
						else {
							gurthmap[a-1] = b;
						}
					} else if( a || b ) goodenough = false; // clue mirrored by empty cell
				}

			for(y=0;y<9;y++) if( gurthmap[y]==0 ) goodenough = false;

			if( goodenough ) {
				let d = document.getElementById("quickhelp");
				if( savehelp=='' ) savehelp = d.innerHTML;
				d.innerHTML = '<div style="color:#77ff77;font-size:12pt"><b>Clue Symmetry Detected!<br>Gurth\'s Theorem Applies</b></div>';
				switch(rots) {
				case 1 : d.innerHTML += 'This puzzle has a symmetry down the diagonal line from top-right <span class="hy">A9</span> to bottom left <span class="hy">J1</span>.<br>'; break;
				case 2 : d.innerHTML += 'This puzzle has a symmetry down the diagonal line from top-left <span class="hy">A1</span> to bottom right <span class="hy">J9</span>.<br>'; break;
				case 3 : d.innerHTML += 'This puzzle has a symmetry when rotated 180 degrees.<br>'; break;
				case 4 : d.innerHTML += 'This puzzle has a symmetry when rotated 90 clockwise.<br>'; break;
				case 5 : d.innerHTML += 'This puzzle has a symmetry when rotated 90 anti-clockwise.<br>'; break;
				}
				d.innerHTML += 'This means that every number maps exclusively onto only one other number, in this case<ul>';
				for(y=1;y<=9;y++) d.innerHTML += '<li>' + y + ' maps to ' + gurthmap[y-1];
				d.innerHTML += '</ul><br><a href="/gurths_theorem" target="_gurth">Gurth\'s Symmetrical Placement Theorem</a> says that when the clues can be mapped one to one via one of five possible symmetries, the the entire solution will be symmetrical as well. This should make solving this puzzle much easier.';
				UsesGurth = rots;
				return rots;
			}
		}
	}
	if( savehelp!='' ) {
		document.getElementById("quickhelp").innerHTML = savehelp;
		savehelp = '';
	}
}

/*----------------------------------------------------------------------*/
/* Function to check for conflicts with the rules						*/
/*----------------------------------------------------------------------*/
function sanity_check(redraw)
{
	let x,y,a,b,failed=0;

	for(y=0;y<9;y++)	// for every square on the board...
		for(x=0;x<9;x++) {
			let cc = g.c(y,x);
			if( cc.val===0 && cc.mask===0 )	// if it is an known square...
			{
				err_square(x,y,0);	// hightlight conflicting squares
				return 1;
			}
			else if (redraw && cc.val)
				set_square(x, y, cc.val, 1);
		}

	for( y=0;y<9;y++ )
		for( x=0;x<9;x++ )	// for every square on the board
			if( g.val(y,x) )	// if it is an known square...
				for( b=0;b<9;b++ )
					for( a=0;a<9;a++ ) {
						let cc = g.c(y,x);
						let ab = g.c(b,a);
						if( !(y==b && x==a)
						 && cc.val==ab.val
						 && (cc.row==ab.row
						  || cc.col==ab.col
						  || cc.box==ab.box
						  || cc.diag & ab.diag )
						  )
						{
							err_square(x,y,cc.val);	// hightlight conflicting squares
							err_square(a,b,ab.val);
							failed++;
						}
					}
	return failed;
}
/* Function to reset the board to its normal blue background */
function blue_board()
{
	let x,y,t,done=0;
	for(y=0;y<9;y++)		// Redraw the board to clear any user highlighting
		for(x=0;x<9;x++)
		{
			let cc = g.c(y,x);
			if( some_changes===false ) t=document.getElementById("a"+y+x);
			if( some_changes===false ) {
				if( t.style.backgroundColor!=cc.jbcol() ) {
					t.style.backgroundColor =cc.jbcol();
					t.style.color = cc.color;
				}
				cc.backgroundColor=cc.jbcol();
			}
			if( cc.val>0 ) done++;
		}
	document.getElementById("chkSB").checked = false;
	return done;
}
function anyNRC() {
	//	((document.getElementById("NRCmode").checked) ? 2 : 0)
/*	const urlParams = new URLSearchParams(window.location.search);
	let nrc = (urlParams.get('nrc') == '1');
	return (nrc) ? 2 : 0; */
	return 0;
}
function grade_sudoku(fullreport)
{
	let done=0,x,y;
	let s='',st='';

    done = blue_board();

	if( !enough_digits() ) return;

    if (puztype==='Sudoku' && done < 16) { alert('Too few clues/numbers, normal Sudoku must have 17 clues minimum.'); return; }
    if (puztype==='Sudoku X' && done < 12) { alert('Too few clues/numbers, Sudoku X must have 12 clues minimum.'); return; }

	if( sanity_check(true)>0 ) {
		strat_add('<div class="res_error">Oops - error detected</div>');
		clear_results = true;
	}
	else if( done == 81 )	// If the number of solutions=81, we're all done
	{
		alert("The puzzle is complete");
	}
	else
	{
		for(y=0;y<9;y++)
			for(x=0;x<9;x++)
				s = s + g.val(y, x);

		document.getElementById('pboard5').className = 'GButton';
		document.getElementById("pboard5").removeEventListener('click', grade_sudoku1);
		//document.getElementById("pboard5").onclick=null;

		document.getElementById('pboard4').className = 'GButton';
		document.getElementById("pboard4").removeEventListener('click', grade_sudoku0);
		//document.getElementById("pboard4").onclick=null;
		setTimeout(restore_sp_button, 6000);

		if( WebSudoku ) {
			let res = WebSudoku.Solutions(puzTypeNum() + ',' + s);
			if( res.indexOf('<b>1</b>')== -1 ) {
				alert("This puzzle does not have one solution, cannot proceed with Solve Path");
				serverbusy=false;
				return;
			}
		}
		for( x=3;x<strat_list.length;x++)
			if( document.getElementById("CB"+strat_list[x]) )
				if( document.getElementById("CB"+strat_list[x]).checked===false && strat_list[x]!="ERT")
					st+=strat_list[x];

		if (puztype==='Sudoku' && document.getElementById("TogAICUR").checked === false) st += 'AUR';

		if (fullreport) document.getElementById('solvepathdiv').innerHTML = '<div style="font-size:14pt">Please wait....</div>';
		if( fullreport ) writeToResults('Requesting Solve Path...');
		if( !fullreport ) writeToResults('Requesting Grade...');

		serverbusy=true;
		let frm = document.forms.servsolv;
		frm.elements['coordmode'].value = coordmode;
		frm.elements['gors'].value = 1;
		frm.elements['strat'].value = 'XWG';
		frm.elements['stratmask'].value = st;
		frm.elements['mapno'].value = puzTypeNum();
		frm.elements['curchain'].value = 1;
		frm.elements['fullreport'].value = (fullreport==1)?1:0;
		frm.elements['board'].value = string_grid();
		frm.submit();
	}
}
function post_to_form(cur_strat, thisCurChain) {
	let x,st='';
	for( x=3;x<strat_list.length;x++) if( document.getElementById("CB"+strat_list[x]) )
		if( document.getElementById("CB"+strat_list[x]).checked===false )
		{
			st+=strat_list[x];
		}
	if (puztype==='Sudoku' && document.getElementById("TogAICUR").checked === false) st += 'AUR';
	let frm = document.forms.servsolv;
	frm.elements['coordmode'].value = coordmode + anyNRC();
	frm.elements['gors'].value = 0;
	frm.elements['strat'].value = cur_strat;
	frm.elements['stratmask'].value = st;
	frm.elements['mapno'].value = puzTypeNum();
	frm.elements['curchain'].value = thisCurChain;
	frm.elements['fullreport'].value = 0;
	frm.elements['board'].value = string_grid();
	frm.submit();
}
function cycle_chains(dir) {
	let i,j;
	if (dir > 0)
		curChain = (curChain < manyChains) ? curChain + 1 : 1;
	else
		curChain = (curChain > 1) ? curChain - 1 : manyChains;
	display_chain_cycle();
	some_changes = false;
	blue_board();
	for (j = 0; j < 9; j++)
		for (i = 0; i < 9; i++) {
			if (g.c(j, i).last > 0) {
				g.c(j, i).show = g.c(j, i).val = 0;
				g.c(j, i).orig = g.c(j, i).mask = g.c(j, i).last;
				lable_square(j, i, 0);
				document.forms.DataEntry.elements["D" + j + i].value = '';
			}
		}
	if( stage>5 )
		post_to_form(strat_list[stage-5], curChain);
}
function take_step()
{
	let i,j,done=0,found=0,x,y,ds;
	done=blue_board();
//	if( stage>0 && done > 0 && !block_board() ) return;

/*	if( done === 0 )	// If the number of solutions=81, we're all done
	{
		alert("Put some numbers in the small board first.");
		return;
	}
	else */
	if( done === 81 )	// If the number of solutions=81, we're all done
	{
		if( sanity_check(true)>0 )
			 alert("Oops. Not a valid " + puztype + " solution");
		else alert("That's it! All done");
		return;
	}
	//if( stage === 0 ) some_changes=false;

	if( !some_changes )
	{
		for(x=0;x<9;x++)
			for(y=0;y<9;y++) g.c(x,y).last=g.mask(x,y);
		laststage=stage;
	}
//	alert('before: ' + stage + ' ' + some_changes);
	if( some_changes ) stage=0;
	else
	{
		if( stage==MAX_STRAT ) stage=1;
		else if( stage<2 ) stage++;
		else stage = 2;
	}

	if( stage == 0 )
	{
		save_unchecked();

		found=check_for_single();
		document.getElementById("R0").innerHTML=(found)? '<font color=#00ff00><b>' + found + '</b></font>' : '<font color=#ff0000><b>0</b></font>';
		some_changes=false;
	}
	else
	{
		if (stage == 1) {
			reset_yes_no(strat_list, 2); jg.clear(); clear_on_off_color(); manyChains = 0; display_chain_cycle();
		}

		if (sanity_check(true)) {
			strat_add('<div class="res_error">Oops - error detected</div>');
			clear_results = true;
			return;
		}
		//if( !enough_digits() ) return;

		if( stage == 1  ) {
			show_candidates();
			if( some_changes ) save_board(cookieauto);
			detect_gurth(1);
		}
		if( stage == 2  ) {

			g.prepareElim();
			clear_results = true;
			hidden_singles();

			if( !some_changes  ) document.getElementById("R2").innerHTML='<font color=#ff0000><b>No</b></font>';

		/*	if( !some_changes ) { stage=3; if( !naked_pairs() ) naked_triples(); }
			if( !some_changes  ) document.getElementById("R3").innerHTML='<font color=#ff0000><b>No</b></font>';

			if( !some_changes ) { stage=4; if( !hidden_pairs() ) hidden_triples(); }
			if( !some_changes  ) document.getElementById("R4").innerHTML='<font color=#ff0000><b>No</b></font>';
			*/
			if( !some_changes ) {

				stage=2;
				document.getElementById("takestep").onclick=null;
				document.getElementById("takestep").className = 'GButton';
				document.getElementById("RPAI").innerHTML='<font color=#ffff00><b>Wait</b></font>';
				curChain = 1;
				post_to_form('PAI',1);  /*quads*/
				backgroundList('PAI');
				setKnown();

				//if( stage == 8  ) post_to_form('PPR');  /*pointing_pairs*/
				//if( stage == 8  ) /*LBR*/	post_to_form('LBR');
				//if( stage == 7  ) pointing_pairs();
				//if( stage == 8  ) line_box_reduction();
				//if( stage == 9  ) post_to_form('XWG');
				return;
			}
			save_board(cookieauto);
		}

		ds = document.getElementById("R" + stage);
		if( ds )
			ds.innerHTML=(some_changes)? '<font color=#00ff00><b>Yes</b></font>' : '<font color=#ff0000><b>No</b></font>';
		else
			alert('take_step: no row called R' + stage);

		for(x=0;x<9;x++)
			for(y=0;y<9;y++) g.c(x,y).orig=g.mask(x,y);
	}
	if( sanity_check(false) )
		strat_add('<div class="res_error">Oops - error detected</div>');

	backgroundList((stage<=2)?''+stage:strat_list[stage]);
	setKnown();
	document.getElementById("backstep").className='SButton';
	if( stage==MAX_STRAT-1 && some_changes == false )
		alert("No more known logical steps to take - you have to enter a number somewhere and then click 'Take Step'");
}
function fired_event()
{
	let i,s,c,y,x,n,stratname;
	let doc,d2;

	if( !document.ifrm )
		 doc = document.getElementById("ifrm").contentDocument;
	else doc = document.ifrm.document;
	let d = doc.getElementById("kbin");
	if( !d ) return;
	s = d.value;
	stratname = doc.getElementById("nstage").value;
	let t = document.getElementById("TestT");

	if( stratname!="NO" )
	{
		stage = get_stage(strat_list,stratname,5);

		if( jg ) {
			jg.clear();

			d = doc.getElementById("chain1");
			if( d )
				if( stratname == "POM" )
					 parse_pom_set( d.value, s.charAt(2) );
				else parsemychain( d.value, "#0000ff" );

			d = doc.getElementById("chain2");
			if( d ) parsemychain( d.value, "#990099" );

			d = doc.getElementById("chain3");
			if( d ) parsemychain( d.value, "#ff0000" );

			d = doc.getElementById("chain4");
			if( d ) parsemychain( d.value, "#009900" );

			//if( stratname=="SCN" ) displaychainlinks( s );
			if( stratname=="SCN" ) {
				show_chains( s.charAt(2)*1 );
			}
			if( stratname=="BUG" ) {
				document.getElementById("chkSB").checked=true;
				show_bivalue();
			}

			jg.paint();
		}
		d2 = doc.getElementById("cols1");
		if( d2 ) grn_blue_color(d2.value,"fshGrn",0);
		d2 = doc.getElementById("cols2");
		if( d2 ) grn_blue_color(d2.value,"fshBlu",0);
		d2 = doc.getElementById("cols3");
		if( d2 ) grn_blue_color(d2.value,"fshOFF",0);

		if( s.length ) grn_blue_color(s,"fsh",1);

		for(i=0;i<s.length;i+=3)
		{
			c = s.charAt(i);
			if( c == '{' ) break;
			y = s.charAt(i)-1;
			x = s.charAt(i+1)-1;
			n = s.charAt(i+2)-1;

			g.c(y,x).mask -= (1 << n);
			g.c(y,x).show += (1 << n);
		//	lable_square(y,x,(1 << n));
			some_changes = true;
		}

		for(y=0;y<9;y++)
			for(x=0;x<9;x++)
			{
				switch( s.charAt(y*9+x+i+1) ){
				case '1' : document.getElementById("a"+y+x).style.backgroundColor='#ffff55'; g.c(y,x).backgroundColor='#ffff55'; break; // YELLOW
				case '2' : document.getElementById("a"+y+x).style.backgroundColor='#eeaa55'; g.c(y,x).backgroundColor='#eeaa55'; break; // ORANGE
				case '3' : document.getElementById("a"+y+x).style.backgroundColor='#55ff55'; g.c(y,x).backgroundColor='#55ff55'; break; // GREEN
				case '4' : document.getElementById("a"+y+x).style.backgroundColor='#55ffcc'; g.c(y,x).backgroundColor='#55ffcc'; break; // CYAN
				case '5' : document.getElementById("a"+y+x).style.backgroundColor='#ffcccc'; g.c(y,x).backgroundColor='#ffcccc'; break; // PINK
				case '6' : document.getElementById("a"+y+x).style.backgroundColor='#BE81F7'; g.c(y,x).backgroundColor='#BE81F7'; break; // PURPLE
				case '7' : document.getElementById("a"+y+x).style.backgroundColor='#D8F781'; g.c(y,x).backgroundColor='#D8F781'; break; // GREENY
				case '8' : document.getElementById("a"+y+x).style.backgroundColor='#BEF781'; g.c(y,x).backgroundColor='#BEF781'; break; // GREENY
				case '9' : document.getElementById("a"+y+x).style.backgroundColor='#999999'; g.c(y,x).backgroundColor='#999999'; break; // GREY
				}
			}
		//alert(stratname + ' ' + stage);
		backgroundList(stratname);
		paint_yes_no( strat_list, stratname );
		some_changes = true;
		if( some_changes ) save_board(cookieauto);
	}
	else
	{
		backgroundList('');
		paint_yes_no( strat_list, stratname );
	}
	document.getElementById("takestep").onclick=take_step;
	document.getElementById("takestep").className='SButton';
	document.getElementById("backstep").className='SButton';
	setKnown();
	set_chain_cycles();
}
function back_step()
{
	let i,j;
	if( document.getElementById("backstep").className == 'GButton' ) return;
	for(j=0;j<9;j++)
		for(i=0;i<9;i++)
		{
			let cc = g.c(j,i);
			if( cc.last>0 )
			{
				cc.show=cc.val=0;
				cc.orig=cc.mask=cc.last;
				lable_square( j,i,0 );
				some_changes=true;
				document.forms.DataEntry.elements["D"+j+i].value='';
			}
		}
	some_changes=false;
	stage=(laststage<=1)?0:laststage;
	backgroundList((stage<=5)?''+stage:strat_list[stage]);
	backup_yes_no( strat_list, stage, 3 );

	document.getElementById("backstep").className='GButton';
	document.getElementById("takestep").onclick=take_step;
	document.getElementById("takestep").className = 'SButton';
	setKnown();
	blue_board();
	save_board(cookieauto);
	jg.clear();
}
/* Function to put a number on the board from the data entry form */
function set_odd_even(tf, e)
{
	let t = e.target;
	let y = parseInt(t.id.charAt(1), 10);	// Coordinate found in the input field name
	let x = parseInt(t.id.charAt(2), 10);

	g.c(y, x).jb = (g.c(y, x).jb == 1) ? 2 : 1;
	g.c(y, x).backgroundColor = g.jbcol(y, x);

	if (g.val(y, x) > 0) {
		set_square(x, y, g.val(y, x), 1);
	}
	else {
		lable_square(y, x, 0);
	}
	let oldcellcol = "DE5";
	if (g.c(y, x).box == 1 || g.c(y, x).box == 3 || g.c(y, x).box == 5 || g.c(y, x).box == 7) oldcellcol = "DE6";
	document.getElementById("D" + y + x).className = (g.c(y, x).jb == 1) ? oldcellcol : "DE3";
}

function add_data(tf, e)
{
	let x,y,change=false;
	some_changes=false;
	let t = e.target;
	y=parseInt(t.id.charAt(1),10);	// Coordinate found in the input field name
	x=parseInt(t.id.charAt(2),10);
	let keyCode = e.which;
	if (keyCode == undefined)
		keyCode = e.keyCode;
	switch( keyCode ) {
	case 9 :
		return; // browser handles navigation
//		break;
	case 37 :
		navigate(y,x-1);
		return;
//		break;
	case 38 :
		navigate(y-1,x);
		return;
//		break;
	case 39 :
		navigate(y,x*1+1);
		return; // space, dot = right arrow
//		break;
	case 40 :
		navigate(y*1+1,x);
		return;
//		break;
//	default: added and removed july 2021 some people getting number replacement
//	    if (IsNumericChar(String.fromCharCode(keyCode)) > -1) t.value = IsNumericChar(String.fromCharCode(keyCode));
	}
	blue_board();
	if( IsNumeric(t.value) )	// If the value is numeric
	{
		//if( g.c(y,x).orig & (1 << (t.value-1)) )	// ..Check if its a possible number for that square
		//{
			if( g.val(y,x)!=t.value ) change=true;
			g.c(y,x).clue = (enterclues) ? t.value : 0;
			g.c(y,x).val=t.value;				// .. it is, so put it on the board
			g.c(y,x).mask=0;
			g.c(y,x).color=(enterclues) ? sq_col[1] : sq_col[2];
			set_square(x,y,g.val(y,x),2);
		//}
		//else t.value=( g.val(y,x) && !g.c(y,x).orig ) ? g.val(y,x) : '';
	}
	else {
		if( t.value==0 ) change=true;
		t.value = '';
		if( g.c(y,x).orig==0 ) g.c(y,x).orig=511;
		g.c(y,x).mask=g.c(y,x).orig;
		g.c(y,x).clue=g.c(y,x).val=0;
		lable_square(y,x,0);
		some_changes=true;
		document.getElementById("R0").innerHTML = '';
	}
	if( change && document.getElementById("autotab").checked ) navigate(y,x*1+1);
	stage=0;
	some_changes=true;
	setKnown();
	if( !sanity_check(true) )
	{
		save_board(cookieauto);
		if( document.getElementById("autoclear").checked ) {
			g.resetMask();
			show_candidates();
		}
	}
}
function email_board()
{
	let x,y,n,h,bc,done=0,okay=false;
	let board='bd=', boardpacked='bd=';
	for(y=0;y<9;y++)
		for(x=0;x<9;x++)
		{
			let cc = g.c(y, x);
			if( cc.val>0 ) done++;
			n = (cc.val ? g.valbit(y, x) : cc.mask);
			board += (cc.val) ? cc.val : '0';
			bc = bit_count(cc.mask);
			if (bc > 1 && bc < 9) okay = true;
			n = (n << 1) + ((cc.clue) ? 1 : 0); // shift to make room for one more bit
			h = n.toString(32);
			if (h.length < 2) h = '0' + h;
			boardpacked += h;
		}
	if (!done) {
		alert("Warning: this board is empty!");
		return;
	}

	document.getElementById("emailhtmlback").className = "popupbackgroundshow";
	document.getElementById("emailhtml").className = "popupformshow";
	document.getElementById("closeemail").focus();

	let emailText = document.getElementById('emailtextarea');

	emailText.value = "There is a " + puztype + " board I would like you to look at\n\nClick on this link:\nhttps://www.sudokuwiki.org/" + solverfile + "?" + board + "\n\n" +
		"Alternatively, with candidates: \n\nClick on this link:\nhttps://www.sudokuwiki.org/" + solverfile + "?" + boardpacked + "\n\n";

	if (okay) {
		emailText.value += "This is a text version of the board useful for posting on forums:\n"
			+ PrintForumSudoku();
	}
}
function print_board(ptype)
{
	let x,y,n,h,done=0;
	let boardpacked='&bd=';
	let showhints = document.getElementById('showhints').checked;
	for(y=0;y<9;y++)
		for(x=0;x<9;x++)
		{
			let cc = g.c(y, x);
			if( cc.val>0 ) done++;
			n = (cc.val ? g.valbit(y, x) : ((showhints) ? cc.mask : 0));
			// going to use the clue field to flag if a candidate or not.
			// That way 1 note can be preserved and clue/solution distintion doesnt matter on print
			n = (n << 1) + ((cc.mask) ? 0 : 1);
			//n = (n << 1) + ((cc.clue) ? 1 : 0); // shift to make room for one more bit
			h = n.toString(32);
			if (h.length < 2) h = '0' + h;
			boardpacked += h;
		}

	let SGW=window.open('/Print/SudokuPrintable.htm?jig=' + puzTypeNum() + '&ptype=' + ptype + boardpacked,'_blank');
	if (!SGW.opener) SGW.opener=self;
}
function closeform(fname) {
	let d = document.getElementById(fname);
	d.className = "popupbackgroundhide";
}
function test_solutions() {
    let x, y, done = 0, SGW;
    let board = '';

    done = blue_board();
    if (puztype==='Sudoku' && done < 16) { alert('Too few clues/numbers, normal Sudoku must have 17 clues minimum.'); return; }
    if (puztype==='Sudoku X' && done < 12) { alert('Too few clues/numbers, Sudoku X must have 12 clues minimum.'); return; }
    if (done == 81) { alert('Puzzle is complete.'); return; }

    if (sanity_check(true) > 0) {
        alert("Oops. Some problem with the puzzle - correct these first");
    } else {
        for (y = 0; y < 9; y++)
			for (x = 0; x < 9; x++)
				board = board + g.val(y, x);

		const outTag = document.getElementById('out');
		const d = document.getElementById("popupbackground");
		d.className = "popupbackgroundshow";
		outTag.innerHTML = "Loading...";
		document.getElementById("solutioncount").className = "popupformshow";
		document.getElementById("closesc").focus();

		const res = WebSudoku.Solutions(puzTypeNum() + ',' + board);
		outTag.innerHTML = res;

      //  SGW = window.open('S/WebSudoku.dll?solutions&' + jig + ',' + board, '_blank', 'resizable=yes,toolbar=1,scrollbars=yes,left=100,top=10,screenX=100,screenY=10,width=670,height=480');
       // if (!SGW.opener) SGW.opener = self;
    }
}
function toggle_strats( chkbox, whichset )
{
	let i;
	if( puztype==='Sudoku' ) {
		switch( whichset ) {
		case 1 :
			for(i=5;i<=13;i++)
				document.getElementById("CB" + strat_list[i]).checked = chkbox.checked;
			break;
		case 2 :
			for(i=14;i<=24;i++)
				document.getElementById("CB" + strat_list[i]).checked = chkbox.checked;
			break;
		case 3 :
			for(i=25;i<=38;i++)
				document.getElementById("CB" + strat_list[i]).checked = chkbox.checked;
			break;
		case 5 :
			document.getElementById("CBURT").checked = !document.getElementById("CBURT").checked;
			document.getElementById("CBHUR").checked = !document.getElementById("CBHUR").checked;
		}
		save_unchecked();
	} else {
		switch( whichset ) {
		case 1 :
			for(i=5;i<=10;i++)
				document.getElementById("CB" + sdx_list[i]).checked = chkbox.checked;
			break;
		case 2 :
			for(i=11;i<=18;i++)
				document.getElementById("CB" + sdx_list[i]).checked = chkbox.checked;
			break;
		case 3 :
			for(i=19;i<=31;i++)
				document.getElementById("CB" + sdx_list[i]).checked = chkbox.checked;
			break;
		case 4 :
			for(i=32;i<=29;i++)
				document.getElementById("CB" + sdx_list[i]).checked = chkbox.checked;
			break;
		case 5 :
			document.getElementById("CBURT").checked = !document.getElementById("CBURT").checked;
			document.getElementById("CBHUR").checked = !document.getElementById("CBHUR").checked;
			document.getElementById("CBEUR").checked = !document.getElementById("CBEUR").checked;
		}
		save_unchecked();
	}
}

function showchainhelp() {
	if( editmode==2 ) {
		document.getElementById("chainingdiv").style.visibility = 'visible';
		document.getElementById("chainingdiv").style.display = 'block';
		document.getElementById("quickhelp").style.visibility = 'collapse';
		document.getElementById("quickhelp").style.display = 'none';
	} else {
		document.getElementById("chainingdiv").style.visibility = 'collapse';
		document.getElementById("chainingdiv").style.display = 'none';
		document.getElementById("quickhelp").style.visibility = 'visible';
		document.getElementById("quickhelp").style.display = 'block';
	}
	if (editmode == 3) {
		document.getElementById("colpicker").style.visibility = 'visible';
		document.getElementById("colpicker").style.display = 'inline-block';
	} else {
		document.getElementById("colpicker").style.visibility = 'collapse';
		document.getElementById("colpicker").style.display = 'none';
	}
}
