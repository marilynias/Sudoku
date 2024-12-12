/*
 * @author Andrew Stuart
 */

let clear_results;
let curHighlight = 0;
let curChain = 1,
  manyChains = 0;
let selectedColour = 0;
let sudjson;
let serverbusy = false;

let stratcols = [
  0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2,
  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4,
  4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5,
];
const stratbands = [
  '#ffffff',
  '#77ff77',
  '#ffdd00',
  '#ff9900',
  '#ff5500',
  '#ff2200',
];

function bit_count(b) {
  let n = 0;
  if (!b) {
    return 0;
  }
  do {
    ++n;
  } while ((b &= b - 1));
  return n;
}
function myIsNaN(o) {
  return typeof o === 'number' && isNaN(o);
}
function IsNumeric(strChar) {
  //  check for valid numeric strings
  const strValidChars = '123456789';
  let blnResult = true;

  if (strChar.length === 0) {
    return false;
  }

  if (strValidChars.indexOf(strChar) == -1) {
    blnResult = false;
  }
  return blnResult;
}
function IsNumeric2(strChar) {
  //  check for valid numeric strings
  if (strChar.length === 0) {
    return false;
  }
  let n = parseInt(strChar, 10);
  if (myIsNaN(n)) {
    return false;
  }
  if (n < 1 || n > 45) {
    return false;
  }
  return true;
}
function IsNumericChar(strChar) {
  //  check for valid numeric strings
  const strChar2Num1 = 'pqwertyuio',
    strChar2Num2 = 'PQWERTYUIO';
  let blnResult = -1;

  if (strChar.length === 0) {
    return -1;
  }
  if (strChar2Num1.indexOf(strChar) > -1) {
    blnResult = strChar2Num1.indexOf(strChar);
  } else if (strChar2Num2.indexOf(strChar) > -1) {
    blnResult = strChar2Num2.indexOf(strChar);
  }
  return blnResult;
}
function IsNumericKenKen(strChar) {
  //  check for valid numeric strings
  if (strChar.length === 0) {
    return false;
  }
  let n = parseInt(strChar, 10);
  if (myIsNaN(n)) {
    return false;
  }
  if (n < 1) {
    return false;
  }
  return true;
}
Array.prototype.inArray = function (s) {
  for (let i = 0; i < this.length; i++) {
    if (this[i] == s) return true;
  }
  return false;
};
Array.prototype.pushIfNotExist = function (element) {
  if (!this.inArray(element)) {
    this.push(element);
  }
};
Array.prototype.popIfExist = function (element) {
  for (let i = 0; i < this.length; i++) {
    if (this[i] == element) this.splice(i, 1);
  }
};
function puzTypeNum() {
  switch (puztype) {
    case 'Sudoku':
      return 0;
    case 'Sudoku X':
      return -1;
    case 'Killer':
      return -3;
    case 'Colour Sudoku':
      return -4;
    case 'Windoku':
      return -5;
    case 'Stripy':
      return -6;
  }
}
function mask2str(m) {
  let i,
    p = 0,
    str = '';
  for (i = 0; i < 9; i++) {
    if (m & (1 << i)) {
      if (p++) {
        str = str + '/';
      }
      str = str + abetx.charAt(i);
    }
  }
  return str;
}
function digitise(y, x, m) {
  let i,
    p = 0,
    str = '';
  for (i = 0; i < 9; i++) {
    if (m & (1 << i)) {
      str += '' + y + x + i;
    }
  }
  return str;
}
function bit2int(m) {
  switch (m) {
    case 1:
      return 0;
    case 2:
      return 1;
    case 4:
      return 2;
    case 8:
      return 3;
    case 16:
      return 4;
    case 32:
      return 5;
    case 64:
      return 6;
    case 128:
      return 7;
    case 256:
      return 8;
  }
  return 0;
}
function cordit(y, x) {
  if (coordmode === 0) {
    return 'r' + abetx.charAt(y) + 'c' + abetx.charAt(x);
  }
  return abety.charAt(y) + abetx.charAt(x);
}
function strat_add(s) {
  let doc;
  /*
	doc = document.getElementById("ifrm");
	if( clear_results ) { // clear anything from server
		doc.value = s;
		clear_results = false;
	} else {
		doc.value = doc.value + '\n' + s;
	}
	return;*/

  if (!document.ifrm) {
    doc = document.getElementById('ifrm').contentDocument;
  } else {
    doc = document.ifrm.document;
  }
  if (clear_results) {
    // clear anything from server
    doc.body.innerHTML = s + '<br>';
    clear_results = false;
  } else {
    doc.body.innerHTML += s + '<br>';
  }
}
function enough_digits() {
  // Need to be 8 or 9 digits to be sane
  let n = 0,
    x,
    y;
  for (y = 0; y < 9; y++)
    for (x = 0; x < 9; x++) if (g.val(x, y)) n |= 1 << (g.val(x, y) - 1);
  if (bit_count(n) < 8) {
    strat_add(
      '<div class="res_error">Error: At least 8 digits 1 to 9 must be on the board</div>'
    );
    return false;
  }
  return true;
}
function change_hints() {
  showhints = !showhints;
  for (let j = 0; j < 9; j++) {
    for (let i = 0; i < 9; i++) {
      if (g.val(j, i) === 0) {
        lable_square(j, i, 0);
      }
    }
  }
}
function convert_str2mask(astr) {
  let c,
    n = 0;
  for (let i = 0; i < astr.length; i++) {
    c = parseInt(astr.charAt(i), 10);
    if (IsNumeric(c)) n |= 1 << (c - 1);
  }
  return n;
}
function assign_clicks() {
  let t, x, y, d;

  for (y = 0; y < 9; y++)
    for (x = 0; x < 9; x++) {
      t = document.getElementById('a' + y + x);
      t.onclick = color_same;
      if (t.captureEvents) t.captureEvents(Event.CLICK);
      if (puztype !== 'Killer' && puztype !== 'Killer Jigsaw') {
        d = document.getElementById('D' + y + x);
        d.addEventListener('keydown', function (e) {
          if (e.which === 38 || e.which === 40) {
            e.preventDefault(); // stop up/down arrows on number inputs
          }
        });
      }
    }
}

const sud_list = [
  'PAI',
  'TRI',
  'QUD',
  'PPR',
  'LBR',
  'GTH',
  'XWG',
  'SCN',
  'YWG',
  'REL',
  'ERT',
  'SFH',
  'XYZ',
  'BUG',
  'XCY',
  'XYC',
  '3DM',
  'JFH',
  'URT',
  'FWK',
  'SKL',
  'EUR',
  'HUR',
  'WXY',
  'APE',
  'JE2',
  'GXC',
  'FXW',
  'FSF',
  'AIC',
  'COQ',
  'PFC',
  'NFC',
  'CFC',
  'UFC',
  'ALS',
  'DBL',
  'POM',
  'QFC',
  'BBB',
];
const jig_list = [
  'PAI',
  'TRI',
  'QUD',
  'PPR',
  'LBR',
  'DPP',
  'DLB',
  'LOL',
  'XWG',
  'SCN',
  'YWG',
  'REL',
  'SFH',
  'XYZ',
  'XCY',
  'XYC',
  '3DM',
  'JFH',
  'WXY',
  'GXC',
  'AIC',
  'PFC',
  'NFC',
  'CFC',
  'UFC',
  'ALS',
  'DBL',
  'POM',
  'QFC',
  'BBB',
];
const sdx_list = [
  'PAI',
  'TRI',
  'QUD',
  'PPR',
  'LBR',
  'XWG',
  'SCN',
  'YWG',
  'REL',
  'SFH',
  'XYZ',
  'XCY',
  'XYC',
  '3DM',
  'JFH',
  'URT',
  'HUR',
  'WXY',
  'APE',
  'GXC',
  'FXW',
  'FSF',
  'AIC',
  'COQ',
  'PFC',
  'NFC',
  'CFC',
  'UFC',
  'ALS',
  'DBL',
  'POM',
  'QFC',
  'BBB',
];
const kil_list = [
  'PAI',
  'TRI',
  'QUD',
  'KL1',
  'IO1',
  'PPR',
  'LBR',
  'KCS',
  'XWG',
  'SCN',
  'YWG',
  'IO2',
  'KL4',
  'CUO',
  'KCC',
  'REL',
  'SFH',
  'XYZ',
  'XCY',
  'XYC',
  '3DM',
  'JFH',
  'WXY',
  'APE',
  'GXC',
  'FXW',
  'FSF',
  'AIC',
  'COQ',
  'PFC',
  'NFC',
  'CFC',
  'UFC',
  'ALS',
  'DBL',
  'QFC',
  'BBB',
];
const win_list = [
  'SIN',
  'PAI',
  'TRI',
  'QUD',
  'PPR',
  'LBR',
  'XWG',
  'SCN',
  'YWG',
  'REL',
  'SFH',
  'XYZ',
  'XCY',
  'XYC',
  '3DM',
  'JFH',
  'WXY',
  'GXC',
  'FXW',
  'FSF',
  'AIC',
  'COQ',
  'PFC',
  'NFC',
  'CFC',
  'UFC',
  'ALS',
  'DBL',
  'POM',
  'QFC',
  'BBB',
];
const kjg_list = [
  'PAI',
  'TRI',
  'QUD',
  'KL1',
  'IO1',
  'PPR',
  'LBR',
  'KCS',
  'DPP',
  'DLB',
  'LOL',
  'XWG',
  'SCN',
  'YWG',
  'IO2',
  'KL4',
  'CUO',
  'KCC',
  'REL',
  'SFH',
  'XYZ',
  'XCY',
  'XYC',
  '3DM',
  'JFH',
  'WXY',
  'APE',
  'GXC',
  'FXW',
  'FSF',
  'AIC',
  'COQ',
  'PFC',
  'NFC',
  'CFC',
  'UFC',
  'ALS',
  'DBL',
  'QFC',
  'BBB',
];

