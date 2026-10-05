/* SmartFrame Hospital: browser port of the Python/Tkinter app.
   Same ideas: frames with inheritance, a symptom knowledge base, department suggestion.
   Records are kept in this browser only (localStorage). */

// ---------- Frame engine (port of frame_engine.py) ----------
class Frame {
  constructor(name, parent = null) {
    this.name = name;
    this.parent = parent;
    this.slots = {};
  }
  setSlot(slot, value) { this.slots[slot] = value; }
  getSlot(slot) {
    if (slot in this.slots) return this.slots[slot];
    if (this.parent) return this.parent.getSlot(slot);
    return null;
  }
  allSlots() {
    const result = this.parent ? this.parent.allSlots() : {};
    return Object.assign(result, this.slots);
  }
}

// ---------- Frame hierarchy: PERSON -> PATIENT ----------
const person = new Frame('PERSON');
person.setSlot('Phone', 'Not Provided');
person.setSlot('Address', 'Not Provided');

const patientTemplate = new Frame('PATIENT', person);
Object.entries({
  'Patient ID': 'Not Assigned', 'Name': 'Not Provided', 'Age': 'Not Provided',
  'Gender': 'Not Provided', 'Blood Group': 'Unknown', 'Allergies': 'Not Provided',
  'Symptoms': 'None', 'Department': 'General Medicine', 'Doctor': 'Not Assigned',
  'Room': 'Not Assigned', 'Bed Number': 'Not Assigned'
}).forEach(([k, v]) => patientTemplate.setSlot(k, v));

// ---------- Knowledge base ----------
const knowledge = {
  'General Medicine': ['fever', 'cough', 'sore throat'],
  'Neurology': ['headache', 'dizziness', 'migraine'],
  'Orthopedics': ['joint pain', 'bone pain', 'swelling'],
  'Gastroenterology': ['stomach pain', 'vomiting', 'diarrhea']
};

// Same rule as suggest_department(): most matching symptoms wins, ties keep the first department.
function suggestDepartment(symptomsText) {
  const given = new Set(symptomsText.split(',').map(s => s.trim().toLowerCase()).filter(Boolean));
  let best = 'General Medicine', highest = 0, matched = [];
  for (const [dept, known] of Object.entries(knowledge)) {
    const hits = known.filter(s => given.has(s));
    if (hits.length > highest) { highest = hits.length; best = dept; matched = hits; }
  }
  return { department: best, matched };
}

// ---------- Storage (browser only, fictional sample data) ----------
const KEY = 'smartframe-hospital-patients-v1';
const SAMPLE = [
  ['P001', 'Asha Verma', 34, 'Female', '0000000001', 'Sample Street, Demo City', 'B+', 'None', 'headache, dizziness', 'Neurology', 'Dr. Rao', '101', 'A1'],
  ['P002', 'Ravi Kulkarni', 52, 'Male', '0000000002', 'Demo Nagar, Sample City', 'O+', 'Penicillin', 'joint pain, swelling', 'Orthopedics', 'Dr. Mehta', '204', 'B3'],
  ['P003', 'Meera Joshi', 27, 'Female', '0000000003', 'Test Colony, Demo City', 'A+', 'Not Provided', 'vomiting, stomach pain', 'Gastroenterology', 'Dr. Iyer', '110', 'C2']
];
const FIELDS = ['patient_id', 'name', 'age', 'gender', 'phone', 'address', 'blood_group', 'allergies', 'symptoms', 'department', 'doctor', 'room', 'bed_number'];
const LABELS = ['Patient ID', 'Name', 'Age', 'Gender', 'Phone Number', 'Address', 'Blood Group', 'Allergies', 'Symptoms', 'Department', 'Doctor', 'Room', 'Bed Number'];

let memoryStore = null; // fallback if storage is blocked
function loadAll() {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) return JSON.parse(raw);
  } catch (e) { if (memoryStore) return memoryStore; }
  if (memoryStore) return memoryStore;
  const seeded = SAMPLE.map(r => r.slice());
  saveAll(seeded);
  return seeded;
}
function saveAll(rows) {
  memoryStore = rows;
  try { localStorage.setItem(KEY, JSON.stringify(rows)); } catch (e) { /* storage unavailable */ }
}
function saveRecord(row) { // INSERT OR REPLACE
  const rows = loadAll().filter(r => r[0].toLowerCase() !== row[0].toLowerCase());
  rows.push(row);
  rows.sort((a, b) => a[0].localeCompare(b[0]));
  saveAll(rows);
}
function findRecord(id) { return loadAll().find(r => r[0].toLowerCase() === id.toLowerCase()) || null; }

// ---------- UI helpers ----------
const $ = (id) => document.getElementById(id);
function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined) n.textContent = text;
  return n;
}
function showMsg(node, text, ok) {
  node.textContent = text;
  node.className = 'demo-msg ' + (ok ? 'ok' : 'err');
}
function recordCard(row) {
  const dl = el('dl', 'record');
  row.forEach((v, i) => {
    dl.appendChild(el('dt', null, LABELS[i]));
    dl.appendChild(el('dd', null, String(v)));
  });
  return dl;
}

