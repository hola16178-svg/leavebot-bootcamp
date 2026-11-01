const byId = (id) => document.getElementById(id);
const employee = byId('employee'), form = byId('leave-form'), fields = byId('leave-fields');
const submitButton = byId('submit-leave'), submitMessage = byId('submit-message');
const listMessage = byId('list-message'), list = byId('leave-list'), refresh = byId('refresh-leaves');
const unknownMessage = '無法確認是否送出成功，請先查看我的假單，再決定是否重送';
let submitting = false, listSequence = 0;
const types = { annual: '特休', personal: '事假', sick: '病假' };
const periods = { full: '整天', am: '上午', pm: '下午' };
async function checkHealth() {
  byId('retry').disabled = true;
  byId('health-status').textContent = '檢查連線中…';
  try {
    const response = await fetch('/api/health', {cache: 'no-store'});
    const data = await response.json();
    if (!response.ok || data.status !== 'ok') throw new Error('health');
    byId('health-status').textContent = '服務連線正常';
  } catch {
    byId('health-status').textContent = '無法連線到服務，請確認服務已啟動後重新檢查。';
  } finally { byId('retry').disabled = false; }
}
function setLocked(locked) {
  employee.disabled = locked;
  fields.disabled = locked || !employee.value;
  refresh.disabled = locked || !employee.value;
  submitButton.textContent = locked ? '送出中…' : '送出請假申請';
}
function addText(parent, tag, text, className) {
  const element = document.createElement(tag);
  element.textContent = text;
  if (className) element.className = className;
  parent.append(element);
  return element;
}
function renderLeaves(leaves) {
  list.replaceChildren();
  for (const leave of leaves) {
    const item = document.createElement('li');
    const title = addText(item, 'div', '', 'leave-title');
    addText(title, 'strong', `${types[leave.leave_type]} · ${leave.days} 天`);
    addText(title, 'span', '待審核', 'badge');
    addText(item, 'p', `${leave.start_date} → ${leave.end_date} · ${periods[leave.period]}`);
    addText(item, 'p', leave.reason || '未填理由', 'reason');
    addText(item, 'small', `申請 #${leave.id}`);
    list.append(item);
  }
}
async function loadLeaves() {
  const selected = employee.value, sequence = ++listSequence;
  list.replaceChildren();
  if (!selected) { listMessage.textContent = '選擇員工後查看申請。'; return; }
  listMessage.textContent = '正在讀取假單…';
  try {
    const response = await fetch(`/api/leaves?employee_id=${encodeURIComponent(selected)}`, {cache: 'no-store'});
    const data = await response.json();
    if (!response.ok || !Array.isArray(data.leaves)) throw new Error('list');
    if (sequence !== listSequence || selected !== employee.value) return;
    renderLeaves(data.leaves);
    listMessage.textContent = data.leaves.length ? `共 ${data.leaves.length} 筆申請` : '目前沒有申請';
  } catch {
    if (sequence !== listSequence || selected !== employee.value) return;
    listMessage.textContent = '無法讀取假單，請稍後再試。';
  }
}
async function loadEmployees() {
  try {
    const response = await fetch('/api/employees', {cache: 'no-store'});
    const data = await response.json();
    if (!response.ok || !Array.isArray(data.employees)) throw new Error('employees');
    employee.replaceChildren(new Option('請選擇員工', ''));
    for (const person of data.employees) employee.append(new Option(person.name, String(person.id)));
    employee.disabled = !data.employees.length;
    if (!data.employees.length) byId('employee-message').textContent = '目前沒有可選員工。';
  } catch {
    employee.replaceChildren(new Option('無法載入員工', ''));
    employee.disabled = true;
    byId('employee-message').textContent = '員工名單載入失敗，請重新整理後再試。';
  }
}
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (submitting || !employee.value || !form.reportValidity()) return;
  const input = Object.fromEntries(new FormData(form));
  input.employee_id = Number(employee.value);
  submitting = true;
  setLocked(true);
  submitMessage.dataset.state = 'loading';
  submitMessage.textContent = '送出中…';
  let saved = false;
  try {
    const response = await fetch('/api/leaves', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(input)});
    const data = await response.json();
    if (response.status === 201 && data.leave?.status === 'pending') {
      submitMessage.dataset.state = 'success';
      submitMessage.textContent = '送出成功，申請已登記為待審核。';
      saved = true;
    } else if (data.error && typeof data.error.message === 'string') {
      submitMessage.dataset.state = 'error';
      submitMessage.textContent = data.error.code === 'SUBMISSION_UNKNOWN' ? unknownMessage : data.error.message;
    } else { throw new Error('unknown result'); }
  } catch {
    submitMessage.dataset.state = 'error';
    submitMessage.textContent = unknownMessage;
  } finally { submitting = false; setLocked(false); }
  if (saved) await loadLeaves();
});
employee.addEventListener('change', () => {
  setLocked(submitting);
  submitMessage.textContent = employee.value ? '填妥後即可送出申請。' : '請先選擇員工。';
  submitMessage.dataset.state = '';
  loadLeaves();
});
byId('reason').addEventListener('input', () => {
  const trimmed = byId('reason').value.replace(/^[\u0009-\u000D\u0020\u0085\u00A0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000]+|[\u0009-\u000D\u0020\u0085\u00A0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000]+$/gu, '');
  byId('reason-count').textContent = `${Array.from(trimmed).length} / 200 字；去除前後空白後計算`;
});
refresh.addEventListener('click', loadLeaves);
byId('retry').addEventListener('click', checkHealth);
checkHealth();
loadEmployees();