function setStratList() {
  switch (puztype) {
    case 'Jigsaw':
      return jig_list;
    case 'Sudoku X':
      return sdx_list;
    case 'Killer':
      return kil_list;
    case 'Colour Sudoku':
      return win_list;
    case 'Windoku':
      return win_list;
    case 'Stripy':
      return win_list;
    case 'Killer Jigsaw':
      return kjg_list;
  }
  return sud_list;
}
let strat_list = setStratList();
let arr_unchecked_strats = [];

const sudokumap =
  '111222333111222333111222333444555666444555666444555666777888999777888999777888999'; // 0 = SUDOKU
const jb_cellbkg = [
  '#ffd5d5',
  '#ddffff',
  '#bbffaa',
  '#ddffbb',
  '#ffffff',
  '#ddeeff',
  '#dddddd',
  '#ffe5ff',
  '#ffffbb',
];
const win_cellbkg = [
  '#ddffff',
  '#ddffff',
  '#ddffff',
  '#ddffff',
  '#ffffff',
  '#ddffbb',
  '#ffd5d5',
  '#ffe5ff',
  '#ffffbb',
];
const linecols = new Array(
  '#ff7600',
  '#ffA900',
  '#8CB32D',
  '#84E900',
  '#00AB6F',
  '#01939A',
  '#6C8AD5',
  '#8E6ED7',
  '#D660DC'
);
const digitcols = new Array(
  '#FEB06E',
  '#FDCF74',
  '#B7CA88',
  '#AEED67',
  '#A3DBC7',
  '#A8E7EA',
  '#BEC9E6',
  '#C7B4F3',
  '#F4C1F6',
  '#FFFF00'
);
const jigsawcols = new Array(
  '#FFAE83',
  '#AFEEFF',
  '#98FB98',
  '#FFee88',
  '#E3E3E3',
  '#DEB887',
  '#87BEEA',
  '#D8BFD8',
  '#FFC0CB'
);
//let jb_cellbkg = jigsawcols

const rmap =
  '111111111222222222333333333444444444555555555666666666777777777888888888999999999';
const cmap =
  '123456789123456789123456789123456789123456789123456789123456789123456789123456789';
const bmap =
  '111222333111222333111222333444555666444555666444555666777888999777888999777888999';

class Cell {
  constructor() {
    this.mask = 0;
    this.elim = 0;
    this.val = 0;
    this.clue = 0;
    this.orig = 0;
    this.last = 0;
    this.jc = 0;
    this.jb = 0;
    this.diag = 0;
    this.map = 0;
    this.csz = 0;
    this.cid = 0;
    this.ccl = 0;
    this.show = 0;
    this.row = 0;
    this.col = 0;
    this.box = 0;
    this.win = 0;
    this.sol = 0;
    this.iswind = false;
    this.color = '#000000';
    this.backgroundColor = '#eeeedd';
  }
  vbit() {
    return 1 << (this.val - 1);
  }
  jbcol() {
    return jig > 0 ? jb_cellbkg[5] : jb_cellbkg[this.jb];
  }
  maskStr() {
    return mask2str(this.mask);
  }
}

class Grid {
  constructor(width, height) {
    this.width = width;
    this.height = height;
    this.cells = Array(width * height)
      .fill(null)
      .map(() => new Cell());
  }
  c(y, x) {
    return this.cells[y * this.width + x];
  }
  mask(y, x) {
    return this.cells[y * this.width + x].mask;
  }
  hasn(y, x, n) {
    let m = this.cells[y * this.width + x].mask;
    return m & (1 << n);
  }
  val(y, x) {
    const cell = this.cells[y * this.width + x];
    return cell ? cell.val : 0;
  }
  row(y, x) {
    return this.cells[y * this.width + x].row;
  }
  col(y, x) {
    return this.cells[y * this.width + x].col;
  }
  box(y, x) {
    return this.cells[y * this.width + x].box;
  }
  win(y, x) {
    return this.cells[y * this.width + x].win;
  }
  sol(y, x) {
    return this.cells[y * this.width + x].sol;
  }
  diag(y, x) {
    return this.cells[y * this.width + x].diag;
  }
  valbit(y, x) {
    const v = this.cells[y * this.width + x].val;
    return 1 << (v - 1);
  }
  jc(y, x) {
    return this.cells[y * this.width + x].jc;
  }
  jbn(y, x) {
    return this.cells[y * this.width + x].jb;
  }
  jbcol(y, x) {
    const cell = this.cells[y * this.width + x];
    if (!cell) return jb_cellbkg[0];
    return jig > 0 ? jb_cellbkg[5] : jb_cellbkg[cell.jb];
  }
  wincol(y, x) {
    const cell = this.cells[y * this.width + x];
    if (!cell) return puztype === 'Windoku' ? win_cellbkg[0] : jb_cellbkg[0];
    if (jig > 0) return jb_cellbkg[5];
    return puztype === 'Windoku' ? win_cellbkg[cell.jb] : jb_cellbkg[cell.jb];
  }
  show(y, x) {
    return this.cells[y * this.width + x].show;
  }
  bcmask(y, x) {
    return bit_count(this.cells[y * this.width + x].mask);
  }
  backgroundColor(y, x) {
    return this.cells[y * this.width + x].backgroundColor;
  }
  rotate_left() {
    const tmp = [...this.cells];
    for (let y = 0; y < 9; y++) {
      for (let x = 0; x < 9; x++) {
        this.cells[(8 - x) * 9 + y] = tmp[y * 9 + x];
      }
    }
  }
  rotate_right() {
    const tmp = [...this.cells];
    for (let y = 0; y < 9; y++) {
      for (let x = 0; x < 9; x++) {
        this.cells[x * 9 + (8 - y)] = tmp[y * 9 + x];
      }
    }
  }
  flip_horiz() {
    const tmp = [...this.cells];
    for (let y = 0; y < 9; y++) {
      for (let x = 0; x < 9; x++) {
        this.cells[y * 9 + x] = tmp[y * 9 + (8 - x)];
      }
    }
  }
  resetMask() {
    for (let y = 0; y < 9; y++) {
      for (let x = 0; x < 9; x++) {
        this.cells[x * 9 + y].mask = this.cells[x * 9 + y].val ? 0 : 511;
      }
    }
  }
  prepareElim() {
    for (let x = 0; x < 9; x++) {
      for (let y = 0; y < 9; y++) {
        this.cells[x * 9 + y].elim = 0;
        this.cells[x * 9 + y].wind = 0;
      }
    }
  }
}

let g = new Grid(9, 9);

const sq_col = ['black', '#bb0000', 'blue', 'blue', '#cccccc', '#aaaaaa'];

