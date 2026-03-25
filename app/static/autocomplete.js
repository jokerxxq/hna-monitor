// ---- 城市数据库 ----
const CITIES = [
  {code:"PEK",name:"北京首都",py:"beijing bj"},
  {code:"PKX",name:"北京大兴",py:"beijing daxing bj"},
  {code:"SHA",name:"上海虹桥",py:"shanghai hongqiao sh"},
  {code:"PVG",name:"上海浦东",py:"shanghai pudong sh"},
  {code:"CAN",name:"广州",py:"guangzhou gz"},
  {code:"SZX",name:"深圳",py:"shenzhen sz"},
  {code:"CTU",name:"成都天府",py:"chengdu tianfu cd"},
  {code:"TFU",name:"成都双流",py:"chengdu shuangliu cd"},
  {code:"HAK",name:"海口",py:"haikou hk"},
  {code:"SYX",name:"三亚",py:"sanya sy"},
  {code:"WUH",name:"武汉",py:"wuhan wh"},
  {code:"CSX",name:"长沙",py:"changsha cs"},
  {code:"HGH",name:"杭州",py:"hangzhou hz"},
  {code:"NKG",name:"南京",py:"nanjing nj"},
  {code:"XMN",name:"厦门",py:"xiamen xm"},
  {code:"FOC",name:"福州",py:"fuzhou fz"},
  {code:"TAO",name:"青岛",py:"qingdao qd"},
  {code:"TNA",name:"济南",py:"jinan jn"},
  {code:"TSN",name:"天津",py:"tianjin tj"},
  {code:"DLC",name:"大连",py:"dalian dl"},
  {code:"SHE",name:"沈阳",py:"shenyang sy"},
  {code:"HRB",name:"哈尔滨",py:"haerbin heb"},
  {code:"CGQ",name:"长春",py:"changchun cc"},
  {code:"XIY",name:"西安",py:"xian xa"},
  {code:"KMG",name:"昆明",py:"kunming km"},
  {code:"NNG",name:"南宁",py:"nanning nn"},
  {code:"KWE",name:"贵阳",py:"guiyang gy"},
  {code:"KHN",name:"南昌",py:"nanchang nc"},
  {code:"CGO",name:"郑州",py:"zhengzhou zz"},
  {code:"TYN",name:"太原",py:"taiyuan ty"},
  {code:"SJW",name:"石家庄",py:"shijiazhuang sjz"},
  {code:"HFE",name:"合肥",py:"hefei hf"},
  {code:"NGB",name:"宁波",py:"ningbo nb"},
  {code:"WNZ",name:"温州",py:"wenzhou wz"},
  {code:"ZUH",name:"珠海",py:"zhuhai zh"},
  {code:"SWA",name:"揭阳",py:"jieyang jy"},
  {code:"URC",name:"乌鲁木齐",py:"wulumuqi urumqi wlmq"},
  {code:"LHW",name:"兰州",py:"lanzhou lz"},
  {code:"XNN",name:"西宁",py:"xining xn"},
  {code:"INC",name:"银川",py:"yinchuan yc"},
  {code:"HET",name:"呼和浩特",py:"huhehaote hhht"},
  {code:"BAV",name:"包头",py:"baotou bt"},
  {code:"WEH",name:"威海",py:"weihai wh"},
  {code:"YNT",name:"烟台",py:"yantai yt"},
  {code:"WUX",name:"无锡",py:"wuxi wx"},
  {code:"HYN",name:"台州",py:"taizhou tz"},
  {code:"LJG",name:"丽江",py:"lijiang lj"},
  {code:"DLU",name:"大理",py:"dali dl"},
  {code:"TXN",name:"黄山",py:"huangshan hs"},
  {code:"ENH",name:"恩施",py:"enshi es"},
  {code:"ZYI",name:"遵义",py:"zunyi zy"},
  {code:"MIG",name:"绵阳",py:"mianyang my"},
  {code:"YIH",name:"宜昌",py:"yichang yc"},
  {code:"JJN",name:"晋江泉州",py:"jinjiang quanzhou jj"},
  {code:"CKG",name:"重庆",py:"chongqing cq"},
  {code:"KHG",name:"喀什",py:"kashi ks"},
  {code:"AKU",name:"阿克苏",py:"akesu aks"},
  {code:"HLD",name:"海拉尔",py:"hailaer hle"},
  {code:"LYA",name:"洛阳",py:"luoyang ly"},
  {code:"YLN",name:"延吉",py:"yanji yj"},
];

