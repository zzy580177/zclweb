// px转rem
function pxTurnRem(pxStr) {
	var page = document.documentElement;
	page.style.padding = 0;
	page.style.margin = 0;
	document.body.style.padding = 0;
	document.body.style.margin = 0;
	var pageW = document.body.clientWidth;
	var fz = (pageW / pxStr) * 100;
	page.style.fontSize = fz + 'px';
}
pxTurnRem(1920)

function notEnlarge() {
	// 禁用双指放大
	document.documentElement.addEventListener(
		'touchstart',
		function(event) {
			if (event.touches.length > 1) {
				event.preventDefault()
			}
		}, {
			passive: false
		}
	)

	// 禁用双击放大
	var lastTouchEnd = 0
	document.documentElement.addEventListener(
		'touchend',
		function(event) {
			var now = Date.now()
			if (now - lastTouchEnd <= 300) {
				event.preventDefault()
			}
			lastTouchEnd = now
		}, {
			passive: false
		}
	)
}
notEnlarge();

function copy(str) {
	var _input = document.createElement("input"); // 直接构建input
	_input.style.fontSize = '12px';
	_input.value = str; // 设置内容
	document.body.appendChild(_input); // 添加临时实例
	_input.select(); // 选择实例内容
	document.execCommand("Copy"); // 执行复制
	document.body.removeChild(_input); // 删除临时实例
	alert('复制成功！');
}

function goPage(str) {
	if (!str) { // 弹框暂未开放
		window.history.back(-1);
		return false;
	}
	window.location.href = str;
}



function closeOpen() {
	document.getElementById('notOpen').style.display = 'none';
}


function changeIdKey(key) {
	let menuDsy = document.getElementById(key).style.display;
	if (menuDsy == 'none') {
		openIdKey(key);
	} else {
		closeIdKey(key);

	}
}

function openIdKey(key) {
	document.getElementById(key).style.display = 'block';
}

function closeIdKey(key) {
	document.getElementById(key).style.display = 'none';
}


function changeTip(key) {
	let menuDsy = document.getElementById(key).style.display;
	if (menuDsy == 'none') {
		openTip(key);
	} else {
		closeTip(key);

	}
}

function openTip(key) {
	document.getElementById(key).style.display = 'flex';
}

function closeTip(key) {
	document.getElementById(key).style.display = 'none';
}

function timeChange(sec) {
	var hour = parseInt(sec / (60 * 60));
	hour = hour > 9 ? hour : '0' + hour;
	var minute = parseInt(sec % (60 * 60) / 60);
	minute = minute > 9 ? minute : '0' + minute;
	var second = parseInt(sec % (60 * 60) % 60);
	second = second > 9 ? second : '0' + second;
	return hour + ':' + minute + ':' + second;
}

function copy(message) {
	var input = document.createElement("input");
	input.value = message;
	document.body.appendChild(input);
	input.select();
	input.setSelectionRange(0, input.value.length), document.execCommand('Copy');
	document.body.removeChild(input);
	alert("复制成功");
}