function sudokuWipe() {
  for (let x = 0; x < 9; x++)
    for (let y = 0; y < 9; y++) {
      let cc = g.c(x, y);
      cc.backgroundColor = cc.jbcol();
      cc.color = 'black';
      cc.orig = cc.mask = 511;
      cc.val = cc.show = 0;
    }
}
function string_grid() {
  let s = '';
  for (let y = 0; y < 9; y++)
    for (let x = 0; x < 9; x++) {
      if (s.length) s += ',';
      if (g.val(y, x)) s += '' + g.valbit(y, x);
      else s += '' + g.mask(y, x);
    }
  return s;
}
function paint_yes_no(thelist, endstage) {
  for (let i = 0; i < thelist.length; i++) {
    if (thelist[i] == endstage) break;
    document.getElementById('R' + thelist[i]).innerHTML =
      '<font color=#ff0000><b>No</b></font>';
  }
  if (endstage != 'NO') {
    let d = document.getElementById('R' + endstage);
    if (d) d.innerHTML = '<font color=#00ff00><b>Yes</b></font>';
    else if (endstage != 'ERT')
      alert('paint_yes_no: no row called ' + 'R' + endstage);
  }
}
function reset_yes_no(thelist, amt) {
  for (let i = 1; i <= amt; i++) {
    if (!document.getElementById('R' + i)) alert('no R' + i);
    else document.getElementById('R' + i).innerHTML = '&nbsp;';
  }
  for (let i = 0; i < thelist.length; i++) {
    let d = document.getElementById('R' + thelist[i]);
    if (d) d.innerHTML = '&nbsp;';
    else if (thelist[i] != 'ERT')
      alert('reset_yes_no: no row called ' + 'R' + thelist[i]);
  }
}
function backgroundList(stratname) {
  let t = document.getElementById('TestT');
  for (let i = 0; i < t.rows.length; i++) {
    t.rows[i].cells[0].style.backgroundColor =
      i % 2 == 1 ? '#333333' : '#222222';
    t.rows[i].cells[1].style.backgroundColor =
      i % 2 == 1 ? '#333333' : '#222222';
    t.rows[i].cells[2].style.backgroundColor =
      i % 2 == 1 ? '#333333' : '#222222';
  }
  /*	for(let i=0;i<strat_list.length+5;i++) {
		if( !document.getElementById("T"+i) ) alert("cannot find T"+i);
		document.getElementById("T"+i).style.backgroundColor=(((i%2)==1)?"#333333":"#222222");
	}*/
  if (stratname != '') {
    if (!document.getElementById('T' + stratname))
      alert('Cannot find element T' + stratname);
    else
      document.getElementById('T' + stratname).style.backgroundColor =
        '#777700';
  }
  if (puztype !== 'Sudoku') return;
  if (UsesGurth) {
    t.rows[9].cells[0].style.backgroundColor = '#114411';
    t.rows[9].cells[1].style.backgroundColor = '#114411';
    t.rows[9].cells[2].style.backgroundColor = '#114411';
    document.getElementById('gurthrow1').style.display = '';
    document.getElementById('TGTH').style.display = '';
    document.getElementById('RGTH').style.display = '';
  } else {
    document.getElementById('gurthrow1').style.display = 'none';
    document.getElementById('TGTH').style.display = 'none';
    document.getElementById('RGTH').style.display = 'none';
  }
}
function backup_yes_no(thelist, stage, amt) {
  let i, s;
  for (i = stage; i < amt; i++) {
    if (!document.getElementById('R' + i))
      alert('cannot find R' + i + ' in backup_yes_no');
    else document.getElementById('R' + i).innerHTML = '&nbsp;';
  }
  s = stage - amt;
  if (s < 0) s = 0;
  for (i = s; i < thelist.length; i++) {
    let d = document.getElementById('R' + thelist[i]);
    if (d) d.innerHTML = '&nbsp;';
    else alert('backup_yes_no: no row called ' + 'R' + thelist[i]);
  }
}
function padzero(a) {
  if (!IsNumeric2(a)) return '00';
  if (a < 10) return '0' + a;
  return a;
}
function get_stage(thelist, stratname, amt) {
  for (let i = 0; i < thelist.length; i++)
    if (thelist[i] == stratname) return amt + i;
  return 0;
}
function navigate(ny, nx) {
  let x = nx == 9 ? 0 : nx == -1 ? 8 : nx;
  let y = nx == 9 ? ny * 1 + 1 : nx == -1 ? ny - 1 : ny;
  y = y == 9 ? 0 : y == -1 ? 8 : y;
  document.getElementById('D' + y + x).focus();
  document.getElementById('D' + y + x).select();
}
function save_auto_tab() {
  let at = document.getElementById('autotab').checked;
  cookie.create('solverautotab', at ? 1 : 0, 30);
}
function save_auto_clear() {
  let at = document.getElementById('autoclear').checked;
  cookie.create('solverautoclear', at ? 1 : 0, 30);
}
function load_auto_tab() {
  let at = cookie.read('solverautotab');
  if (at === 1) document.getElementById('autotab').checked = true;
  if (at === 0) document.getElementById('autotab').checked = false;
  at = cookie.read('solverautoclear');
  if (at === 1) document.getElementById('autoclear').checked = true;
  if (at === 0) document.getElementById('autoclear').checked = false;
}
function setKnown() {
  let i,
    j,
    k = 0;
  for (
    j = 0;
    j < 9;
    j++ // For each square on the board
  )
    for (i = 0; i < 9; i++) if (g.val(j, i) > 0) k++;
  document.getElementById('countknown').innerHTML =
    'Clues+Solved: ' + k + '/81';
}

function toggle_color(elem, color_one, color_two) {
  let bgcolor = elem.css('background-color');
  elem.css('background-color', color_one); // try new color
  if (bgcolor == elem.css('background-color'))
    // check if color changed
    elem.css('background-color', color_two); // if here means our color was color_one
}

function HexToR(h) {
  return parseInt(cutHex(h).substring(0, 2), 16);
}
function HexToG(h) {
  return parseInt(cutHex(h).substring(2, 4), 16);
}
function HexToB(h) {
  return parseInt(cutHex(h).substring(4, 6), 16);
}
function cutHex(h) {
  return h.charAt(0) == '#' ? h.substring(1, 7) : h;
}

function hexToRgb22(hex) {
  let result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}
function hexToRgb(hex) {
  let bigint = parseInt(hex.slice(1), 16);
  let r = (bigint >> 16) & 255;
  let g = (bigint >> 8) & 255;
  let b = bigint & 255;

  return 'rgb(' + r + ', ' + g + ', ' + b + ')';
}
function componentToHex(c) {
  let hex = c.toString(16);
  return hex.length == 1 ? '0' + hex : hex;
}

function rgbToHex(r, g, b) {
  return '#' + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

let currentToggleOn = '#009900';
let currentToggleOff = '#FF0000';
let backgroundCol = '#ccccff';

function hexColor(colorval) {
  let parts = colorval.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
  if (parts === null) {
    parts = colorval.match(/^rgba\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)$/);
    if (parts === null) return '';
    delete parts[4];
  }

  delete parts[0];
  for (let i = 1; i <= 3; ++i) {
    parts[i] = parseInt(parts[i]).toString(16);
    if (parts[i].length == 1) parts[i] = '0' + parts[i];
  }
  return '#' + parts.join('');
}
/*------------------------------------------------------------------------*/
/* Function to colour the board according to what the user has clicked on */
/*------------------------------------------------------------------------*/
let newInput;
function Sudoku1(afield, y, x) {
  let cell;
  let fval = convert_str2mask(afield.value);

  cell = document.getElementById('a' + y + x);
  cell.removeChild(newInput);
  cell.onclick = color_same;
  let cc = g.c(y, x);

  if (fval == 0) {
    cc.val = 0;
    cc.mask = 511;
    cc.color = 'black';
    lable_square(y, x, 0);
  } else {
    if (bit_count(fval) == 1) {
      if (afield.value.charAt(0) == '0') {
        cc.val = 0;
        cc.mask = fval;
        cc.color = 'black';
        lable_square(y, x, 0);
      } else {
        cc.val = bit2int(fval) + 1;
        cc.mask = 0;
        cc.color = sq_col[2];
        set_square(x, y, g.val(y, x), 2);
      }
    } else {
      cc.val = 0;
      cc.mask = fval;
      cc.color = 'black';
      lable_square(y, x, 0);
    }
  }
  if (document.getElementById('autoclear').checked) {
    g.resetMask();
    show_candidates();
  }
  save_board(cookieauto);
  stage = 0;
  backgroundList('');
}
function color_same(e) {
  let targ, x, y, i, j, t, f, n, searchmode;
  let ival = '';
  if (!e) e = window.event;
  if (e.target) targ = e.target;
  else if (e.srcElement) targ = e.srcElement;
  if (targ.nodeType == 3)
    // defeat Safari bug
    targ = targ.parentNode;

  if (targ.id == null || targ.id == '') return;

  x = parseInt(targ.id.charAt(2), 10);
  y = parseInt(targ.id.charAt(1), 10);
  if (editmode == 3) {
    //for (i = 0; i < jb_cellbkg.length; i++)
    //	document.getElementById('colpicker' + i).style.backgroundColor = digitcols[i];
    document.getElementById('colpicker').style.display = 'inline-block';

    //	let tg = document.getElementById('colpicker');
    //	const rect = targ.getBoundingClientRect();
    //	tg.style.display = 'block';
    //	tg.style.left = (parseInt(rect.x) + 1) + 'px';
    //	tg.style.top = (parseInt(rect.y) - 1) + 'px';

    if (targ.id.charAt(0) != 'w') targ = document.getElementById('a' + y + x);
    else if (targ.innerHTML == '&nbsp;')
      targ = document.getElementById('a' + y + x);

    if (
      targ.style.backgroundColor == '' ||
      targ.style.backgroundColor == hexToRgb(g.wincol(y, x))
    )
      //  'rgb(221, 238, 255)' )
      targ.style.backgroundColor = digitcols[selectedColour];
    else targ.style.backgroundColor = g.wincol(y, x);
  } else if (editmode == 2) {
    if (targ.id.charAt(0) == 'w') {
      n = parseInt(targ.id.charAt(3), 10);

      if (!(g.mask(y, x) & (1 << n))) return;

      if (targ.className === 'fshON') {
        searchmode = 1;
      } else if (targ.className === 'fshOFF') {
        searchmode = 0;
      } else {
        searchmode = 2;
      }
      if (!e.shiftKey) {
        if (jg) jg.clear();
        clear_on_off_color();
        curLevel = 1;
      }

      const analyzer = new ChainAnalyzer(
        g,
        document.getElementById('3Dchains').checked,
        puztype == 'Killer Jigsaw'
      ); // true to enable 3D chains
      analyzer.check(x, y, n, searchmode);
    } else {
      clear_on_off_color();
    }
  } else if (editmode == 0) {
    if (targ.id.charAt(0) == 'w') targ = document.getElementById('a' + y + x);
    targ.onclick = null;

    if (g.val(y, x))
      // If user clicked on an unknown square..
      ival = g.val(y, x);
    else
      for (i = 0; i < 9; i++)
        if (g.mask(y, x) & (1 << i)) ival = ival + (i * 1 + 1);

    let icell = document.getElementById('cl' + y + x);
    if (icell) icell.style.display = 'none';
    else targ.innerHTML = '';
    newInput = document.createElement('input');
    newInput.setAttribute('id', 'iput');
    newInput.setAttribute('maxlength', 9);
    newInput.setAttribute('type', 'number');
    newInput.setAttribute('value', ival);
    newInput.className = 'iput2';
    newInput.onblur = function () {
      Sudoku1(this, y, x);
    };
    newInput.addEventListener('keydown', function (e) {
      if (e.which === 38 || e.which === 40) {
        e.preventDefault();
      }
    });
    targ.appendChild(newInput);
    newInput.focus();
  } else if (editmode == 1) {
    if (targ.id.charAt(0) == 'w') {
      n = parseInt(targ.id.charAt(3), 10);
      curHighlight += curHighlight & (1 << n) ? -(1 << n) : 1 << n;
      if ((g.mask(y, x) & (1 << n)) > 0)
        for (j = 0; j < 9; j++)
          for (i = 0; i < 9; i++)
            if ((g.mask(j, i) & (1 << n)) > 0) {
              f = document.getElementById('w' + j + i + n);
              f.style.backgroundColor =
                curHighlight & (1 << n)
                  ? digitcols[n]
                  : g.c(j, i).backgroundColor;
            }
    } else {
      n = g.val(y, x) - 1;
      curHighlight += curHighlight & (1 << n) ? -(1 << n) : 1 << n;
      for (
        j = 0;
        j < 9;
        j++ // For each square on the board
      )
        for (i = 0; i < 9; i++) {
          if (g.val(j, i) == n + 1 && puztype != 'Colour Sudoku') {
            t = document.getElementById('a' + j + i);
            t.style.backgroundColor =
              curHighlight & (1 << n)
                ? digitcols[n]
                : g.c(j, i).backgroundColor;
          } else if (g.mask(j, i) & (1 << n)) {
            // If user clicked on an unknown square..
            f = document.getElementById('w' + j + i + n);
            f.style.backgroundColor =
              curHighlight & (1 << n)
                ? digitcols[n]
                : g.c(j, i).backgroundColor;
          }
        }
    }
  }
}
function show_bivalue() {
  let i, j, t;
  let showit = document.getElementById('chkSB').checked;
  for (j = 0; j < 9; j++)
    for (i = 0; i < 9; i++) {
      t = document.getElementById('a' + j + i);
      if (bit_count(g.mask(j, i)) == 2 && showit)
        t.style.backgroundColor = '#ffeedd';
      else t.style.backgroundColor = g.c(j, i).backgroundColor;
    }
}
async function sendRequest(url, method) {
  // Query the Companies House API
  let headers = new Headers({
    'Content-Type': 'text/html',
    Origin: thedomain + '/',
  });
  const options = {
    method: method,
    headers: headers,
    mode: 'cors',
  };
  const response = await fetch(url, options);

  if (!response.ok) {
    let message = 'An error has occured: ' + response.status;
    throw new Error(message);
  }
  sudjson = await response.json();
  return sudjson;
}
function load_from_solve_path(stepno) {
  sudokuFromSolvePath(sudjson.steps[stepno].position);
  for (let i = 0; i < sudjson.steps.length; i++) {
    let d = document.getElementById('loadsp' + i);
    d.style.backgroundColor = '#222';
  }
  let d = document.getElementById('loadsp' + stepno);
  d.style.backgroundColor = '#226622';
}