// ---------- Tabs ----------
const tabs = document.querySelectorAll('.demo-tab');
tabs.forEach(tab => tab.addEventListener('click', () => {
  tabs.forEach(t => { t.classList.remove('active'); t.setAttribute('aria-selected', 'false'); });
  document.querySelectorAll('.demo-panel').forEach(p => p.hidden = true);
  tab.classList.add('active'); tab.setAttribute('aria-selected', 'true');
  $(tab.dataset.panel).hidden = false;
  if (tab.dataset.panel === 'panel-all') renderAll();
  if (tab.dataset.panel === 'panel-frames') renderFrames();
}));

// ---------- Patient Management ----------
$('patientForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  const get = (k, dflt) => (f.get(k) || '').toString().trim() || dflt;
  const msg = $('saveMsg');

  const id = get('id', '');
  const name = get('name', '');
  const ageText = get('age', '');
  if (!id) return showMsg(msg, 'Enter Patient ID.', false);
  if (!name) return showMsg(msg, 'Enter Patient Name.', false);
  if (!ageText) return showMsg(msg, 'Enter Age.', false);
  if (!/^\d+$/.test(ageText)) return showMsg(msg, 'Age must be a number.', false);
  const age = parseInt(ageText, 10);

  const gender = get('gender', 'Not Provided');
  const phone = get('phone', 'Not Provided');
  const address = get('address', 'Not Provided');
  const blood = get('blood', 'Unknown');
  const allergies = get('allergies', 'Not Provided');
  const symptoms = get('symptoms', 'None');
  const doctor = get('doctor', 'Not Assigned');
  const room = get('room', 'Not Assigned');
  const bed = get('bed', 'Not Assigned');

  const result = symptoms.toLowerCase() === 'none'
    ? { department: 'General Medicine', matched: [] }
    : suggestDepartment(symptoms);

  // Build the patient instance frame (inherits from PATIENT, which inherits from PERSON)
  const frame = new Frame('PATIENT_' + id, patientTemplate);
  Object.entries({
    'Patient ID': id, 'Name': name, 'Age': age, 'Gender': gender, 'Phone': phone, 'Address': address,
    'Blood Group': blood, 'Allergies': allergies, 'Symptoms': symptoms, 'Department': result.department,
    'Doctor': doctor, 'Room': room, 'Bed Number': bed
  }).forEach(([k, v]) => frame.setSlot(k, v));

  saveRecord([id, name, age, gender, phone, address, blood, allergies, symptoms, result.department, doctor, room, bed]);

  const why = result.matched.length
    ? ' (matched: ' + result.matched.join(', ') + ')'
    : ' (no symptom matched, default department)';
  showMsg(msg, 'Patient details saved. Suggested department: ' + result.department + why + '.', true);
  e.target.reset();
});

// ---------- Search ----------
function doSearch() {
  const out = $('searchOut');
  out.textContent = '';
  const id = $('searchId').value.trim();
  if (!id) { out.appendChild(el('p', 'demo-msg err', 'Enter Patient ID.')); return; }
  const row = findRecord(id);
  if (!row) { out.appendChild(el('p', 'demo-msg err', 'PATIENT NOT FOUND')); return; }
  out.appendChild(el('h3', null, 'Patient information'));
  out.appendChild(recordCard(row));
}
$('searchBtn').addEventListener('click', doSearch);
$('searchId').addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); doSearch(); } });

// ---------- Frame Explorer ----------
function slotTable(frame) {
  const t = el('dl', 'record');
  Object.entries(frame.allSlots()).forEach(([k, v]) => {
    t.appendChild(el('dt', null, k));
    const dd = el('dd', null, String(v));
    if (!(k in frame.slots)) dd.appendChild(el('span', 'tag', 'inherited'));
    t.appendChild(dd);
  });
  return t;
}
function renderFrames() {
  const out = $('framesOut');
  out.textContent = '';
  out.appendChild(el('h3', null, 'Frame 1: PERSON'));
  out.appendChild(slotTable(person));
  out.appendChild(el('h3', null, 'Frame 2: PATIENT (parent: PERSON)'));
  out.appendChild(slotTable(patientTemplate));
  out.appendChild(el('h3', null, 'Frame hierarchy'));
  out.appendChild(el('pre', 'tree', 'PERSON\n  |\n  +---- PATIENT\n           |\n           +---- Patient Instance'));
  out.appendChild(el('h3', null, 'Medical knowledge frames'));
  const kb = el('dl', 'record');
  Object.entries(knowledge).forEach(([d, s]) => {
    kb.appendChild(el('dt', null, d));
    kb.appendChild(el('dd', null, s.slice().sort().join(', ')));
  });
  out.appendChild(kb);
}

// ---------- All patients ----------
function renderAll() {
  const out = $('allOut');
  out.textContent = '';
  const rows = loadAll();
  if (!rows.length) { out.appendChild(el('p', null, 'No patient records found.')); return; }
  out.appendChild(el('h3', null, 'All patient records (' + rows.length + ')'));
  const wrap = el('div', 'table-wrap');
  const table = el('table', 'records');
  const thead = el('thead'); const hr = el('tr');
  LABELS.forEach(l => hr.appendChild(el('th', null, l)));
  thead.appendChild(hr); table.appendChild(thead);
  const tbody = el('tbody');
  rows.forEach(r => {
    const tr = el('tr');
    r.forEach(v => tr.appendChild(el('td', null, String(v))));
    tbody.appendChild(tr);
  });
  table.appendChild(tbody); wrap.appendChild(table); out.appendChild(wrap);
}
$('resetBtn').addEventListener('click', () => {
  saveAll(SAMPLE.map(r => r.slice()));
  renderAll();
});

loadAll();
renderFrames();
