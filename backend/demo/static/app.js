'use strict';

const $ = id => document.getElementById(id);
const state = {
  data: null, accounts: [], kiosk: null, resident: null, residentInfo: null,
  ownParcels: [], session: null, busy: false, lockerSignature: '', serverOffset: 0,
};
const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const short = id => id ? id.slice(0, 8) : '—';
const time = seconds => new Intl.DateTimeFormat('vi-VN', {timeStyle: 'medium'}).format(new Date(seconds * 1000));
const errors = {
  no_suitable_locker: 'Không có ngăn phù hợp. Kiểm tra kết nối Node và trạng thái hai ngăn.',
  recipient_not_found: 'Mã phòng và số điện thoại không khớp cư dân có sẵn.',
  node_offline: 'Locker Node đang offline. Hãy kết nối Node trước.',
  invalid_credentials: 'Tên đăng nhập hoặc mật khẩu không đúng.',
  invalid_kiosk_session: 'Phiên kiosk đã hết hạn, đã dùng, bị khóa hoặc không đúng đơn.',
  invalid_kiosk_code: 'Mã kiosk không đúng. Sau 5 lần sai, phiên bị khóa.',
  not_parcel_owner: 'Cư dân này không phải chủ đơn.',
  command_not_requested: 'Backend chưa có lệnh này. Hoàn thành các bước cần thiết trước.',
  invalid_command_result: 'Lệnh đã áp dụng hoặc không khớp phiên.',
  missing_door_open: 'Cần có tín hiệu cửa OPEN trước CLOSED trong đúng phiên.',
  unlock_not_applied: 'Hãy xác nhận UNLOCK_APPLIED trước khi gửi tín hiệu cửa.',
  transaction_not_pending: 'Phiên không còn pending. Phiên lỗi cần reset demo để bắt đầu lại.',
  invalid_state_transition: 'Trạng thái hiện tại không cho phép thao tác này.',
  lock_requires_closed_door: 'Cần đóng cửa trước khi áp dụng LOCK.',
  stale_device_event: 'Dữ liệu thiết bị đã cũ. Gửi snapshot CLOSED mới bằng nút thủ công.',
  invalid_or_expired_token: 'Phiên đăng nhập hết hạn. Tải lại trang hoặc đăng nhập cư dân lại.',
};

async function request(path, {method = 'GET', body, token} = {}) {
  const headers = {'X-Demo-Control': '1'};
  if (token) headers.Authorization = `Bearer ${token}`;
  if (method !== 'GET') headers['X-Request-ID'] = crypto.randomUUID();
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  const response = await fetch(path, {method, headers, body: body === undefined ? undefined : JSON.stringify(body), cache: 'no-store'});
  const data = await response.json();
  if (!response.ok) {
    const detail = typeof data.detail === 'string' ? data.detail : 'Dữ liệu không hợp lệ. Kiểm tra lại thông tin nhập.';
    throw new Error(errors[detail] || detail);
  }
  return data;
}

let toastTimer;
function toast(message, isError = false) {
  clearTimeout(toastTimer);
  $('toast').textContent = message;
  $('toast').className = 'toast' + (isError ? ' error' : '');
  $('toast').hidden = false;
  toastTimer = setTimeout(() => { $('toast').hidden = true; }, isError ? 9000 : 5000);
}

async function action(work) {
  if (state.busy) return;
  state.busy = true;
  document.body.setAttribute('aria-busy', 'true');
  try {
    const message = await work();
    await refresh();
    if (message) toast(message);
  } catch (error) {
    toast(error.message, true);
    try { await refresh(); } catch { /* A connection banner already explains the failure. */ }
  } finally {
    state.busy = false;
    document.body.removeAttribute('aria-busy');
  }
}

async function authenticate(account) {
  const result = await request('/api/v1/auth/login', {method: 'POST', body: {username: account.username, password: account.password}});
  return result.access_token;
}