function grade_sudoku0() {
  grade_sudoku(0);
}
function grade_sudoku1() {
  grade_sudoku(1);
}
function restore_sp_button() {
  if (serverbusy) {
    setTimeout(restore_sp_button, 6000);
    return;
  }
  document.getElementById('pboard4').className = 'YButton';
  document
    .getElementById('pboard4')
    .addEventListener('click', grade_sudoku0, false);
  document.getElementById('pboard5').className = 'YButton';
  document
    .getElementById('pboard5')
    .addEventListener('click', grade_sudoku1, false);

  serverbusy = false;
}
function release_lock() {
  serverbusy = false;
}
function openresultfile() {
  let doc, newurl, i, j;

  if (!document.ifrm) doc = document.getElementById('ifrm').contentDocument;
  else doc = document.ifrm.document;
  if (!doc) return;

  if (!doc.getElementById('spfile')) {
    alert("Error: Couldn't create the output file");
    return;
  }
  if (thedomain == 'https://localhost:44327')
    newurl = '/' + doc.getElementById('spfile').value;
  else newurl = '/sudoku/solvepaths/' + doc.getElementById('spfile').value;
  let randomnum = '?rnd=' + Math.random().toFixed(7);
  newurl = newurl.substring(0, newurl.length - 3) + 'txt' + randomnum;

  let url = thedomain + newurl;
  serverbusy = false;

  sendRequest(url, 'GET')
    .then((sudjson) => {
      //'<input type="button" class="BButton" style="position:fixed" name="spmove" value="<" onclick="javascript:movesolvepath();" id="spmove">' +

      let d = document.getElementById('solvepathdiv');
      d.className = 'solvepathshow';
      let s =
        '<table class="t100pc"><tr><td><div class="w100pc ccenter"><h2 style="margin:0">' +
        sudjson.title +
        '</h2><div style="font-size:9pt">' +
        sudjson.version +
        '</div></td>' +
        '<td style="width:30px"><input value="X" type="button" id="closesp" class="cancelpopup" onclick="closeform(\'solvepathdiv\');" /></td></tr></table>' +
        '<a target="_solvepath" href="' +
        url +
        '">Open JSON file</a>, <a target="_solvepath" href="/sudoku/solvepaths/' +
        doc.getElementById('spfile').value +
        randomnum +
        '">Open HTML file</a><br>' +
        'Solution: ' +
        sudjson.solution +
        '<br>';
      s +=
        'Clues: ' +
        sudjson.clues +
        ', &nbsp;' +
        'Score: ' +
        sudjson.final_score +
        ', &nbsp;' +
        'Grade: ' +
        (sudjson.final_score == 0 ? 'Unknown' : sudjson.grade) +
        '<br>';
      s += '<div id="solvepathsub">';
      if (sudjson.excluded) {
        s += 'Strategies Excluded from Solver in this run: ';
        for (i = 1; i < sudjson.excluded.length; i++) {
          s += (i > 1 ? ', ' : '') + sudjson.excluded[i];
        }
        s += '<br>';
      }
      for (i = 0; i < sudjson.steps.length; i++) {
        s +=
          '<div id="loadsp' +
          i +
          '" class="sname">Step ' +
          sudjson.steps[i].step +
          ' - ' +
          '<span style="color:' +
          stratbands[stratcols[sudjson.steps[i].snum]] +
          '">' +
          sudjson.steps[i].name +
          '</span>';
        if (sudjson.steps[i].position)
          s +=
            ' &nbsp;<input type="button" class="GreyButton" value="Load" style="font-size:8pt" onclick="load_from_solve_path(' +
            i +
            ')" />';
        s += '</div ><ul>';
        for (j = 0; j < sudjson.steps[i].steps.length; j++)
          s += '<li>' + sudjson.steps[i].steps[j] + '</li>';
        s += '</ul>';
      }
      d.innerHTML = s + '</div>';
    })
    .catch((error) => {
      let d = document.getElementById('solvepathdiv');
      d.className = 'solvepathshow';
      d.innerHTML =
        'Error fetching solve path: ' +
        error.message +
        '<br><br><a href="' +
        url +
        '">Open json file</a>';
    });
}
function clear_on_off_color() {
  let x, y, n, f, t;
  for (y = 0; y < 9; y++)
    for (x = 0; x < 9; x++) {
      t = document.getElementById('a' + y + x);
      if (t.style.backgroundColor != g.c(y, x).backgroundColor) {
        t.style.backgroundColor = g.c(y, x).backgroundColor;
        t.style.color = g.c(y, x).color;
      }
      for (n = 0; n < 9; n++) {
        f = document.getElementById('w' + y + x + n);
        if (f) {
          f.className = '';
          f.style.backgroundColor = '';
        }
      }
    }
  if (jg) jg.clear();
}
function grn_blue_color(s, highlight, m) {
  let i, x, y, n, f;
  for (i = 0; i < s.length; i += 3) {
    if (s.charAt(i) == '{') break;
    y = s.charAt(i) - m;
    x = s.charAt(i + 1) - m;
    n = s.charAt(i + 2) - m;
    f = document.getElementById('w' + y + x + n);
    if (f) f.className = highlight;
  }
}

//============================================================
// Chaining display
//============================================================

class ChainAnalyzer {
  constructor(grid, use3DChains = false, isKiller = false) {
    this.grid = grid;
    this.use3DChains = use3DChains;
    this.bfg = this.initializeBfg();
    this.curLevel = 1;
    this.showbox = true;
    this.showrow = true;
    this.showcol = true;
    this.showwin = false;
    this.showdiag = false;
    this.isKiller = isKiller;
  }

  initializeBfg() {
    return Array(9)
      .fill()
      .map(() =>
        Array(9)
          .fill()
          .map(() => Array(9).fill(0))
      );
  }