function matchCities(q) {
  if (!q || q.trim() === '') return [];
  const raw = q.trim();
  const lq = raw.toLowerCase();
  const uq = raw.toUpperCase();

  const scored = CITIES.map(c => {
    // 精确三字码匹配 — 最高优先级
    if (c.code === uq) return { c, score: 100 };
    // 三字码前缀
    if (c.code.startsWith(uq)) return { c, score: 90 };
    // 城市名完全包含
    if (c.name.includes(raw)) return { c, score: 80 };
    // 拼音完整词匹配
    const pyWords = c.py.split(' ');
    if (pyWords.some(p => p === lq)) return { c, score: 70 };
    // 拼音前缀
    if (pyWords.some(p => p.startsWith(lq))) return { c, score: 60 };
    return null;
  }).filter(Boolean);

  scored.sort((a, b) => b.score - a.score);
  return scored.map(s => s.c).slice(0, 8);
}

function initAC(labelId, listId, hiddenId) {
  const input  = document.getElementById(labelId);
  const list   = document.getElementById(listId);
  const hidden = document.getElementById(hiddenId);

  function hideList() {
    list.style.display = 'none';
    list.innerHTML = '';
  }

  function selectCity(c) {
    input.value  = `${c.name} (${c.code})`;
    hidden.value = c.code;
    input.dataset.confirmed = '1';
    hideList();
  }

  function renderList(matches) {
    list.innerHTML = '';
    if (!matches.length) { hideList(); return; }
    matches.forEach(c => {
      const li = document.createElement('li');
      li.innerHTML = `<span class="ac-name">${c.name}</span><span class="ac-code">${c.code}</span>`;
      li.addEventListener('mousedown', e => {
        e.preventDefault();
        selectCity(c);
      });
      list.appendChild(li);
    });
    list.style.display = 'block';
  }

  input.addEventListener('input', () => {
    hidden.value = '';
    input.dataset.confirmed = '';
    const matches = matchCities(input.value);
    renderList(matches);
  });

  input.addEventListener('focus', () => {
    // 重新聚焦时如果内容不为空，再次触发搜索
    if (input.value.trim() && !hidden.value) {
      const matches = matchCities(input.value);
      renderList(matches);
    }
  });

  input.addEventListener('blur', () => {
    setTimeout(() => {
      // blur 后尝试从输入内容自动补全（允许直接输入三字码）
      if (!hidden.value) {
        const upper = input.value.trim().toUpperCase();
        const exact = CITIES.find(c => c.code === upper);
        if (exact) {
          selectCity(exact);
        }
      }
      hideList();
    }, 180);
  });

  // 键盘导航
  input.addEventListener('keydown', e => {
    const items = list.querySelectorAll('li');
    const active = list.querySelector('li.active');
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (!active) {
        items[0] && items[0].classList.add('active');
      } else {
        const next = active.nextElementSibling;
        active.classList.remove('active');
        if (next) next.classList.add('active');
        else items[0] && items[0].classList.add('active');
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (active) {
        const prev = active.previousElementSibling;
        active.classList.remove('active');
        if (prev) prev.classList.add('active');
        else items[items.length - 1] && items[items.length - 1].classList.add('active');
      }
    } else if (e.key === 'Enter') {
      if (active) {
        e.preventDefault();
        const idx = Array.from(items).indexOf(active);
        const matches = matchCities(input.value);
        if (matches[idx]) selectCity(matches[idx]);
      }
    } else if (e.key === 'Escape') {
      hideList();
    }
  });
}

function validateAC(form) {
  const originHidden = form.querySelector('#origin_code');
  const destHidden   = form.querySelector('#dest_code');
  if (!originHidden.value) {
    showFieldError('origin_label', '请从下拉列表选择出发城市，或直接输入三字码（如 SZX）');
    return false;
  }
  if (!destHidden.value) {
    showFieldError('dest_label', '请从下拉列表选择到达城市，或直接输入三字码（如 HAK）');
    return false;
  }
  return true;
}

function showFieldError(inputId, msg) {
  const el = document.getElementById(inputId);
  if (!el) return;
  el.classList.add('input-error');
  let tip = el.parentElement.querySelector('.field-error-tip');
  if (!tip) {
    tip = document.createElement('span');
    tip.className = 'field-error-tip';
    el.parentElement.appendChild(tip);
  }
  tip.textContent = msg;
  el.focus();
  el.addEventListener('input', () => {
    el.classList.remove('input-error');
    tip.textContent = '';
  }, { once: true });
}

// 初始化
window.addEventListener('DOMContentLoaded', () => {
  initAC('origin_label', 'origin_list', 'origin_code');
  initAC('dest_label',   'dest_list',   'dest_code');

  // 日期最小值设为今天
  const dateInput = document.querySelector('input[name="travel_date"]');
  if (dateInput) {
    const today = new Date().toISOString().slice(0, 10);
    if (!dateInput.min) dateInput.min = today;
    if (!dateInput.value) dateInput.value = today;
  }

  const form = document.querySelector('form[action="/tasks"]');
  if (form) {
    form.addEventListener('submit', e => {
      if (!validateAC(form)) e.preventDefault();
    });
  }
});