async function bootstrap() {
  const data = await request('/demo/bootstrap');
  state.accounts = data.accounts;
  state.kiosk = await authenticate(state.accounts.find(a => a.role === 'KIOSK'));
  $('kiosk-auth').textContent = 'Kiosk đã đăng nhập';
  const residents = state.accounts.filter(a => a.role === 'RESIDENT');
  $('demo-accounts').innerHTML = residents.map(a => `<div class="account-entry"><strong>${escapeHTML(a.username)}</strong> · Phòng ${escapeHTML(a.room_code)} · ${escapeHTML(a.phone)}<br>Mật khẩu: <code>${escapeHTML(a.password)}</code></div>`).join('');
  $('resident-password').value = residents[0].password;
  $('resident-username').value = residents[0].username;
  state.resident = null;
  state.residentInfo = null;
  state.ownParcels = [];
  state.session = null;
  $('pickup-code').value = '';
  $('resident-auth').textContent = 'Chưa đăng nhập';
  $('resident-auth').className = 'pill neutral';
}

function options(id, items, placeholder, autoSelect = true) {
  const select = $(id);
  const old = select.value;
  const html = `<option value="">${escapeHTML(placeholder)}</option>` + items.map(item => `<option value="${escapeHTML(item.id)}">${escapeHTML(item.label)}</option>`).join('');
  if (select.innerHTML !== html) {
    select.innerHTML = html;
    select.value = items.some(item => item.id === old) ? old : (autoSelect && items.length === 1 ? items[0].id : '');
  }
}

function pill(status) {
  const colors = {AVAILABLE: 'good', STORED: 'good', COMPLETED: 'good', OCCUPIED: 'good',
    RESERVED: 'waiting', CREATED: 'waiting', PENDING: 'waiting', PICKUP_PENDING: 'working',
    DEPOSITING: 'working', COLLECTING: 'working', UNKNOWN: 'bad', EXCEPTION: 'bad', FAULT: 'bad'};
  return `<span class="pill ${colors[status] || 'neutral'}">${escapeHTML(status)}</span>`;
}