  convert_x(cellx, n) {
    let b = 6;
    if (jig >= 1 && cellx > 3) b = 8; // adjustment for jigsaw solver
    if (this.isKiller) b = cellx;
    return cellx * 46 + (n % 3) * 12 + b + parseInt(cellx / 3, 10) * 2;
  }
  convert_y(celly, n) {
    let b = 5;
    if (jig >= 1 && celly > 3) b = 2; // adjustment for jigsaw solver
    if (jig >= 1 && celly > 6) b = 0;
    if (this.isKiller) b = celly;
    return (
      celly * 46 + parseInt(n / 3, 10) * 13 + b + parseInt(celly / 3, 10) * 2
    );
  }
  onOffColor(cellx, celly, n, strong) {
    let highlight = !strong ? 'fshOFF' : 'fshON';
    let f = document.getElementById('w' + celly + cellx + n);
    if (f) f.className = highlight;
  }
  ringCandidate(cellx, celly, n, colour, strong) {
    let x = this.convert_x(cellx, n);
    let y = this.convert_y(celly, n);

    jg.setColor(colour);
    jg.setStroke(1);
    jg.drawEllipse(x, y, 11, 12);
    this.onOffColor(cellx, celly, n, strong);
  }
  ringALS(cellx1, celly1, cellx2, celly2, n, colour, strong) {
    let x1, y1, x2, y2, x3, y3, w, h;

    x1 = this.convert_x(cellx1, n) + 1;
    y1 = this.convert_y(celly1, n) + 1;
    x3 = this.convert_x(cellx2, n) + 1;
    y3 = this.convert_y(celly2, n) + 1;

    x2 = x1 < x3 ? x1 : x3;
    y2 = y1 < y3 ? y1 : y3;
    w = Math.abs(x3 - x1) + 10;
    h = Math.abs(y3 - y1) + 10;

    jg.setColor(colour);
    jg.setStroke(2);
    jg.drawRect(x2, y2, w, h);

    this.onOffColor(cellx1, celly1, n, strong);
    this.onOffColor(cellx2, celly2, n, strong);
  }
  connectCandidates(
    cellx1,
    celly1,
    n1,
    cellx2,
    celly2,
    n2,
    strong,
    colour,
    colourweak
  ) {
    let x1, y1, x2, y2, x3, y3;

    x1 = this.convert_x(cellx1, n1) + 1;
    y1 = this.convert_y(celly1, n1) + 1;
    x3 = this.convert_x(cellx2, n2) + 1;
    y3 = this.convert_y(celly2, n2) + 1;

    if (y1 < y3) y1 += 8;
    if (y3 < y1) y3 += 8;

    if (x1 < x3) x1 += 8;
    if (x3 < x1) x3 += 8;

    x2 = Math.abs(x3 - x1) / 2 + Math.min(x1, x3) - 10;
    y2 = Math.abs(y3 - y1) / 2 + Math.min(y1, y3) - 10;

    let Xpoints = new Array(x1, x2, x3);
    let YPoints = new Array(y1, y2, y3);

    if (strong) {
      jg.setColor(colour);
      jg.setStroke(3);
      jg.drawPolyline(Xpoints, YPoints);
    } else {
      jg.setColor(colour);
      jg.setStroke(1);
      jg.drawPolyline(Xpoints, YPoints);
      Xpoints = new Array(x1 - 2, x2 - 2, x3 - 2);
      YPoints = new Array(y1 + 2, y2 + 2, y3 + 2);
      jg.drawPolyline(Xpoints, YPoints);
    }
  }

  chainLink(cellx1, celly1, n1, cellx2, celly2, n2, colour) {
    let x1, y1, x2, y2, x3, y3;

    x1 = this.convert_x(cellx1, n1) + 1;
    y1 = this.convert_y(celly1, n1) + 1;
    x3 = this.convert_x(cellx2, n2) + 1;
    y3 = this.convert_y(celly2, n2) + 1;

    if (y1 < y3) y1 += 8;
    if (y3 < y1) y3 += 8;

    if (x1 < x3) x1 += 8;
    if (x3 < x1) x3 += 8;

    x2 = Math.abs(x3 - x1) / 2 + Math.min(x1, x3) - 5;
    y2 = Math.abs(y3 - y1) / 2 + Math.min(y1, y3) - 5;
    //	if( n1>6 && n2>6 )
    //		y2 = Math.abs(y3-y1)/2 + Math.min(y1,y3)+10;

    let Xpoints = new Array(x1, x2, x3);
    let YPoints = new Array(y1, y2, y3);

    jg.setColor(colour);
    jg.setStroke(2);
    jg.drawPolyline(Xpoints, YPoints);
  }

  followLink(newLevel, y, x, n, alternateMode) {
    if (alternateMode === 2) {
      // ON
      this.handleOnMode(newLevel, y, x, n);
    } else if (alternateMode === 1) {
      // OFF
      this.handleOffMode(newLevel, y, x, n);
    } else {
      document.getElementById('w' + y + x + n).className = '';
    }
  }

  handleOnMode(newLevel, y, x, n) {
    let i, j;
    document.getElementById('w' + y + x + n).className = 'fshON';

    for (i = 0; i < 9; i++)
      if (i != x && this.grid.mask(y, i) & (1 << n) && this.bfg[y][i][n] >= 0) {
        // was ==0 but this way chains connect up
        this.bfg[y][i][n] = newLevel;
        this.chainLink(x, y, n, i, y, n, linecols[n]);
      }
    for (j = 0; j < 9; j++)
      if (j != y && this.grid.mask(j, x) & (1 << n) && this.bfg[j][x][n] >= 0) {
        this.bfg[j][x][n] = newLevel;
        this.chainLink(x, y, n, x, j, n, linecols[n]);
      }
    for (j = 0; j < 9; j++)
      for (i = 0; i < 9; i++)
        if (
          !(i == x && j == y) &&
          this.grid.mask(j, i) & (1 << n) &&
          this.grid.box(j, i) == this.grid.box(y, x) &&
          this.bfg[j][i][n] >= 0
        ) {
          this.bfg[j][i][n] = newLevel;
          this.chainLink(x, y, n, i, j, n, linecols[n]);
        }
    if (puztype === 'Sudoku X' && x == y) {
      // Sudoku X diagonal
      for (i = 0; i < 9; i++)
        if (
          i != x &&
          this.grid.mask(i, i) & (1 << n) &&
          this.bfg[i][i][n] >= 0
        ) {
          this.bfg[i][i][n] = newLevel;
          this.chainLink(x, y, n, i, i, n, linecols[n]);
        }
    }
    if (puztype === 'Sudoku X' && x == 8 - y) {
      // Sudoku X diagonal
      for (i = 0; i < 9; i++)
        if (
          i != x &&
          this.grid.mask(8 - i, i) & (1 << n) &&
          this.bfg[8 - i][i][n] >= 0
        ) {
          this.bfg[8 - i][i][n] = newLevel;
          this.chainLink(x, y, n, i, 8 - i, n, linecols[n]);
        }
    }
    if (
      puztype === 'Colour Sudoku' ||
      puztype === 'Windoku' ||
      puztype === 'Stripy'
    )
      // Windoku
      for (j = 0; j < 9; j++)
        for (i = 0; i < 9; i++)
          if (
            !(i == x && j == y) &&
            this.grid.mask(j, i) & (1 << n) &&
            g.win(j, i) == g.win(y, x) &&
            this.bfg[j][i][n] >= 0
          ) {
            console.log('ON ', x, y, n, i, j, this.bfg[j][i][n], newLevel);
            this.bfg[j][i][n] = newLevel;
            this.chainLink(x, y, n, i, j, n, linecols[n]);
            jg.paint();
          }
    if (this.use3DChains) {
      for (let i = 0; i < 9; i++) {
        if (
          i !== n &&
          this.grid.mask(y, x) & (1 << i) &&
          this.bfg[y][x][i] >= 0
        ) {
          this.bfg[y][x][i] = newLevel;
        }
      }
    }
  }