function renderLockers() {
  const data = state.data;
  const signature = JSON.stringify([data.lockers, data.transactions, data.commands, data.demo_hardware]);
  if (signature === state.lockerSignature) return;
  state.lockerSignature = signature;
  $('lockers').innerHTML = data.lockers.map(locker => {
    const tx = data.transactions.find(t => t.locker_id === locker.id && t.active)
      || data.transactions.filter(t => t.locker_id === locker.id).at(-1);
    const hardware = data.demo_hardware.find(h => h.locker_id === locker.id);
    const commands = data.commands.filter(c => c.transaction_id === tx?.id);
    const pending = Boolean(tx && tx.status === 'PENDING' && locker.online);
    const unlock = commands.find(c => c.action === 'UNLOCK');
    const lock = commands.find(c => c.action === 'LOCK');
    const evidence = [
      ['UNLOCK', unlock?.status === 'APPLIED'], ['OPEN', tx?.opened_sequence != null],
      ['CLOSED', tx?.closed_sequence != null], ['CONFIRM', Boolean(tx?.confirmed)], ['LOCK', lock?.status === 'APPLIED'],
    ];
    const button = (kind, text, enabled, style = 'ghost') => `<button class="button ${style}" type="button" data-locker="${locker.id}" data-kind="${kind}" data-tx="${escapeHTML(tx?.id || '')}" ${enabled ? '' : 'disabled'}>${text}</button>`;
    return `<article class="locker-card">
      <div class="locker-header"><div class="locker-title"><h3>${locker.id}</h3><span class="size-badge">SIZE ${locker.size}</span></div>${pill(locker.state)}</div>
      <div class="locker-body"><div class="cabinet ${locker.online ? '' : 'offline'} ${hardware.door === 'OPEN' ? 'open' : ''} ${locker.state === 'OCCUPIED' ? 'occupied' : ''}" aria-hidden="true"><div class="cabinet-door"></div><span class="cabinet-label">${locker.id}</span></div>
        <div class="locker-info"><div class="status-title">${locker.online ? 'Node đang kết nối' : 'Chờ kết nối thiết bị'}</div><div class="device-meta"><div><span>Cảm biến cửa</span><strong>${escapeHTML(hardware.door)}</strong></div><div><span>Phiên hiện tại</span><strong>${tx ? (tx.kind === 'DEPOSIT' ? 'Gửi hàng' : 'Nhận hàng') + ' · ' + escapeHTML(tx.status) : 'Chưa có phiên active'}</strong></div><div><span>Lệnh đang chờ</span><strong>${commands.filter(c => c.status === 'PENDING').map(c => c.action).join(', ') || '—'}</strong></div></div></div>
      </div><div class="locker-session">${tx ? `TX ${escapeHTML(short(tx.id))} · Đơn ${escapeHTML(short(tx.parcel_id))}` : 'Chưa có transaction'}</div>
      <div class="evidence">${evidence.map(([label, done]) => `<span class="${done ? 'done' : ''}">${done ? '✓ ' : ''}${label}</span>`).join('')}</div>
      <div class="locker-actions">${button('UNLOCK_APPLIED', 'UNLOCK', pending && unlock?.status === 'PENDING', 'secondary')}${button('DOOR_OPEN', 'Mở cửa', pending && unlock?.status === 'APPLIED')}${button('DOOR_CLOSED', 'Đóng cửa', pending && unlock?.status === 'APPLIED')}${button('LOCK_APPLIED', 'LOCK', pending && lock?.status === 'PENDING' && hardware.door === 'CLOSED', 'primary')}</div>
      <div class="locker-aux"><button class="text-button" type="button" data-locker="${locker.id}" data-tx="${escapeHTML(tx?.id || '')}" data-kind="SENSOR" ${pending && tx?.closed_sequence != null && hardware.door === 'CLOSED' ? '' : 'disabled'}>Snapshot CLOSED mới</button><span id="fresh-${locker.id}" class="freshness">Chưa có dữ liệu cửa</span><button class="text-button error-button" type="button" data-locker="${locker.id}" data-tx="${escapeHTML(tx?.id || '')}" data-kind="ERROR" ${pending ? '' : 'disabled'}>Mô phỏng lỗi</button></div>
    </article>`;
  }).join('');
}

function renderParcels() {
  const data = state.data;
  $('parcel-count').textContent = `${data.parcels.length} đơn`;
  $('parcel-rows').innerHTML = [...data.parcels].reverse().map(parcel => {
    const resident = data.residents.find(r => r.id === parcel.resident_id);
    const tx = data.transactions.find(t => t.parcel_id === parcel.id && t.kind === 'DEPOSIT');
    const locker = data.lockers.find(l => l.id === tx?.locker_id);
    return `<tr><td class="mono" title="${escapeHTML(parcel.id)}">#${escapeHTML(short(parcel.id))}</td><td>Phòng ${escapeHTML(resident?.room_code)}<br><small>${escapeHTML(resident?.phone)}</small></td><td>${escapeHTML(parcel.requested_size)} / ${escapeHTML(locker?.size || '—')}</td><td>${escapeHTML(tx?.locker_id || '—')}</td><td>${pill(parcel.status)}</td><td>${time(parcel.created_at)}</td></tr>`;
  }).join('') || '<tr><td colspan="6" class="empty"><span class="empty-symbol">▱</span>Chưa có đơn hàng.<br>Kết nối Node và tạo đơn gửi đầu tiên.</td></tr>';
  options('deposit-select', data.parcels.filter(p => ['CREATED', 'DEPOSITING'].includes(p.status)).map(p => ({id: p.id, label: `#${short(p.id)} · ${p.status}`})), 'Chọn phiên gửi hàng');
  options('pickup-select', state.ownParcels.filter(p => ['STORED', 'PICKUP_PENDING'].includes(p.status)).map(p => ({id: p.id, label: `#${short(p.id)} · ${p.status}`})), state.resident ? 'Chọn đơn để nhận' : 'Đăng nhập để xem đơn của bạn');
  options('history-filter', data.parcels.map(p => ({id: p.id, label: `Đơn #${short(p.id)}`})), 'Tất cả đơn hàng', false);
  $('pickup-select').disabled = !state.resident;
  updateForms();
}