  handleOffMode(newLevel, y, x, n) {
    let i, j, c, x2, y2;
    document.getElementById('w' + y + x + n).className = 'fshOFF';

    for (c = i = 0; i < 9; i++) if (this.grid.mask(y, i) & (1 << n)) c++;
    if (c == 2)
      for (i = 0; i < 9; i++)
        if (
          i != x &&
          this.grid.mask(y, i) & (1 << n) &&
          this.bfg[y][i][n] == 0
        ) {
          this.bfg[y][i][n] = newLevel;
          this.chainLink(x, y, n, i, y, n, '#000000');
        }
    for (c = j = 0; j < 9; j++) if (this.grid.mask(j, x) & (1 << n)) c++;
    if (c == 2)
      for (j = 0; j < 9; j++)
        if (
          j != y &&
          this.grid.mask(j, x) & (1 << n) &&
          this.bfg[j][x][n] == 0
        ) {
          this.bfg[j][x][n] = newLevel;
          this.chainLink(x, y, n, x, j, n, '#000000');
        }
    for (c = j = 0; j < 9; j++)
      for (i = 0; i < 9; i++)
        if (
          this.grid.box(j, i) == this.grid.box(y, x) &&
          this.grid.mask(j, i) & (1 << n)
        )
          c++;
    if (c == 2)
      for (j = 0; j < 9; j++)
        for (i = 0; i < 9; i++)
          if (
            !(i == x && j == y) &&
            this.grid.mask(j, i) & (1 << n) &&
            this.grid.box(j, i) == this.grid.box(y, x) &&
            this.bfg[j][i][n] == 0
          ) {
            this.bfg[j][i][n] = newLevel;
            this.chainLink(x, y, n, i, j, n, '#000000');
          }

    if (puztype === 'Sudoku X' && x == y) {
      // Sudoku X diagonal
      for (c = i = 0; i < 9; i++)
        if (!g.val(i, i) && this.grid.mask(i, i) & (1 << n)) {
          if (x != i) x2 = i;
          if (x != i) y2 = i;
          c++;
        }
      if (c == 2 && this.bfg[y2][x2][n] == 0) {
        this.bfg[y2][x2][n] = newLevel;
        this.chainLink(x, y, n, x2, y2, n, '#000000');
      }
    }
    if (puztype === 'Sudoku X' && 8 - x == y) {
      // Sudoku X diagonal
      for (c = i = 0; i < 9; i++)
        if (!g.val(8 - i, i) && this.grid.mask(8 - i, i) & (1 << n)) {
          if (8 - y != i) x2 = i;
          if (8 - y != i) y2 = 8 - i;
          c++;
        }
      if (c == 2 && this.bfg[y2][x2][n] == 0) {
        this.bfg[y2][x2][n] = newLevel;
        this.chainLink(x, y, n, x2, y2, n, '#000000');
      }
    }
    if (
      puztype === 'Colour Sudoku' ||
      puztype === 'Windoku' ||
      puztype === 'Stripy'
    ) {
      for (c = j = 0; j < 9; j++)
        for (i = 0; i < 9; i++)
          if (
            this.grid.win(j, i) == this.grid.win(y, x) &&
            this.grid.mask(j, i) & (1 << n)
          )
            c++;
      if (c == 2)
        for (j = 0; j < 9; j++)
          for (i = 0; i < 9; i++)
            if (
              !(i == x && j == y) &&
              this.grid.mask(j, i) & (1 << n) &&
              this.grid.win(j, i) == this.grid.win(y, x) &&
              this.bfg[j][i][n] == 0
            ) {
              this.bfg[j][i][n] = newLevel;
              this.chainLink(x, y, n, i, j, n, '#000000');
            }
    }
    if (this.use3DChains && bit_count(this.grid.mask(y, x)) == 2)
      for (i = 0; i < 9; i++)
        if (i != n && this.grid.mask(y, x) & (1 << i) && this.bfg[y][x][i] == 0)
          this.bfg[y][x][i] = newLevel;
  }
  followChain(level, alternateMode) {
    let nothing = false;

    while (!nothing && level < this.curLevel + 20) {
      nothing = true;
      for (let j = 0; j < 9; j++) {
        for (let i = 0; i < 9; i++) {
          for (let n = 0; n < 9; n++) {
            if (this.bfg[j][i][n] === level) {
              nothing = false;
              this.followLink(level + 1, j, i, n, alternateMode);
            }
          }
        }
      }
      level++;
      alternateMode = alternateMode === 2 ? 1 : 2;
    }
    if (level > this.curLevel) this.curLevel = level;
  }
  // EXTERNAL FUNCTIONS
  justDrawBox(cellx1, celly1, cellx2, celly2, colour) {
    let x1, y1, x2, y2, x3, y3, w, h;

    x1 = this.convert_x(cellx1, 0) - 4;
    y1 = this.convert_y(celly1, 0) - 4;
    x3 = this.convert_x(cellx2, 8) + 3;
    y3 = this.convert_y(celly2, 8) + 3;

    x2 = x1 < x3 ? x1 : x3;
    y2 = y1 < y3 ? y1 : y3;
    w = Math.abs(x3 - x1) + 11;
    h = Math.abs(y3 - y1) + 11;

    jg.setColor(colour);
    jg.setStroke(3);
    jg.drawRect(x2, y2, w, h);
    jg.paint();
  }
  check(x, y, n, searchmode) {
    this.bfg = this.initializeBfg();
    this.bfg[y][x][n] = this.curLevel;
    this.followChain(this.curLevel, searchmode); // Assuming it starts with alternateMode 2

    if (searchmode !== 0)
      for (let i = 0; i < 9; i++)
        for (let j = 0; j < 9; j++)
          if (this.grid.hasn(j, i, n) && this.bfg[j][i][n] == 0) {
            document.getElementById('w' + j + i + n).className = 'fshGry';
          }

    jg.paint();
  }

  showChains(focuson) {
    let x, y, n, m, w, i, c;
    let x1, y1, x2, y2, wx, wy, bx, by;
    bx = [
      [0, 1, 2, 0, 1, 2, 0, 1, 2],
      [3, 4, 5, 3, 4, 5, 3, 4, 5],
      [6, 7, 8, 6, 7, 8, 6, 7, 8],
      [0, 1, 2, 0, 1, 2, 0, 1, 2],
      [3, 4, 5, 3, 4, 5, 3, 4, 5],
      [6, 7, 8, 6, 7, 8, 6, 7, 8],
      [0, 1, 2, 0, 1, 2, 0, 1, 2],
      [3, 4, 5, 3, 4, 5, 3, 4, 5],
      [6, 7, 8, 6, 7, 8, 6, 7, 8],
    ];
    by = [
      [0, 0, 0, 1, 1, 1, 2, 2, 2],
      [0, 0, 0, 1, 1, 1, 2, 2, 2],
      [0, 0, 0, 1, 1, 1, 2, 2, 2],
      [3, 3, 3, 4, 4, 4, 5, 5, 5],
      [3, 3, 3, 4, 4, 4, 5, 5, 5],
      [3, 3, 3, 4, 4, 4, 5, 5, 5],
      [6, 6, 6, 7, 7, 7, 8, 8, 8],
      [6, 6, 6, 7, 7, 7, 8, 8, 8],
      [6, 6, 6, 7, 7, 7, 8, 8, 8],
    ];

    if (jig >= 0) {
      for (y = 0; y < 9; y++) for (x = 0; x < 9; x++) bx[y][x] = by[y][x] = 10;

      for (n = 0; n < 9; n++)
        for (m = y = 0; y < 9; y++)
          for (x = 0; x < 9; x++) {
            c = jigsaw_boxes[jig].charAt(y * 9 + x) * 1 - 1;
            if (c == n) {
              bx[n][m] = x;
              by[n][m++] = y;
            }
          }
    }
    //	"111222333111222333111222333444555666444555666444555666777888999777888999777888999", // 0 = SUDOKU

    if (puztype === 'Colour Sudoku')
      wx = [
        [0, 3, 6, 0, 3, 6, 0, 3, 6],
        [1, 4, 7, 1, 4, 7, 1, 4, 7],
        [2, 5, 8, 2, 5, 8, 2, 5, 8],
        [0, 3, 6, 0, 3, 6, 0, 3, 6],
        [1, 4, 7, 1, 4, 7, 1, 4, 7],
        [2, 5, 8, 2, 5, 8, 2, 5, 8],
        [0, 3, 6, 0, 3, 6, 0, 3, 6],
        [1, 4, 7, 1, 4, 7, 1, 4, 7],
        [2, 5, 8, 2, 5, 8, 2, 5, 8],
      ];
    if (puztype === 'Colour Sudoku')
      wy = [
        [0, 0, 0, 3, 3, 3, 6, 6, 6],
        [0, 0, 0, 3, 3, 3, 6, 6, 6],
        [0, 0, 0, 3, 3, 3, 6, 6, 6],
        [1, 1, 1, 4, 4, 4, 7, 7, 7],
        [1, 1, 1, 4, 4, 4, 7, 7, 7],
        [1, 1, 1, 4, 4, 4, 7, 7, 7],
        [2, 2, 2, 5, 5, 5, 8, 8, 8],
        [2, 2, 2, 5, 5, 5, 8, 8, 8],
        [2, 2, 2, 5, 5, 5, 8, 8, 8],
      ];
    if (puztype === 'Windoku')
      wx = [
        [1, 2, 3, 1, 2, 3, 1, 2, 3],
        [5, 6, 7, 5, 6, 7, 5, 6, 7],
        [1, 2, 3, 1, 2, 3, 1, 2, 3],
        [5, 6, 7, 5, 6, 7, 5, 6, 7],
        [1, 2, 3, 1, 2, 3, 1, 2, 3],
        [5, 6, 7, 5, 6, 7, 5, 6, 7],
        [0, 0, 0, 4, 4, 4, 8, 8, 8],
        [0, 0, 0, 4, 4, 4, 8, 8, 8],
        [0, 4, 8, 0, 4, 8, 0, 4, 8],
      ];
    if (puztype === 'Windoku')
      wy = [
        [1, 1, 1, 2, 2, 2, 3, 3, 3],
        [1, 1, 1, 2, 2, 2, 3, 3, 3],
        [5, 5, 5, 6, 6, 6, 7, 7, 7],
        [5, 5, 5, 6, 6, 6, 7, 7, 7],
        [0, 0, 0, 4, 4, 4, 8, 8, 8],
        [0, 0, 0, 4, 4, 4, 8, 8, 8],
        [1, 2, 3, 1, 2, 3, 1, 2, 3],
        [5, 6, 7, 5, 6, 7, 5, 6, 7],
        [0, 0, 0, 4, 4, 4, 8, 8, 8],
      ];
    if (puztype === 'Stripy')
      wx = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [1, 2, 3, 4, 5, 6, 7, 8, 0],
        [2, 3, 4, 5, 6, 7, 8, 0, 1],
        [3, 4, 5, 6, 7, 8, 0, 1, 2],
        [4, 5, 6, 7, 8, 0, 1, 2, 3],
        [5, 6, 7, 8, 0, 1, 2, 3, 4],
        [6, 7, 8, 0, 1, 2, 3, 4, 5],
        [7, 8, 0, 1, 2, 3, 4, 5, 6],
        [8, 0, 1, 2, 3, 4, 5, 6, 7],
      ];
    if (puztype === 'Stripy')
      wy = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
        [0, 1, 2, 3, 4, 5, 6, 7, 8],
      ];

    for (
      n = 0;
      n < 9;
      n++ // .. check each number
    ) {
      if (
        focuson == 0 &&
        document.getElementById('cand' + n) &&
        document.getElementById('cand' + n).checked === false
      )
        continue;
      if (focuson > 0 && n != focuson - 1) continue;

      if (this.showrow || focuson > 0) {
        for (y = 0; y < 9; y++) {
          for (c = x = 0; x < 9; x++)
            if (!g.val(y, x) && g.mask(y, x) & (1 << n)) {
              if (c == 0) x1 = x;
              if (c == 0) y1 = y;
              if (c == 1) x2 = x;
              if (c == 1) y2 = y;
              c++;
            }
          if (c == 2) {
            this.chainLink(x1, y1, n, x2, y2, n, linecols[n]);
            if (!focuson) set_pair_col(y1, x1, y2, x2, n);
          }
        }
      }

      if (this.showbox || focuson > 0) {
        for (w = 0; w < 9; w++) {
          // for each box
          for (c = i = 0; i < 9; i++) {
            // for cell in each box
            if (
              !g.val(by[w][i], bx[w][i]) &&
              g.mask(by[w][i], bx[w][i]) & (1 << n)
            ) {
              if (c == 0) x1 = bx[w][i];
              if (c == 0) y1 = by[w][i];
              if (c == 1) x2 = bx[w][i];
              if (c == 1) y2 = by[w][i];
              c++;
            }
          }
          if (c == 2) {
            this.chainLink(x1, y1, n, x2, y2, n, linecols[n]);
            if (!focuson) set_pair_col(y1, x1, y2, x2, n);
          }
        }
      }

      if (this.showcol || focuson > 0) {
        for (x = 0; x < 9; x++) {
          for (c = y = 0; y < 9; y++)
            if (!g.val(y, x) && g.mask(y, x) & (1 << n)) {
              if (c == 0) x1 = x;
              if (c == 0) y1 = y;
              if (c == 1) x2 = x;
              if (c == 1) y2 = y;
              c++;
            }
          if (c == 2) {
            this.chainLink(x1, y1, n, x2, y2, n, linecols[n]);
            if (!focuson) set_pair_col(y1, x1, y2, x2, n);
          }
        }
      }
      if (this.showwin) {
        for (w = 0; w < 9; w++) {
          // for each window
          for (c = i = 0; i < 9; i++) {
            // for cell in each window
            if (
              !g.val(wy[w][i], wx[w][i]) &&
              g.mask(wy[w][i], wx[w][i]) & (1 << n)
            ) {
              if (c == 0) x1 = wx[w][i];
              if (c == 0) y1 = wy[w][i];
              if (c == 1) x2 = wx[w][i];
              if (c == 1) y2 = wy[w][i];
              c++;
            }
          }
          if (c == 2) {
            this.chainLink(x1, y1, n, x2, y2, n, linecols[n]);
            if (!focuson) set_pair_col(y1, x1, y2, x2, n);
          }
        }
      }
      if (this.showdiag) {
        for (c = x = 0; x < 9; x++)
          if (!g.val(x, x) && g.mask(x, x) & (1 << n)) {
            if (c == 0) x1 = x;
            if (c == 0) y1 = x;
            if (c == 1) x2 = x;
            if (c == 1) y2 = x;
            c++;
          }
        if (c == 2) {
          this.chainLink(x1, y1, n, x2, y2, n, linecols[n]);
          if (!focuson) set_pair_col(y1, x1, y2, x2, n);
        }
        for (c = x = 0; x < 9; x++)
          if (!g.val(8 - x, x) && g.mask(8 - x, x) & (1 << n)) {
            if (c == 0) x1 = x;
            if (c == 0) y1 = 8 - x;
            if (c == 1) x2 = x;
            if (c == 1) y2 = 8 - x;
            c++;
          }
        if (c == 2) {
          this.chainLink(x1, y1, n, x2, y2, n, linecols[n]);
          if (!focuson) set_pair_col(y1, x1, y2, x2, n);
        }
      }
    }
    jg.paint();
  }
  parsePOMset(s, n) {
    let i, p, x1, x2, y, y1, y2, f;

    for (y = 0; y < 9; y++) for (x1 = 0; x1 < 9; x1++) g.c(y, x1).cid = 0;

    // This nasty beast takes a series of 9-strings and draws a line from row A to J
    // skipping any row set to X position = 0
    n--;
    for (i = p = 0; p < s.length; p += 9, i++) {
      y2 = 0;
      let col = 0;
      for (y1 = y2; y1 < 8; y1++) {
        let done = false;
        for (y2 = y1 + 1; y2 < 9 && !done; y2++) {
          x1 = s.charAt(p + y1) - 1;
          x2 = s.charAt(p + y2) - 1;
          if (x1 >= 0 && x2 >= 0) {
            if (!col) col = x1 + 1;
            //console.log(y + ' ' + x1 + ' ' + x2 + ' ' + i);
            if (g.mask(y1, x1) & (1 << n) && g.mask(y2, x2) & (1 << n)) {
              f = document.getElementById('w' + y1 + x1 + n);
              if (f) f.className = 'fsh' + (col - 1);
              g.c(y1, x1).cid = col;
              f = document.getElementById('w' + y2 + x2 + n);
              if (f) f.className = 'fsh' + (col - 1);
              this.chainLink(x1, y1, n, x2, y2, n, linecols[col - 1]);
            }
            done = true;
          }
        }
      }
    }
    jg.paint();
  }
  parseChain(chain, maincolor) {
    let c,
      c2,
      i,
      n,
      inside,
      strong,
      stack = 0;
    let xo,
      yo,
      no,
      oldn = 0,
      x = [0, 0, 0, 0, 0, 0, 0, 0],
      y = [0, 0, 0, 0, 0, 0, 0, 0],
      many = 0;

    strong = inside = false;

    for (i = 0; i < chain.length; i++) {
      c = chain.charAt(i, 1);
      c2 = chain.charAt(i + 1, 1);
      if (c == '[' || c == '{') inside = true;
      else if (c == ']' || c == '}') {
        inside = false;
        if (!many) {
          this.ringCandidate(x[0], y[0], n - 1, maincolor, strong);
          if (stack > 1) {
            this.connectCandidates(
              xo,
              yo,
              no,
              x[many],
              y[many],
              n - 1,
              strong,
              maincolor,
              '#ff8800'
            );
          }
        } // cope with ALS
        else {
          this.ringALS(x[0], y[0], x[1], y[1], n - 1, maincolor, strong);
          if (many > 1)
            this.ringALS(x[1], y[1], x[2], y[2], n - 1, maincolor, strong);
          if (many > 2)
            this.ringALS(x[2], y[2], x[3], y[3], n - 1, maincolor, strong);

          //	for(j=0;j<=many;j++)
          //		ringCandidate(x[j],y[j],n-1,"#ff0000");

          if (stack > 1) {
            x[0] = (x[0] + x[1]) / 2;
            y[0] = (y[0] + y[1]) / 2;
            this.connectCandidates(
              xo,
              yo,
              no,
              x[0],
              y[0],
              n - 1,
              strong,
              maincolor,
              '#ff8800'
            );
          }
        }
        xo = x[0];
        yo = y[0];
        many = 0;
      } else if (c == '+') strong = true;
      else if (c == '-') strong = false;
      else if (c == '|') many++;
      else if (c == '(') {
        // UR as chain link

        if (c2 == 'X') {
          // -4(XW[-F4/-G4+G2-F2])
          c = chain.charAt(i + 5, 1);
          y[0] = c.charCodeAt(0) - 65;
          if (y[0] == 9) y[0] = 8;
          c = chain.charAt(i + 6, 1);
          x[0] = parseInt(c, 10) - 1;

          c = chain.charAt(i + 9, 1);
          y[1] = c.charCodeAt(0) - 65;
          if (y[1] == 9) y[1] = 8;
          c = chain.charAt(i + 10, 1);
          x[1] = parseInt(c, 10) - 1;

          c = chain.charAt(i + 12, 1);
          y[2] = c.charCodeAt(0) - 65;
          if (y[2] == 9) y[2] = 8;
          c = chain.charAt(i + 13, 1);
          x[2] = parseInt(c, 10) - 1;

          c = chain.charAt(i + 15, 1);
          y[3] = c.charCodeAt(0) - 65;
          if (y[3] == 9) y[3] = 8;
          c = chain.charAt(i + 16, 1);
          x[3] = parseInt(c, 10) - 1;

          this.connectCandidates(
            xo,
            yo,
            oldn,
            x[0],
            y[0],
            n - 1,
            false,
            maincolor,
            '#ff8800'
          );
          this.ringALS(x[0], y[0], x[2], y[2], n - 1, maincolor, strong);
          this.onOffColor(x[0], y[0], n - 1, false);
          this.onOffColor(x[1], y[1], n - 1, false);
          this.onOffColor(x[2], y[2], n - 1, true);
          this.onOffColor(x[3], y[3], n - 1, false);

          xo = x[3];
          yo = y[3];
          i += 18;
        } else {
          c = chain.charAt(i + 4, 1);
          y[1] = c.charCodeAt(0) - 65;
          if (y[1] == 9) y[1] = 8;
          c = chain.charAt(i + 6, 1);
          x[1] = parseInt(c, 10) - 1;

          c = chain.charAt(i + 5, 1);
          y[2] = c.charCodeAt(0) - 65;
          if (y[2] == 9) y[2] = 8;
          c = chain.charAt(i + 7, 1);
          x[2] = parseInt(c, 10) - 1;

          //		ringALS( x[1],y[1], x[2],y[2], n-1, maincolor,strong);

          if (g.mask(y[1], x[1]) & (1 << no)) {
            y[0] = y[1];
            x[0] = x[1];
          }
          if (g.mask(y[1], x[2]) & (1 << no)) {
            y[0] = y[1];
            x[0] = x[2];
          }
          if (g.mask(y[2], x[1]) & (1 << no)) {
            y[0] = y[2];
            x[0] = x[1];
          }
          if (g.mask(y[2], x[2]) & (1 << no)) {
            y[0] = y[2];
            x[0] = x[2];
          }

          document.getElementById('a' + y[1] + x[1]).style.backgroundColor =
            sq_col[5];
          document.getElementById('a' + y[2] + x[1]).style.backgroundColor =
            sq_col[5];
          document.getElementById('a' + y[1] + x[2]).style.backgroundColor =
            sq_col[5];
          document.getElementById('a' + y[2] + x[2]).style.backgroundColor =
            sq_col[5];

          this.connectCandidates(
            xo,
            yo,
            oldn,
            x[0],
            y[0],
            n - 1,
            false,
            maincolor,
            '#ff8800'
          );
          this.ringCandidate(x[0], y[0], n - 1, maincolor, strong);

          xo = x[0];
          yo = y[0];
          i += 9;
        }
        many = 0;
      } else if (c != ' ') {
        if (inside) {
          if (c == 'A' && c2 == 'L') {
            i += 3;
          } else {
            if (!many) {
              xo = x[0];
              yo = y[0];
            }
            if (!coordmode) {
              c = chain.charAt(i + 1, 1);
              c2 = chain.charAt(i + 3, 1);
              y[many] = parseInt(c, 10) - 1;
              x[many] = parseInt(c2, 10) - 1;
              i += 3;
            } else {
              y[many] = c.charCodeAt(0) - 65;
              if (y[many] == 9) y[many] = 8;
              x[many] = parseInt(c2, 10) - 1;
              i++;
            }
            stack++;
          }
        } else {
          oldn = n - 1;
          no = n - 1;
          n = parseInt(c, 10);
        }
      }
    }
  }
}
function just_a_box(cellx1, celly1, cellx2, celly2, colour) {
  const analyzer = new ChainAnalyzer(g, false, puztype == 'Killer Jigsaw');
  analyzer.justDrawBox(cellx1 * 1, celly1 * 1, cellx2 * 1, celly2 * 1, colour);
}
function show_chains(focuson) {
  const analyzer = new ChainAnalyzer(g, false, puztype == 'Killer Jigsaw');

  if (puztype !== 'Killer' && puztype !== 'Killer Jigsaw') {
    // not killer
    analyzer.showbox =
      focuson > 0 || document.getElementById('showbox').checked;
    analyzer.showrow =
      focuson > 0 || document.getElementById('showrow').checked;
    analyzer.showcol =
      focuson > 0 || document.getElementById('showcol').checked;
    analyzer.showwin =
      (puztype === 'Colour Sudoku' ||
        puztype === 'Windoku' ||
        puztype === 'Stripy') &&
      (focuson > 0 || document.getElementById('showwin').checked);
    analyzer.showdiag =
      puztype === 'Sudoku X' &&
      (focuson > 0 || document.getElementById('showdiag').checked);
  }
  clear_on_off_color();
  analyzer.showChains(focuson);
}
function parse_pom_set(s, n) {
  const analyzer = new ChainAnalyzer(g, false);
  analyzer.parsePOMset(s, n);
}
function parsemychain(chain, maincolor) {
  const analyzer = new ChainAnalyzer(g, false);
  analyzer.parseChain(chain, maincolor);
}
function set_pair_col(y1, x1, y2, x2, n) {
  let f = document.getElementById('w' + y1 + x1 + n);
  if (f) f.className = 'fsh' + n;
  f = document.getElementById('w' + y2 + x2 + n);
  if (f) f.className = 'fsh' + n;
}
/* 2d array map example
var scores = [[2, 7], [13, 47], [55, 77]];
scores.map(function(subarray) {
  return subarray.map(function(number) {
    return number * 3;
  })
})
*/