function updateForms() {
  $('deposit-confirm').disabled = !$('deposit-select').value || !state.kiosk;
  const parcel = state.ownParcels.find(p => p.id === $('pickup-select').value);
  $('kiosk-code').disabled = !parcel || parcel.status !== 'STORED';
  $('pickup-request').disabled = !state.resident || !parcel || parcel.status !== 'STORED' || state.session?.parcel_id !== parcel.id;
  $('pickup-confirm').disabled = !state.resident || parcel?.status !== 'PICKUP_PENDING';
}

function renderHistory() {
  const filter = $('history-filter').value;
  const events = state.data.event_logs.filter(e => !filter || e.parcel_id === filter);
  $('event-count').textContent = String(events.length);
  $('event-list').innerHTML = events.slice(0, 120).map(e => `<div class="event-row"><span class="event-time">${time(e.created_at)}</span><span class="event-icon">${e.event.includes('ERROR') || e.event.includes('OFFLINE') ? '!' : '·'}</span><div class="event-text"><strong>${escapeHTML(e.event)}</strong>${e.new_state ? ` · ${escapeHTML(e.old_state || '∅')} → ${escapeHTML(e.new_state)}` : ''}<small>${e.locker_id || 'Locker Node'} ${e.parcel_id ? `· Đơn #${escapeHTML(short(e.parcel_id))}` : ''}</small></div><span class="event-extra">${e.transaction_id ? 'TX ' + escapeHTML(short(e.transaction_id)) : 'DEMO'}</span></div>`).join('') || '<div class="empty">Chưa có sự kiện trong lịch sử này.</div>';
  $('transaction-rows').innerHTML = [...state.data.transactions].reverse().filter(t => !filter || t.parcel_id === filter).map(t => `<tr><td class="mono" title="${escapeHTML(t.id)}">${escapeHTML(short(t.id))}</td><td>#${escapeHTML(short(t.parcel_id))} / ${escapeHTML(t.locker_id)}</td><td>${t.kind === 'DEPOSIT' ? 'Gửi' : 'Nhận'}</td><td>${pill(t.status)}</td><td>${t.confirmed ? 'Đã xác nhận' : 'Chưa xác nhận'}</td><td class="mono">${t.opened_sequence ?? '—'} / ${t.closed_sequence ?? '—'} / ${t.locked_sequence ?? '—'}</td></tr>`).join('') || '<tr><td colspan="6" class="empty">Chưa có giao dịch.</td></tr>';
}

function renderInspector() {
  if ($('database-details').open && state.data) $('database-json').textContent = JSON.stringify(state.data[$('database-table').value], null, 2);
}

function render() {
  const data = state.data;
  $('metric-available').innerHTML = `${data.lockers.filter(l => l.state === 'AVAILABLE' && l.online).length}<span>/ 2</span>`;
  $('metric-stored').textContent = data.parcels.filter(p => p.status === 'STORED').length;
  $('metric-pending').textContent = data.transactions.filter(t => t.status === 'PENDING').length;
  $('metric-completed').textContent = data.parcels.filter(p => p.status === 'COMPLETED').length;
  const online = data.lockers.every(l => l.online);
  $('node-status').textContent = online ? 'NODE ONLINE' : data.lockers.some(l => l.online) ? 'NODE PARTIAL' : 'NODE OFFLINE';
  $('node-status').className = 'pill ' + (online ? 'good' : 'neutral');
  $('node-toggle').textContent = online ? 'Ngắt kết nối' : 'Kết nối Node';
  renderLockers();
  renderParcels();
  renderHistory();
  renderInspector();
  tick();
}

async function refresh() {
  try {
    state.data = await request('/demo/state');
    state.serverOffset = state.data.server_time * 1000 - Date.now();
    if (state.resident) {
      try { state.ownParcels = await request('/api/v1/parcels', {token: state.resident}); }
      catch { state.resident = null; state.ownParcels = []; $('resident-auth').textContent = 'Cần đăng nhập lại'; }
    }
    render();
    $('sync-label').textContent = 'Đã đồng bộ ' + time(state.data.server_time);
    $('connection-error').hidden = true;
  } catch (error) {
    $('connection-error').textContent = 'Không thể đọc trạng thái mới: ' + error.message + '. Dữ liệu trên màn hình có thể đã cũ.';
    $('connection-error').hidden = false;
    $('sync-label').textContent = 'Mất đồng bộ';
    throw error;
  }
}

function tick() {
  const now = (Date.now() + state.serverOffset) / 1000;
  if (state.data) for (const locker of state.data.lockers) {
    const tx = state.data.transactions.find(t => t.locker_id === locker.id && t.active);
    const element = $('fresh-' + locker.id);
    const latest = tx || state.data.transactions.filter(t => t.locker_id === locker.id).at(-1);
    if (element) element.textContent = latest?.closed_at ? (latest.status === 'COMPLETED' ? 'Phiên đã hoàn tất' : `CLOSED ${Math.max(0, Math.floor(now - latest.closed_at))}s trước${now - latest.closed_at > 10 ? ' · đã cũ' : ''}`) : 'Chưa có CLOSED trong phiên';
  }
  if (state.session) {
    const remaining = Math.max(0, Math.ceil(state.session.expires_at - now));
    $('kiosk-countdown').textContent = remaining ? `Mã còn hiệu lực ${remaining}s` : 'Mã đã hết hạn · lấy mã mới';
    $('kiosk-countdown').className = remaining ? '' : 'expired';
  } else {
    $('kiosk-countdown').textContent = 'Mã một lần · TTL 30 giây';
    $('kiosk-countdown').className = '';
  }
}

$('node-toggle').addEventListener('click', () => action(async () => {
  const online = !state.data.lockers.every(l => l.online);
  await request('/demo/node', {method: 'POST', body: {online}});
  return online ? 'Đã kết nối Node. Các reservation và trạng thái lỗi vẫn được giữ nguyên.' : 'Đã ngắt Node. Phiên đang chạy chuyển EXCEPTION và vẫn giữ ngăn.';
}));

$('lockers').addEventListener('click', event => {
  const button = event.target.closest('button[data-kind]');
  if (!button || button.disabled) return;
  action(async () => {
    await request(`/demo/lockers/${button.dataset.locker}/events`, {method: 'POST', body: {
      event_id: crypto.randomUUID(), transaction_id: button.dataset.tx, kind: button.dataset.kind,
      door: button.dataset.kind === 'SENSOR' ? 'CLOSED' : 'UNKNOWN',
    }});
    return `${button.dataset.locker} · Đã ghi ${button.dataset.kind}.`;
  });
});

$('deposit-form').addEventListener('submit', event => {
  event.preventDefault();
  action(async () => {
    const result = await request('/api/v1/deposits', {method: 'POST', token: state.kiosk, body: Object.fromEntries(new FormData(event.target))});
    return `Đã đặt ${result.locker_id} · kiện ${result.requested_size}, ngăn ${result.allocated_size}. Tiếp theo, bấm UNLOCK ở trạm mô phỏng.`;
  });
});
$('deposit-confirm').addEventListener('click', () => action(async () => {
  const result = await request(`/api/v1/deposits/${$('deposit-select').value}/confirm`, {method: 'POST', token: state.kiosk});
  return `Đã ghi xác nhận gửi · ${result.status}. Nếu CLOSED đã cũ, bấm Snapshot CLOSED mới rồi LOCK.`;
}));

$('resident-username').addEventListener('change', () => {
  const account = state.accounts.find(a => a.username === $('resident-username').value && a.role === 'RESIDENT');
  $('resident-password').value = account?.password || '';
});
$('login-form').addEventListener('submit', event => {
  event.preventDefault();
  action(async () => {
    const fields = Object.fromEntries(new FormData(event.target));
    // Drop the previous identity even when the replacement login fails.
    if (state.resident) await request('/api/v1/auth/logout', {method: 'POST', token: state.resident});
    state.resident = null;
    state.residentInfo = null;
    state.ownParcels = [];
    state.session = null;
    $('pickup-code').value = '';
    $('resident-auth').textContent = 'Chưa đăng nhập';
    const token = await authenticate(fields);
    const residents = await request('/api/v1/residents', {token});
    if (residents.length !== 1) throw new Error('Hãy dùng tài khoản có vai trò RESIDENT.');
    state.resident = token;
    state.residentInfo = residents[0];
    $('resident-auth').textContent = 'Phòng ' + residents[0].room_code;
    $('resident-auth').className = 'pill good';
    return `Đã đăng nhập ${fields.username}. Chỉ hiển thị đơn thuộc cư dân này.`;
  });
});
$('kiosk-code').addEventListener('click', () => action(async () => {
  const parcel_id = $('pickup-select').value;
  state.session = {...await request('/api/v1/kiosk-sessions', {method: 'POST', token: state.kiosk, body: {parcel_id}}), parcel_id};
  $('pickup-code').value = state.session.code;
  return 'Đã tạo mã kiosk một lần. Bấm Xác thực nhận hàng trong 30 giây.';
}));
$('pickup-form').addEventListener('submit', event => {
  event.preventDefault();
  action(async () => {
    if (!state.session) throw new Error('Hãy lấy mã kiosk trước.');
    const parcel = $('pickup-select').value;
    await request(`/api/v1/pickups/${parcel}`, {method: 'POST', token: state.resident, body: {session_id: state.session.session_id, code: $('pickup-code').value}});
    state.session = null;
    $('pickup-code').value = '';
    return 'Đã chấp nhận yêu cầu nhận hàng. Bấm UNLOCK, OPEN và CLOSED ở trạm mô phỏng.';
  });
});
$('pickup-confirm').addEventListener('click', () => action(async () => {
  const result = await request(`/api/v1/pickups/${$('pickup-select').value}/confirm`, {method: 'POST', token: state.resident});
  return `Đã ghi xác nhận lấy hàng · ${result.status}. Bấm LOCK khi dữ liệu cửa còn mới.`;
}));

for (const id of ['deposit-select', 'pickup-select']) $(id).addEventListener('change', () => {
  if (id === 'pickup-select') { state.session = null; $('pickup-code').value = ''; }
  updateForms();
});
$('history-filter').addEventListener('change', renderHistory);
$('database-table').addEventListener('change', renderInspector);
$('database-details').addEventListener('toggle', renderInspector);
for (const tab of ['events', 'transactions']) $(tab + '-tab').addEventListener('click', () => {
  for (const name of ['events', 'transactions']) {
    $(name + '-tab').setAttribute('aria-selected', String(name === tab));
    $(name + '-panel').hidden = name !== tab;
  }
});
$('reset-open').addEventListener('click', () => $('reset-dialog').showModal());
$('reset-cancel').addEventListener('click', () => $('reset-dialog').close());
$('reset-confirm').addEventListener('click', () => {
  $('reset-dialog').close();
  action(async () => {
    await request('/demo/reset', {method: 'POST'});
    state.lockerSignature = '';
    await bootstrap();
    return 'Đã reset database demo. Kết nối Node để bắt đầu phiên mới.';
  });
});
for (const link of document.querySelectorAll('.nav-link')) link.addEventListener('click', () => {
  document.querySelectorAll('.nav-link').forEach(item => item.classList.remove('active'));
  link.classList.add('active');
});

async function poll() {
  if (!state.busy && !document.hidden) {
    try { await refresh(); } catch { /* Keep the visible error banner. */ }
  }
  setTimeout(poll, 1500);
}

(async () => {
  try { await bootstrap(); await refresh(); }
  catch (error) {
    $('connection-error').textContent = 'Không thể khởi tạo demo: ' + error.message + '. Hãy tải lại trang.';
    $('connection-error').hidden = false;
  }
  setInterval(tick, 1000); // Read-only countdown; never produces device evidence.
  poll();
})();