function save_unchecked() {
  for (let i = 3; i < strat_list.length; i++) {
    if (document.getElementById('CB' + strat_list[i])) {
      if (document.getElementById('CB' + strat_list[i]).checked)
        arr_unchecked_strats.popIfExist(strat_list[i]);
      else arr_unchecked_strats.pushIfNotExist(strat_list[i]);
    }
  }
  cookie.create('strats_unchecked', arr_unchecked_strats, 90);
}
function load_unchecked() {
  if (document.getElementById('colpicker0')) {
    for (let i = 0; i < digitcols.length; i++)
      document.getElementById('colpicker' + i).style.backgroundColor =
        digitcols[i];
    document.getElementById('colpicker0').style.border = '1px dashed red';
  }
  selectedColour = 0;

  let s = cookie.read('strats_unchecked');
  if (s == null) return;
  if (s.length == 0) return;
  arr_unchecked_strats = s.split(',');
  for (let i = 3; i < strat_list.length; i++) {
    if (document.getElementById('CB' + strat_list[i]))
      //alert("no " + strat_list[i]);
      document.getElementById('CB' + strat_list[i]).checked =
        !arr_unchecked_strats.inArray(strat_list[i]);
  }
}
function send_to_player() {
  let i,
    j,
    n,
    h,
    s = '';
  for (j = 0; j < 9; j++)
    for (i = 0; i < 9; i++) {
      let cc = g.c(j, i);
      n = cc.val ? g.valbit(j, i) : cc.mask;
      n = (n << 1) + (cc.clue ? 1 : 0); // shift to make room for one more bit
      h = n.toString(32);
      if (h.length < 2) h = '0' + h;
      s += h;
    }
  location.href = '/Sudoku_player?bd=' + s;
}
function populate_player() {
  if (location.search.substring(0, 3) !== 'bd=') return;

  alert(location.search);
  //	document.getElementById('ASSudoku').src = 'ASSudokuASPX.aspx?' + s;"
}
function display_chain_cycle() {
  let doc = undefined;
  if (!document.ifrm) doc = document.getElementById('ifrm').contentDocument;
  else doc = document.ifrm.document;
  if (!doc) return;
  if (!doc.getElementById('chaincycle')) {
    manyChains = 0;
    curChain = 1;
  } else {
    let chaincycle = doc.getElementById('chaincycle');
    chaincycle.innerHTML =
      manyChains < 2
        ? ''
        : '<br><hr>Explore ' +
          (manyChains - 1) +
          ' other chains ' +
          '<input type="button" class="class="BButton" value="&lt;" onclick="top.cycle_chains(-1)" />&nbsp;' +
          curChain +
          '/' +
          manyChains +
          '&nbsp;' +
          '<input type="button" class="class="BButton" value="&gt;" onclick="top.cycle_chains(1)" />';
  }
}
function set_chain_cycles() {
  let doc = undefined;
  if (!document.ifrm) doc = document.getElementById('ifrm').contentDocument;
  else doc = document.ifrm.document;
  if (!doc) return;

  if (!doc.getElementById('manyChains')) {
    manyChains = 0;
  } else {
    manyChains = doc.getElementById('manyChains').value * 1;
  }
  display_chain_cycle();
}
function pickcol(w) {
  document.getElementById('colpicker' + selectedColour).style.border =
    '1px solid white	';
  selectedColour = w;
  document.getElementById('colpicker' + w).style.border = '1px dashed red';
}
function err_square(x, y, val) {
  let t = document.getElementById('a' + y + x);
  t.style.backgroundColor = g.backgroundColor(y, x);
  t.style.color = 'blue';
  t.style.fontSize = '16pt';
  t.innerHTML =
    '<div style="width:30px;height:25px;border-radius:10px;background-color:#ff0000;margin:auto auto;pointer-events:none;">' +
    val +
    '</div>';
}
function PrintForumSudoku() {
  let x, y, i, s, h;
  let n = [0, 0, 0, 0, 0, 0, 0, 0, 0];

  for (x = 0; x < 9; x++) {
    n[x] = 3;
    for (y = 0; y < 9; y++) {
      h = bit_count(g.val(y, x) ? g.valbit(y, x) : g.mask(y, x));
      if (h > n[x]) n[x] = h;
    }
    n[x]++;
  }

  s = '+-';
  for (x = 0; x < 9; x++) {
    for (i = 0; i < n[x]; i++) s += '-';
    if (x == 2 || x == 5) s += '-+-';
  }
  s += '-+\n';
  for (y = 0; y < 9; y++) {
    s += '| ';
    for (x = 0; x < 9; x++) {
      h = g.val(y, x) ? g.valbit(y, x) : g.mask(y, x);
      for (i = 1; i < 10; i++) if (h & (1 << (i - 1))) s += i;
      h = bit_count(h);
      //console.log((g.val(y, x) ? g.valbit(y, x) : g.mask(y, x)) + " - " + h);
      for (i = 0; i < n[x] - h; i++) s += ' ';
      if (x == 2 || x == 5) s += ' | ';
    }
    s += ' |\n';
    if (y == 2 || y == 5 || y == 8) {
      s += '+-';
      for (x = 0; x < 9; x++) {
        for (i = 0; i < n[x]; i++) s += '-';
        if (x == 2 || x == 5) s += '-+-';
      }
      s += '-+\n';
    }
  }
  return s;
}
