import { useState } from "react";

const C = {
  bg: "#080c08", surface: "#0f130f", surface2: "#151a15",
  border: "#1c231c", borderLight: "#252e25",
  accent: "#00e676", accentBg: "#00e67608",
  text: "#eef2ee", textSub: "#7a957a", textMuted: "#3d4e3d",
  danger: "#ff5252", dangerBg: "#ff525208",
  warn: "#ffab40", warnBg: "#ffab4008",
  blue: "#40c4ff", blueBg: "#40c4ff08",
  purple: "#ce93d8", purpleBg: "#ce93d808",
};

const initEmployees = [
  { emp_id: 1,  emp_code: "EMP001", full_name: "จ๊อด",         position: "หัวหน้างาน", daily_wage: 1000, phone: "081-234-5678", national_id: "1-1001-00001-00-1", start_date: "2020-01-01", status: "active", role: "admin",    emergency_name: "แม่จ๊อด",     emergency_phone: "081-999-0001", address: "123 ถ.เพชรบุรี กรุงเทพฯ",  bank: "กสิกรไทย",   bank_account: "123-4-56789-0", note: "", ot: 500,  advance: 0,    work_days: 20, leave_days: 2, absent_days: 0 },
  { emp_id: 4,  emp_code: "EMP004", full_name: "เขียว",         position: "พนักงาน",    daily_wage: 500,  phone: "082-111-2222", national_id: "1-1001-00004-00-4", start_date: "2022-03-15", status: "active", role: "employee", emergency_name: "พ่อเขียว",    emergency_phone: "082-999-0002", address: "456 ถ.ลาดพร้าว กรุงเทพฯ", bank: "ไทยพาณิชย์", bank_account: "456-7-89012-3", note: "", ot: 200,  advance: 500,  work_days: 18, leave_days: 2, absent_days: 0 },
  { emp_id: 5,  emp_code: "EMP005", full_name: "ทอง",           position: "พนักงาน",    daily_wage: 550,  phone: "083-222-3333", national_id: "1-1001-00005-00-5", start_date: "2022-06-01", status: "active", role: "employee", emergency_name: "แม่ทอง",      emergency_phone: "083-999-0003", address: "789 ถ.รัชดา กรุงเทพฯ",    bank: "กรุงไทย",    bank_account: "789-0-12345-6", note: "", ot: 0,    advance: 0,    work_days: 17, leave_days: 3, absent_days: 0 },
  { emp_id: 8,  emp_code: "EMP008", full_name: "จอ",            position: "พนักงาน",    daily_wage: 420,  phone: "084-333-4444", national_id: "1-1001-00008-00-8", start_date: "2023-01-10", status: "active", role: "employee", emergency_name: "พ่อจอ",       emergency_phone: "084-999-0004", address: "101 ถ.สุขุมวิท กรุงเทพฯ", bank: "กรุงเทพ",    bank_account: "012-3-45678-9", note: "", ot: 100,  advance: 200,  work_days: 19, leave_days: 1, absent_days: 0 },
  { emp_id: 9,  emp_code: "EMP009", full_name: "เจมีน",         position: "พนักงาน",    daily_wage: 400,  phone: "085-444-5555", national_id: "1-1001-00009-00-9", start_date: "2023-02-01", status: "active", role: "employee", emergency_name: "แม่เจมีน",    emergency_phone: "085-999-0005", address: "202 ถ.พระราม 4 กรุงเทพฯ", bank: "กสิกรไทย",   bank_account: "234-5-67890-1", note: "", ot: 0,    advance: 0,    work_days: 20, leave_days: 0, absent_days: 0 },
  { emp_id: 10, emp_code: "EMP010", full_name: "มีน",           position: "พนักงาน",    daily_wage: 400,  phone: "086-555-6666", national_id: "1-1001-00010-00-0", start_date: "2023-03-01", status: "active", role: "employee", emergency_name: "พ่อมีน",      emergency_phone: "086-999-0006", address: "303 ถ.งามวงศ์วาน นนทบุรี", bank: "ไทยพาณิชย์", bank_account: "345-6-78901-2", note: "", ot: 300,  advance: 0,    work_days: 20, leave_days: 0, absent_days: 0 },
  { emp_id: 11, emp_code: "EMP011", full_name: "ดู",            position: "พนักงาน",    daily_wage: 400,  phone: "087-666-7777", national_id: "1-1001-00011-00-1", start_date: "2023-04-01", status: "active", role: "employee", emergency_name: "แม่ดู",       emergency_phone: "087-999-0007", address: "404 ถ.แจ้งวัฒนะ นนทบุรี", bank: "กรุงไทย",    bank_account: "456-7-89012-3", note: "", ot: 0,    advance: 500,  work_days: 16, leave_days: 2, absent_days: 2 },
  { emp_id: 12, emp_code: "EMP012", full_name: "ลาย",           position: "พนักงาน",    daily_wage: 400,  phone: "088-777-8888", national_id: "1-1001-00012-00-2", start_date: "2023-05-01", status: "active", role: "employee", emergency_name: "พ่อลาย",      emergency_phone: "088-999-0008", address: "505 ถ.บางนา สมุทรปราการ",  bank: "กรุงเทพ",    bank_account: "567-8-90123-4", note: "", ot: 0,    advance: 0,    work_days: 20, leave_days: 0, absent_days: 0 },
  { emp_id: 17, emp_code: "EMP017", full_name: "พี่นายแมคโคร", position: "พนักงาน",    daily_wage: 600,  phone: "093-222-3333", national_id: "1-1001-00017-00-7", start_date: "2021-05-01", status: "active", role: "employee", emergency_name: "ภรรยาแมคโคร", emergency_phone: "093-999-0013", address: "110 ถ.รามคำแหง กรุงเทพฯ", bank: "กสิกรไทย",   bank_account: "012-3-45678-9", note: "", ot: 600,  advance: 1000, work_days: 20, leave_days: 0, absent_days: 0 },
  { emp_id: 18, emp_code: "EMP018", full_name: "ปัง",           position: "พนักงาน",    daily_wage: 400,  phone: "094-333-4444", national_id: "1-1001-00018-00-8", start_date: "2024-01-01", status: "active", role: "employee", emergency_name: "แม่ปัง",      emergency_phone: "094-999-0014", address: "111 ถ.ลาดกระบัง กรุงเทพฯ", bank: "ไทยพาณิชย์", bank_account: "123-4-56789-0", note: "", ot: 0,    advance: 0,    work_days: 20, leave_days: 0, absent_days: 0 },
];

const ATTENDANCE = [
  { emp_id: 1,  full_name: "จ๊อด",         status: "normal", check_in: "08:02", check_out: null },
  { emp_id: 4,  full_name: "เขียว",         status: "normal", check_in: "08:00", check_out: "17:00" },
  { emp_id: 5,  full_name: "ทอง",           status: "absent", check_in: null,    check_out: null },
  { emp_id: 8,  full_name: "จอ",            status: "normal", check_in: "08:05", check_out: null },
  { emp_id: 9,  full_name: "เจมีน",         status: "normal", check_in: "08:00", check_out: null },
  { emp_id: 10, full_name: "มีน",           status: "normal", check_in: "08:00", check_out: null },
  { emp_id: 11, full_name: "ดู",            status: "absent", check_in: null,    check_out: null },
  { emp_id: 12, full_name: "ลาย",           status: "normal", check_in: "08:01", check_out: null },
  { emp_id: 17, full_name: "พี่นายแมคโคร", status: "normal", check_in: "07:55", check_out: null },
  { emp_id: 18, full_name: "ปัง",           status: "normal", check_in: "08:00", check_out: null },
];

const initLogs = [
  { id: 1, ts: "2026-05-13 08:02", user: "จ๊อด", action: "เพิ่ม",   target: "พนักงาน", detail: "เพิ่มพนักงาน ปัง (EMP018)" },
  { id: 2, ts: "2026-05-12 14:30", user: "จ๊อด", action: "แก้ไข",  target: "รายได้",   detail: "แก้ไข OT ของ พี่นายแมคโคร: 0 → 600 บาท" },
  { id: 3, ts: "2026-05-12 09:15", user: "จ๊อด", action: "อนุมัติ", target: "ใบลา",     detail: "อนุมัติใบลาป่วยของ เขียว 1 วัน" },
  { id: 4, ts: "2026-05-11 17:00", user: "จ๊อด", action: "แก้ไข",  target: "พนักงาน", detail: "แก้ไขค่าแรง ทอง: 500 → 550 บาท/วัน" },
  { id: 5, ts: "2026-05-10 10:20", user: "จ๊อด", action: "เพิ่ม",   target: "รายได้",   detail: "บันทึกเบิกล่วงหน้า เขียว 500 บาท" },
  { id: 6, ts: "2026-05-09 16:45", user: "จ๊อด", action: "ลบ",      target: "รายได้",   detail: "ลบรายการ OT ของ ดู (บันทึกผิด)" },
  { id: 7, ts: "2026-05-08 08:00", user: "ระบบ", action: "อัตโนมัติ",target: "การเข้างาน","detail": "Auto check-in พนักงาน 10 คน" },
];

const avatarColors = ["#00e676","#40c4ff","#ffab40","#ff5252","#ce93d8","#80cbc4","#fff176","#ffcc02"];
const getColor = (name) => avatarColors[name.charCodeAt(0) % avatarColors.length];
const nowStr = () => new Date().toLocaleString("th-TH", { year:"numeric", month:"2-digit", day:"2-digit", hour:"2-digit", minute:"2-digit" }).replace(/\//g,"-");

function Avatar({ name, size = 40, photo }) {
  const color = getColor(name);
  if (photo) return (
    <div style={{ width: size, height: size, borderRadius: "50%", flexShrink: 0, overflow: "hidden", border: `2px solid ${color}50` }}>
      <img src={photo} alt={name} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    </div>
  );
  return (
    <div style={{ width: size, height: size, borderRadius: "50%", flexShrink: 0, background: color + "18", border: `2px solid ${color}40`, display: "flex", alignItems: "center", justifyContent: "center", color, fontWeight: 800, fontSize: size * 0.38, userSelect: "none" }}>
      {name.charAt(0)}
    </div>
  );
}

// อ่านไฟล์รูปเป็น base64
function readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = e => resolve(e.target.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// Upload zone component
function PhotoUpload({ label, value, onChange, round = false }) {
  const [drag, setDrag] = useState(false);
  const handleFile = async (file) => {
    if (!file || !file.type.startsWith("image/")) return;
    const b64 = await readFileAsBase64(file);
    onChange(b64);
  };
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ color: C.textSub, fontSize: 11, letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 8 }}>{label}</div>
      {value ? (
        <div style={{ position: "relative", display: "inline-block" }}>
          <img src={value} alt={label} style={{ width: round ? 80 : 160, height: round ? 80 : 100, objectFit: "cover", borderRadius: round ? "50%" : 8, border: `2px solid ${C.accent}40`, display: "block" }} />
          <button onClick={() => onChange(null)} style={{ position: "absolute", top: -6, right: -6, width: 20, height: 20, borderRadius: "50%", background: C.danger, border: "none", color: "#fff", cursor: "pointer", fontSize: 12, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800 }}>✕</button>
          <label style={{ position: "absolute", bottom: -6, right: -6, width: 22, height: 22, borderRadius: "50%", background: C.accent, border: "none", color: "#000", cursor: "pointer", fontSize: 11, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800 }}>
            ✏<input type="file" accept="image/*" style={{ display: "none" }} onChange={e => handleFile(e.target.files[0])} />
          </label>
        </div>
      ) : (
        <label style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", width: round ? 80 : "100%", height: round ? 80 : 100, borderRadius: round ? "50%" : 8, border: `2px dashed ${drag ? C.accent : C.border}`, background: drag ? C.accentBg : C.bg, cursor: "pointer", transition: "all 0.15s", gap: 6 }}
          onDragOver={e => { e.preventDefault(); setDrag(true); }}
          onDragLeave={() => setDrag(false)}
          onDrop={e => { e.preventDefault(); setDrag(false); handleFile(e.dataTransfer.files[0]); }}
        >
          <span style={{ fontSize: round ? 20 : 24, opacity: 0.4 }}>📷</span>
          {!round && <span style={{ color: C.textMuted, fontSize: 11 }}>คลิกหรือลากรูปมาวาง</span>}
          <input type="file" accept="image/*" style={{ display: "none" }} onChange={e => handleFile(e.target.files[0])} />
        </label>
      )}
    </div>
  );
}

function Tag({ type }) {
  const map = {
    normal: { label: "มาทำงาน", color: C.accent, bg: C.accentBg },
    absent: { label: "ขาด", color: C.danger, bg: C.dangerBg },
    sick: { label: "ลาป่วย", color: C.warn, bg: C.warnBg },
    personal: { label: "ลากิจ", color: C.blue, bg: C.blueBg },
    vacation: { label: "ลาพักร้อน", color: C.purple, bg: C.purpleBg },
    pending: { label: "รออนุมัติ", color: C.warn, bg: C.warnBg },
    approved: { label: "อนุมัติแล้ว", color: C.accent, bg: C.accentBg },
    rejected: { label: "ไม่อนุมัติ", color: C.danger, bg: C.dangerBg },
    active: { label: "ทำงานอยู่", color: C.accent, bg: C.accentBg },
    inactive: { label: "ลาออกแล้ว", color: C.textMuted, bg: C.surface2 },
    admin: { label: "Admin", color: C.purple, bg: C.purpleBg },
    employee: { label: "พนักงาน", color: C.blue, bg: C.blueBg },
    เพิ่ม: { label: "เพิ่ม", color: C.accent, bg: C.accentBg },
    แก้ไข: { label: "แก้ไข", color: C.blue, bg: C.blueBg },
    ลบ: { label: "ลบ", color: C.danger, bg: C.dangerBg },
    อนุมัติ: { label: "อนุมัติ", color: C.warn, bg: C.warnBg },
    อัตโนมัติ: { label: "Auto", color: C.textSub, bg: C.surface2 },
  };
  const s = map[type] || { label: type, color: C.textSub, bg: C.surface };
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 4, background: s.bg, color: s.color, border: `1px solid ${s.color}25`, borderRadius: 6, padding: "3px 9px", fontSize: 11, fontWeight: 700, whiteSpace: "nowrap" }}>
      <span style={{ width: 4, height: 4, borderRadius: "50%", background: s.color }} />{s.label}
    </span>
  );
}

function Btn({ children, variant = "primary", size = "md", style: s, ...props }) {
  const pad = { sm: "6px 12px", md: "9px 18px", lg: "12px 28px" };
  const v = {
    primary: { background: C.accent, color: "#000", border: "none" },
    outline: { background: "transparent", color: C.accent, border: `1px solid ${C.accent}50` },
    ghost: { background: "transparent", color: C.textSub, border: `1px solid ${C.border}` },
    danger: { background: C.danger, color: "#fff", border: "none" },
    warn: { background: C.warn, color: "#000", border: "none" },
  };
  return (
    <button {...props} style={{ ...v[variant], padding: pad[size], borderRadius: 8, cursor: "pointer", fontSize: 13, fontWeight: 700, fontFamily: "inherit", transition: "opacity 0.15s", display: "inline-flex", alignItems: "center", gap: 6, ...s }}
      onMouseEnter={e => e.currentTarget.style.opacity = "0.8"}
      onMouseLeave={e => e.currentTarget.style.opacity = "1"}
    >{children}</button>
  );
}

function Card({ children, style: s, onClick }) {
  return (
    <div onClick={onClick} style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, ...s, cursor: onClick ? "pointer" : "default", transition: "border-color 0.15s, background 0.15s" }}
      onMouseEnter={onClick ? e => { e.currentTarget.style.borderColor = C.accent + "50"; e.currentTarget.style.background = C.surface2; } : undefined}
      onMouseLeave={onClick ? e => { e.currentTarget.style.borderColor = C.border; e.currentTarget.style.background = C.surface; } : undefined}
    >{children}</div>
  );
}

function Divider() { return <div style={{ height: 1, background: C.border }} />; }

function InfoRow({ label, value, mono }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", padding: "11px 0", borderBottom: `1px solid ${C.border}` }}>
      <span style={{ color: C.textSub, fontSize: 13, minWidth: 130 }}>{label}</span>
      <span style={{ color: C.text, fontSize: 13, fontWeight: 500, textAlign: "right", fontFamily: mono ? "monospace" : "inherit" }}>{value || "—"}</span>
    </div>
  );
}

function FieldEdit({ label, value, onChange, type = "text", options }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ color: C.textSub, fontSize: 11, letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 5 }}>{label}</div>
      {options ? (
        <select value={value} onChange={e => onChange(e.target.value)} style={{ width: "100%", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 7, padding: "9px 12px", color: C.text, fontSize: 14, fontFamily: "inherit", outline: "none" }}>
          {options.map(o => <option key={o.value ?? o} value={o.value ?? o}>{o.label ?? o}</option>)}
        </select>
      ) : (
        <input type={type} value={value ?? ""} onChange={e => onChange(e.target.value)} style={{ width: "100%", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 7, padding: "9px 12px", color: C.text, fontSize: 14, fontFamily: "inherit", outline: "none", boxSizing: "border-box" }}
          onFocus={e => e.target.style.borderColor = C.accent + "70"}
          onBlur={e => e.target.style.borderColor = C.border}
        />
      )}
    </div>
  );
}

// ─── CALENDAR COMPONENT (แยกออกมาเพื่อ useState ถูกต้อง) ────
function EmployeeCalendar({ emp }) {
  const [calMonth, setCalMonth] = useState(new Date());
  const [selDay, setSelDay] = useState(new Date().getDate());

  const year  = calMonth.getFullYear();
  const month = calMonth.getMonth();
  const monthNameTH = calMonth.toLocaleDateString("th-TH", { month: "long", year: "numeric" });
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDow    = new Date(year, month, 1).getDay();
  const today       = new Date();
  const isToday     = (d) => d === today.getDate() && month === today.getMonth() && year === today.getFullYear();

  // สร้าง mock data แบบ deterministic (seed จาก emp_id + year + month)
  const getStatus = (d) => {
    const date = new Date(year, month, d);
    const dow  = date.getDay();
    if (dow === 0 || dow === 6) return "holiday";
    if (date > today) return "future";
    // deterministic โดยใช้ emp_id + d เป็น seed
    const seed = (emp.emp_id * 31 + d * 7 + month * 13) % 100;
    if (seed < 5)  return "absent";
    if (seed < 12) return "leave";
    if (seed < 18) return "ot";
    return "normal";
  };

  const dayStatus = {
    normal:  { dot: C.accent,   label: "มาทำงาน",  detail: "เข้างาน 08:00 — 17:00" },
    absent:  { dot: C.danger,   label: "ขาดงาน",   detail: "ไม่มีการบันทึกการเข้างาน" },
    leave:   { dot: C.warn,     label: "ลา",        detail: "ลางาน — อนุมัติแล้ว" },
    ot:      { dot: C.blue,     label: "ทำ OT",     detail: "ทำงานล่วงเวลา" },
    holiday: { dot: C.textMuted,label: "วันหยุด",   detail: "วันหยุดประจำสัปดาห์" },
    future:  { dot: "transparent", label: "",       detail: "" },
  };

  // สรุปเดือน
  const summary = { normal: 0, absent: 0, leave: 0, ot: 0 };
  for (let d = 1; d <= daysInMonth; d++) {
    const st = getStatus(d);
    if (summary[st] !== undefined) summary[st]++;
  }

  const selStatus = getStatus(selDay);
  const selDate   = new Date(year, month, selDay);

  return (
    <div>
      {/* Month nav */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <button onClick={() => { setCalMonth(new Date(year, month - 1, 1)); setSelDay(1); }}
          style={{ background: "none", border: "none", color: C.accent, cursor: "pointer", fontSize: 24, padding: "4px 12px", borderRadius: 8 }}>‹</button>
        <div style={{ color: C.text, fontWeight: 700, fontSize: 16 }}>{monthNameTH}</div>
        <button onClick={() => { setCalMonth(new Date(year, month + 1, 1)); setSelDay(1); }}
          style={{ background: "none", border: "none", color: C.accent, cursor: "pointer", fontSize: 24, padding: "4px 12px", borderRadius: 8 }}>›</button>
      </div>

      {/* Day headers */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", marginBottom: 6 }}>
        {["อา","จ","อ","พ","พฤ","ศ","ส"].map((d, i) => (
          <div key={d} style={{ textAlign: "center", color: i === 0 ? C.danger : i === 6 ? C.blue : C.textMuted, fontSize: 11, fontWeight: 600, padding: "4px 0" }}>{d}</div>
        ))}
      </div>

      {/* Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 3, marginBottom: 18 }}>
        {Array(firstDow).fill(null).map((_, i) => <div key={`e${i}`} />)}
        {Array(daysInMonth).fill(null).map((_, i) => {
          const d  = i + 1;
          const st = getStatus(d);
          const ds = dayStatus[st];
          const selected = selDay === d;
          const todayMark = isToday(d);
          return (
            <div key={d} onClick={() => st !== "future" && setSelDay(d)} style={{
              display: "flex", flexDirection: "column", alignItems: "center",
              padding: "7px 2px", borderRadius: 12, cursor: st !== "future" ? "pointer" : "default",
              background: selected ? C.accent : todayMark && !selected ? C.accentBg : "transparent",
              transition: "background 0.15s",
            }}
              onMouseEnter={e => { if (!selected && st !== "future") e.currentTarget.style.background = C.surface2; }}
              onMouseLeave={e => { if (!selected) e.currentTarget.style.background = selected ? C.accent : todayMark ? C.accentBg : "transparent"; }}
            >
              <div style={{
                color: selected ? "#000" : todayMark ? C.accent : st === "holiday" && i % 7 === 0 ? C.danger : st === "future" ? C.textMuted : C.text,
                fontWeight: selected || todayMark ? 800 : 400, fontSize: 15, lineHeight: 1, marginBottom: 4,
              }}>{d}</div>
              <div style={{ width: 5, height: 5, borderRadius: "50%", background: st !== "future" && st !== "holiday" ? (selected ? "#00000060" : ds.dot) : "transparent" }} />
            </div>
          );
        })}
      </div>

      {/* Selected day card */}
      {selStatus && selStatus !== "future" && (
        <div style={{ background: C.surface2, border: `1px solid ${C.border}`, borderRadius: 14, padding: "14px 18px", marginBottom: 16 }}>
          <div style={{ color: C.textSub, fontSize: 12, marginBottom: 8 }}>
            {selDate.toLocaleDateString("th-TH", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ width: 4, height: 40, borderRadius: 2, background: dayStatus[selStatus]?.dot, flexShrink: 0 }} />
            <div>
              <div style={{ color: C.text, fontWeight: 700, fontSize: 15, marginBottom: 3 }}>{dayStatus[selStatus]?.label}</div>
              <div style={{ color: C.textSub, fontSize: 13 }}>{dayStatus[selStatus]?.detail}</div>
            </div>
          </div>
        </div>
      )}

      {/* Monthly summary */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 8 }}>
        {[
          { label: "มาทำงาน", val: summary.normal, color: C.accent },
          { label: "ลา",       val: summary.leave,  color: C.warn },
          { label: "ขาดงาน",  val: summary.absent, color: C.danger },
          { label: "OT",       val: summary.ot,     color: C.blue },
        ].map(s => (
          <div key={s.label} style={{ background: C.surface2, border: `1px solid ${C.border}`, borderRadius: 10, padding: "12px 8px", textAlign: "center" }}>
            <div style={{ color: s.color, fontWeight: 800, fontSize: 24, lineHeight: 1 }}>{s.val}</div>
            <div style={{ color: C.textMuted, fontSize: 10, marginTop: 4 }}>{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}


function EmployeeDetail({ emp, onClose, onSave, addLog }) {
  const [editing, setEditing] = useState(false);
  const [editIncome, setEditIncome] = useState(false);
  const [showOtDetail, setShowOtDetail] = useState(false);
  const [showAdvDetail, setShowAdvDetail] = useState(false);
  const [form, setForm] = useState({ ...emp });
  const [incomeForm, setIncomeForm] = useState({ ot: emp.ot || 0, advance: emp.advance || 0, work_days: emp.work_days || 0, leave_days: emp.leave_days || 0, absent_days: emp.absent_days || 0 });
  const [tab, setTab] = useState("info");
  const color = getColor(emp.full_name);
  const f = (key) => (val) => setForm(p => ({ ...p, [key]: val }));
  const fi = (key) => (val) => setIncomeForm(p => ({ ...p, [key]: val }));

  // Mock OT รายการ (seed จาก emp_id)
  const mockOT = emp.ot > 0 ? [
    { date: `${new Date().getFullYear()}-05-08`, note: "OT งานพิเศษ",        amount: Math.round(emp.ot * 0.5) },
    { date: `${new Date().getFullYear()}-05-15`, note: "OT ล่วงเวลา 2 ชม.",  amount: Math.round(emp.ot * 0.3) },
    { date: `${new Date().getFullYear()}-05-22`, note: "OT วันหยุด",          amount: emp.ot - Math.round(emp.ot * 0.5) - Math.round(emp.ot * 0.3) },
  ].filter(r => r.amount > 0) : [];

  // Mock เบิกล่วงหน้า (seed จาก emp_id)
  const mockAdv = emp.advance > 0 ? [
    { date: `${new Date().getFullYear()}-05-03`, note: "เบิกล่วงหน้าประจำเดือน", amount: emp.advance },
  ] : [];

  // รอบเงินเดือน
  const now = new Date();
  const pStart = now.getDate() >= 6 ? new Date(now.getFullYear(), now.getMonth(), 6) : new Date(now.getFullYear(), now.getMonth() - 1, 6);
  const pEnd   = new Date(pStart.getFullYear(), pStart.getMonth() + 1, 5);
  const fmt    = (d) => d.toLocaleDateString("th-TH", { day: "numeric", month: "short", year: "numeric" });

  const wageTotal  = incomeForm.work_days * emp.daily_wage;
  const netIncome  = wageTotal + Number(incomeForm.ot) - Number(incomeForm.advance);

  const handleSaveInfo = () => {
    // log changes
    const changes = [];
    if (form.daily_wage !== emp.daily_wage) changes.push(`ค่าแรง: ${emp.daily_wage} → ${form.daily_wage} บาท/วัน`);
    if (form.position   !== emp.position)   changes.push(`ตำแหน่ง: ${emp.position} → ${form.position}`);
    if (form.phone      !== emp.phone)       changes.push(`เบอร์โทร: ${emp.phone} → ${form.phone}`);
    if (changes.length > 0) addLog("แก้ไข", "พนักงาน", `แก้ไขข้อมูล ${emp.full_name}: ${changes.join(", ")}`);
    onSave(form);
    setEditing(false);
  };

  const handleSaveIncome = () => {
    const changes = [];
    if (Number(incomeForm.ot)      !== (emp.ot||0))      changes.push(`OT: ${emp.ot||0} → ${incomeForm.ot} บาท`);
    if (Number(incomeForm.advance) !== (emp.advance||0)) changes.push(`เบิกล่วงหน้า: ${emp.advance||0} → ${incomeForm.advance} บาท`);
    if (Number(incomeForm.work_days) !== (emp.work_days||0)) changes.push(`วันทำงาน: ${emp.work_days||0} → ${incomeForm.work_days} วัน`);
    if (changes.length > 0) addLog("แก้ไข", "รายได้", `แก้ไขรายได้ ${emp.full_name}: ${changes.join(", ")}`);
    onSave({ ...emp, ...incomeForm, ot: Number(incomeForm.ot), advance: Number(incomeForm.advance), work_days: Number(incomeForm.work_days), leave_days: Number(incomeForm.leave_days), absent_days: Number(incomeForm.absent_days) });
    setEditIncome(false);
  };

  const tabs = [
    { id: "info",      label: "ข้อมูลส่วนตัว" },
    { id: "work",      label: "ข้อมูลงาน" },
    { id: "income",    label: "💰 รายได้เดือนนี้" },
    { id: "calendar",  label: "📅 ปฏิทิน" },
    { id: "photos",    label: "📷 รูปภาพ" },
    { id: "bank",      label: "บัญชีธนาคาร" },
    { id: "emergency", label: "ฉุกเฉิน" },
  ];

  return (
    <div style={{ position: "fixed", inset: 0, background: "#000000cc", backdropFilter: "blur(6px)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 300, padding: 20, overflowY: "auto" }} onClick={onClose}>
      <div style={{ background: C.surface, border: `1px solid ${C.borderLight}`, borderRadius: 16, width: "100%", maxWidth: 640, boxShadow: "0 32px 80px #00000090", maxHeight: "90vh", overflowY: "auto" }} onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div style={{ padding: "26px 26px 20px", background: `linear-gradient(135deg, ${color}08, transparent 60%)`, borderBottom: `1px solid ${C.border}` }}>
          <div style={{ display: "flex", alignItems: "flex-start", gap: 16 }}>
            <div style={{ position: "relative" }}>
              <Avatar name={form.full_name} size={64} photo={form.photo} />
              {editing && (
                <label style={{ position: "absolute", bottom: -2, right: -2, width: 22, height: 22, borderRadius: "50%", background: C.accent, color: "#000", cursor: "pointer", fontSize: 11, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800 }}>
                  ✏<input type="file" accept="image/*" style={{ display: "none" }} onChange={async e => {
                    const b64 = await readFileAsBase64(e.target.files[0]);
                    setForm(p => ({ ...p, photo: b64 }));
                  }} />
                </label>
              )}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 5, flexWrap: "wrap" }}>
                <span style={{ color: C.text, fontWeight: 800, fontSize: 20 }}>{emp.full_name}</span>
                <Tag type={emp.role} /><Tag type={emp.status} />
              </div>
              <div style={{ color: C.textSub, fontSize: 13, marginBottom: 6 }}>{emp.position} · {emp.emp_code}</div>
              <span style={{ color: C.accent, fontWeight: 800, fontSize: 16 }}>฿{emp.daily_wage?.toLocaleString()}<span style={{ color: C.textSub, fontWeight: 400, fontSize: 11 }}>/วัน</span></span>
            </div>
            {/* Edit buttons — ซ่อนในหน้า income เพราะมีปุ่มแยก */}
            {tab !== "income" && (
              <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
                {editing ? (
                  <>
                    <Btn size="sm" onClick={handleSaveInfo}>💾 บันทึก</Btn>
                    <Btn size="sm" variant="ghost" onClick={() => { setForm({ ...emp }); setEditing(false); }}>ยกเลิก</Btn>
                  </>
                ) : (
                  <Btn size="sm" variant="outline" onClick={() => setEditing(true)}>✏ แก้ไข</Btn>
                )}
              </div>
            )}
            <button onClick={onClose} style={{ background: "none", border: "none", color: C.textSub, cursor: "pointer", fontSize: 20, padding: 4, flexShrink: 0 }}>✕</button>
          </div>
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", borderBottom: `1px solid ${C.border}`, padding: "0 18px", overflowX: "auto" }}>
          {tabs.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} style={{ background: "none", border: "none", padding: "12px 13px", color: tab === t.id ? C.accent : C.textSub, borderBottom: tab === t.id ? `2px solid ${C.accent}` : "2px solid transparent", cursor: "pointer", fontSize: 12, fontWeight: tab === t.id ? 700 : 400, fontFamily: "inherit", marginBottom: -1, whiteSpace: "nowrap" }}>
              {t.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div style={{ padding: "22px 26px" }}>

          {/* ─── INFO ─── */}
          {tab === "info" && (editing ? (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 16px" }}>
              <FieldEdit label="ชื่อ-นามสกุล" value={form.full_name} onChange={f("full_name")} />
              <FieldEdit label="เบอร์โทร" value={form.phone} onChange={f("phone")} />
              <FieldEdit label="เลขบัตรประชาชน" value={form.national_id} onChange={f("national_id")} />
              <FieldEdit label="วันเริ่มงาน" value={form.start_date} onChange={f("start_date")} type="date" />
              <div style={{ gridColumn: "1/-1" }}><FieldEdit label="ที่อยู่" value={form.address} onChange={f("address")} /></div>
            </div>
          ) : (
            <>
              <InfoRow label="ชื่อ-นามสกุล" value={emp.full_name} />
              <InfoRow label="เบอร์โทรศัพท์" value={emp.phone} mono />
              <InfoRow label="เลขบัตรประชาชน" value={emp.national_id} mono />
              <InfoRow label="ที่อยู่" value={emp.address} />
            </>
          ))}

          {/* ─── WORK ─── */}
          {tab === "work" && (editing ? (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 16px" }}>
              <FieldEdit label="รหัสพนักงาน" value={form.emp_code} onChange={f("emp_code")} />
              <FieldEdit label="ตำแหน่ง" value={form.position} onChange={f("position")} options={["หัวหน้างาน","พนักงาน","ขับรถ","คลังสินค้า"]} />
              <FieldEdit label="ค่าแรง/วัน (฿)" value={form.daily_wage} onChange={f("daily_wage")} type="number" />
              <FieldEdit label="สถานะ" value={form.status} onChange={f("status")} options={[{value:"active",label:"ทำงานอยู่"},{value:"inactive",label:"ลาออกแล้ว"}]} />
              <FieldEdit label="สิทธิ์" value={form.role} onChange={f("role")} options={[{value:"admin",label:"Admin"},{value:"employee",label:"พนักงาน"}]} />
              <div style={{ gridColumn: "1/-1" }}><FieldEdit label="หมายเหตุ" value={form.note} onChange={f("note")} /></div>
            </div>
          ) : (
            <>
              <InfoRow label="รหัสพนักงาน" value={emp.emp_code} mono />
              <InfoRow label="ตำแหน่ง" value={emp.position} />
              <InfoRow label="ค่าแรง / วัน" value={`฿${emp.daily_wage?.toLocaleString()}`} />
              <InfoRow label="เงินเดือนประมาณ" value={`฿${(emp.daily_wage * 26)?.toLocaleString()} / เดือน`} />
              <InfoRow label="วันเริ่มงาน" value={emp.start_date} />
              <InfoRow label="สถานะ" value={<Tag type={emp.status} />} />
              <InfoRow label="สิทธิ์ระบบ" value={<Tag type={emp.role} />} />
            </>
          ))}

          {/* ─── INCOME ─── */}
          {tab === "income" && (
            <div>
              {/* Period bar */}
              <div style={{ background: C.accentBg, border: `1px solid ${C.accent}25`, borderRadius: 10, padding: "13px 16px", marginBottom: 16, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ color: C.textMuted, fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 2 }}>รอบเงินเดือน</div>
                  <div style={{ color: C.accent, fontWeight: 700, fontSize: 13 }}>{fmt(pStart)} — {fmt(pEnd)}</div>
                </div>
                {/* Edit toggle for income */}
                {editIncome ? (
                  <div style={{ display: "flex", gap: 8 }}>
                    <Btn size="sm" onClick={handleSaveIncome}>💾 บันทึก</Btn>
                    <Btn size="sm" variant="ghost" onClick={() => { setIncomeForm({ ot: emp.ot||0, advance: emp.advance||0, work_days: emp.work_days||0, leave_days: emp.leave_days||0, absent_days: emp.absent_days||0 }); setEditIncome(false); }}>ยกเลิก</Btn>
                  </div>
                ) : (
                  <Btn size="sm" variant="outline" onClick={() => setEditIncome(true)}>✏ แก้ไข</Btn>
                )}
              </div>

              {/* Day stats — editable */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginBottom: 16 }}>
                {[
                  { label: "วันทำงาน",   key: "work_days",   color: C.accent },
                  { label: "วันลา",      key: "leave_days",  color: C.warn },
                  { label: "วันขาดงาน", key: "absent_days", color: C.danger },
                ].map(s => (
                  <div key={s.key} style={{ background: C.bg, border: `1px solid ${C.border}`, borderRadius: 9, padding: "12px", textAlign: "center" }}>
                    {editIncome ? (
                      <input type="number" value={incomeForm[s.key]} onChange={e => fi(s.key)(e.target.value)} min="0"
                        style={{ width: "100%", background: "transparent", border: "none", borderBottom: `1px solid ${s.color}60`, color: s.color, fontWeight: 800, fontSize: 24, textAlign: "center", outline: "none", fontFamily: "inherit" }} />
                    ) : (
                      <div style={{ color: s.color, fontSize: 28, fontWeight: 800, lineHeight: 1 }}>{incomeForm[s.key]}</div>
                    )}
                    <div style={{ color: C.textMuted, fontSize: 11, marginTop: 5 }}>{s.label}</div>
                  </div>
                ))}
              </div>

              {/* Breakdown — editable */}
              <div style={{ background: C.bg, border: `1px solid ${C.border}`, borderRadius: 10, overflow: "hidden", marginBottom: 14 }}>
                {/* อัตราค่าจ้าง */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", borderBottom: `1px solid ${C.border}` }}>
                  <span style={{ color: C.textSub, fontSize: 13 }}>อัตราค่าจ้าง</span>
                  <span style={{ color: C.text, fontSize: 13, fontFamily: "monospace", fontWeight: 600 }}>฿{emp.daily_wage?.toLocaleString()} / วัน</span>
                </div>
                {/* ค่าแรงรวม */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", borderBottom: `1px solid ${C.border}` }}>
                  <span style={{ color: C.textSub, fontSize: 13 }}>ค่าแรง ({incomeForm.work_days} วัน)</span>
                  <span style={{ color: C.text, fontSize: 13, fontFamily: "monospace", fontWeight: 600 }}>฿{wageTotal.toLocaleString()}</span>
                </div>

                {/* OT — expandable */}
                <div style={{ borderBottom: `1px solid ${C.border}` }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", cursor: editIncome ? "default" : "pointer" }}
                    onClick={() => !editIncome && setShowOtDetail(v => !v)}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ color: C.textSub, fontSize: 13 }}>OT</span>
                      {!editIncome && (
                        <span style={{ color: C.textMuted, fontSize: 11, background: C.surface2, border: `1px solid ${C.border}`, borderRadius: 4, padding: "1px 6px" }}>
                          {mockOT.length} รายการ {showOtDetail ? "▲" : "▼"}
                        </span>
                      )}
                    </div>
                    {editIncome ? (
                      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                        <span style={{ color: C.accent, fontSize: 13 }}>+ ฿</span>
                        <input type="number" value={incomeForm.ot} onChange={e => fi("ot")(e.target.value)} min="0"
                          style={{ width: 80, background: C.surface2, border: `1px solid ${C.accent}50`, borderRadius: 6, padding: "4px 8px", color: C.accent, fontSize: 13, fontFamily: "monospace", textAlign: "right", outline: "none" }} />
                      </div>
                    ) : (
                      <span style={{ color: C.accent, fontSize: 13, fontFamily: "monospace", fontWeight: 600 }}>+ ฿{Number(incomeForm.ot).toLocaleString()}</span>
                    )}
                  </div>
                  {/* OT detail rows */}
                  {showOtDetail && !editIncome && (
                    <div style={{ background: C.surface2, borderTop: `1px solid ${C.border}` }}>
                      {mockOT.map((item, i) => (
                        <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 20px", borderBottom: i < mockOT.length - 1 ? `1px solid ${C.border}` : "none" }}>
                          <div>
                            <div style={{ color: C.text, fontSize: 13, fontWeight: 500 }}>{item.date}</div>
                            <div style={{ color: C.textMuted, fontSize: 11, marginTop: 2 }}>{item.note}</div>
                          </div>
                          <span style={{ color: C.accent, fontFamily: "monospace", fontWeight: 700, fontSize: 14 }}>+ ฿{item.amount.toLocaleString()}</span>
                        </div>
                      ))}
                      <div style={{ display: "flex", justifyContent: "space-between", padding: "10px 20px", borderTop: `1px solid ${C.accent}30`, background: C.accentBg }}>
                        <span style={{ color: C.accent, fontSize: 12, fontWeight: 700 }}>รวม OT</span>
                        <span style={{ color: C.accent, fontFamily: "monospace", fontWeight: 800 }}>฿{mockOT.reduce((s, r) => s + r.amount, 0).toLocaleString()}</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* เบิกล่วงหน้า — expandable */}
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", cursor: editIncome ? "default" : "pointer" }}
                    onClick={() => !editIncome && setShowAdvDetail(v => !v)}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ color: C.textSub, fontSize: 13 }}>เบิกล่วงหน้า</span>
                      {!editIncome && (
                        <span style={{ color: C.textMuted, fontSize: 11, background: C.surface2, border: `1px solid ${C.border}`, borderRadius: 4, padding: "1px 6px" }}>
                          {mockAdv.length} รายการ {showAdvDetail ? "▲" : "▼"}
                        </span>
                      )}
                    </div>
                    {editIncome ? (
                      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                        <span style={{ color: C.danger, fontSize: 13 }}>- ฿</span>
                        <input type="number" value={incomeForm.advance} onChange={e => fi("advance")(e.target.value)} min="0"
                          style={{ width: 80, background: C.surface2, border: `1px solid ${C.danger}50`, borderRadius: 6, padding: "4px 8px", color: C.danger, fontSize: 13, fontFamily: "monospace", textAlign: "right", outline: "none" }} />
                      </div>
                    ) : (
                      <span style={{ color: C.danger, fontSize: 13, fontFamily: "monospace", fontWeight: 600 }}>- ฿{Number(incomeForm.advance).toLocaleString()}</span>
                    )}
                  </div>
                  {/* Advance detail rows */}
                  {showAdvDetail && !editIncome && (
                    <div style={{ background: C.surface2, borderTop: `1px solid ${C.border}` }}>
                      {mockAdv.map((item, i) => (
                        <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 20px", borderBottom: i < mockAdv.length - 1 ? `1px solid ${C.border}` : "none" }}>
                          <div>
                            <div style={{ color: C.text, fontSize: 13, fontWeight: 500 }}>{item.date}</div>
                            <div style={{ color: C.textMuted, fontSize: 11, marginTop: 2 }}>{item.note}</div>
                          </div>
                          <span style={{ color: C.danger, fontFamily: "monospace", fontWeight: 700, fontSize: 14 }}>- ฿{item.amount.toLocaleString()}</span>
                        </div>
                      ))}
                      <div style={{ display: "flex", justifyContent: "space-between", padding: "10px 20px", borderTop: `1px solid ${C.danger}30`, background: C.dangerBg }}>
                        <span style={{ color: C.danger, fontSize: 12, fontWeight: 700 }}>รวมเบิก</span>
                        <span style={{ color: C.danger, fontFamily: "monospace", fontWeight: 800 }}>฿{mockAdv.reduce((s, r) => s + r.amount, 0).toLocaleString()}</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Net */}
              <div style={{ background: `linear-gradient(135deg, ${C.accent}14, ${C.accent}06)`, border: `1px solid ${C.accent}35`, borderRadius: 10, padding: "16px 20px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <div style={{ color: C.textSub, fontSize: 13, marginBottom: 3 }}>รายได้รวมปัจจุบัน</div>
                  <div style={{ color: C.textMuted, fontSize: 11 }}>คำนวณถึงวันนี้ · {incomeForm.work_days} วันทำงาน</div>
                </div>
                <div style={{ color: C.accent, fontWeight: 800, fontSize: 30 }}>฿{netIncome.toLocaleString()}</div>
              </div>
            </div>
          )}

          {/* ─── CALENDAR ─── */}
          {tab === "calendar" && <EmployeeCalendar emp={emp} />}

          {/* ─── PHOTOS ─── */}
          {tab === "photos" && (
            <div>
              {/* รูปพนักงาน */}
              <div style={{ marginBottom: 28 }}>
                <div style={{ color: C.text, fontWeight: 700, fontSize: 14, marginBottom: 4 }}>รูปพนักงาน</div>
                <div style={{ color: C.textMuted, fontSize: 12, marginBottom: 16 }}>รูปถ่ายหน้าตรง ใช้แสดงในระบบ</div>
                <div style={{ display: "flex", alignItems: "flex-start", gap: 20 }}>
                  {/* Preview */}
                  <div style={{ flexShrink: 0 }}>
                    {form.photo ? (
                      <div style={{ position: "relative" }}>
                        <img src={form.photo} alt="รูปพนักงาน" style={{ width: 100, height: 100, borderRadius: "50%", objectFit: "cover", border: `3px solid ${C.accent}50`, display: "block" }} />
                        <button onClick={() => { setForm(p => ({ ...p, photo: null })); addLog("แก้ไข", "พนักงาน", `ลบรูปพนักงาน ${emp.full_name}`); }}
                          style={{ position: "absolute", top: -4, right: -4, width: 22, height: 22, borderRadius: "50%", background: C.danger, border: "none", color: "#fff", cursor: "pointer", fontSize: 12, fontWeight: 800, display: "flex", alignItems: "center", justifyContent: "center" }}>✕</button>
                      </div>
                    ) : (
                      <div style={{ width: 100, height: 100, borderRadius: "50%", background: C.surface2, border: `2px dashed ${C.border}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 32, color: C.textMuted }}>
                        {emp.full_name.charAt(0)}
                      </div>
                    )}
                  </div>
                  <div style={{ flex: 1 }}>
                    <PhotoUpload label="" value={null} onChange={async (b64) => {
                      setForm(p => ({ ...p, photo: b64 }));
                      onSave({ ...form, photo: b64 });
                      addLog("แก้ไข", "พนักงาน", `อัปโหลดรูปพนักงาน ${emp.full_name}`);
                    }} round={false} />
                    <div style={{ color: C.textMuted, fontSize: 11 }}>รองรับ JPG, PNG, WEBP · แนะนำ 1:1</div>
                  </div>
                </div>
              </div>

              <div style={{ height: 1, background: C.border, marginBottom: 24 }} />

              {/* รูปบัตรประชาชน */}
              <div>
                <div style={{ color: C.text, fontWeight: 700, fontSize: 14, marginBottom: 4 }}>รูปบัตรประจำตัวประชาชน</div>
                <div style={{ color: C.textMuted, fontSize: 12, marginBottom: 16 }}>ถ่ายรูปหน้าบัตร ชัดเจน อ่านได้</div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                  {/* หน้าบัตร */}
                  <div>
                    <div style={{ color: C.textSub, fontSize: 11, letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 8 }}>หน้าบัตร (ด้านหน้า)</div>
                    {form.id_card_front ? (
                      <div style={{ position: "relative" }}>
                        <img src={form.id_card_front} alt="หน้าบัตร" style={{ width: "100%", height: 130, objectFit: "cover", borderRadius: 10, border: `2px solid ${C.accent}40`, display: "block" }} />
                        <button onClick={() => setForm(p => ({ ...p, id_card_front: null }))}
                          style={{ position: "absolute", top: 6, right: 6, width: 22, height: 22, borderRadius: "50%", background: C.danger, border: "none", color: "#fff", cursor: "pointer", fontSize: 11, fontWeight: 800, display: "flex", alignItems: "center", justifyContent: "center" }}>✕</button>
                        <label style={{ position: "absolute", bottom: 6, right: 6, background: C.accent, color: "#000", borderRadius: 6, padding: "4px 8px", fontSize: 10, fontWeight: 800, cursor: "pointer", display: "flex", alignItems: "center", gap: 4 }}>
                          ✏ เปลี่ยน<input type="file" accept="image/*" style={{ display: "none" }} onChange={async e => { const b64 = await readFileAsBase64(e.target.files[0]); setForm(p => ({ ...p, id_card_front: b64 })); onSave({ ...form, id_card_front: b64 }); addLog("แก้ไข", "พนักงาน", `อัปโหลดบัตรประชาชน (หน้า) ${emp.full_name}`); }} />
                        </label>
                      </div>
                    ) : (
                      <label style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: 130, borderRadius: 10, border: `2px dashed ${C.border}`, background: C.bg, cursor: "pointer", gap: 8, transition: "all 0.15s" }}
                        onMouseEnter={e => e.currentTarget.style.borderColor = C.accent + "60"}
                        onMouseLeave={e => e.currentTarget.style.borderColor = C.border}
                      >
                        <span style={{ fontSize: 28 }}>🪪</span>
                        <span style={{ color: C.textMuted, fontSize: 11 }}>คลิกอัปโหลด</span>
                        <input type="file" accept="image/*" style={{ display: "none" }} onChange={async e => { const b64 = await readFileAsBase64(e.target.files[0]); setForm(p => ({ ...p, id_card_front: b64 })); onSave({ ...form, id_card_front: b64 }); addLog("แก้ไข", "พนักงาน", `อัปโหลดบัตรประชาชน (หน้า) ${emp.full_name}`); }} />
                      </label>
                    )}
                  </div>

                  {/* หลังบัตร */}
                  <div>
                    <div style={{ color: C.textSub, fontSize: 11, letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 8 }}>หลังบัตร (ด้านหลัง)</div>
                    {form.id_card_back ? (
                      <div style={{ position: "relative" }}>
                        <img src={form.id_card_back} alt="หลังบัตร" style={{ width: "100%", height: 130, objectFit: "cover", borderRadius: 10, border: `2px solid ${C.blue}40`, display: "block" }} />
                        <button onClick={() => setForm(p => ({ ...p, id_card_back: null }))}
                          style={{ position: "absolute", top: 6, right: 6, width: 22, height: 22, borderRadius: "50%", background: C.danger, border: "none", color: "#fff", cursor: "pointer", fontSize: 11, fontWeight: 800, display: "flex", alignItems: "center", justifyContent: "center" }}>✕</button>
                        <label style={{ position: "absolute", bottom: 6, right: 6, background: C.blue, color: "#000", borderRadius: 6, padding: "4px 8px", fontSize: 10, fontWeight: 800, cursor: "pointer", display: "flex", alignItems: "center", gap: 4 }}>
                          ✏ เปลี่ยน<input type="file" accept="image/*" style={{ display: "none" }} onChange={async e => { const b64 = await readFileAsBase64(e.target.files[0]); setForm(p => ({ ...p, id_card_back: b64 })); onSave({ ...form, id_card_back: b64 }); addLog("แก้ไข", "พนักงาน", `อัปโหลดบัตรประชาชน (หลัง) ${emp.full_name}`); }} />
                        </label>
                      </div>
                    ) : (
                      <label style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: 130, borderRadius: 10, border: `2px dashed ${C.border}`, background: C.bg, cursor: "pointer", gap: 8, transition: "all 0.15s" }}
                        onMouseEnter={e => e.currentTarget.style.borderColor = C.blue + "60"}
                        onMouseLeave={e => e.currentTarget.style.borderColor = C.border}
                      >
                        <span style={{ fontSize: 28 }}>🪪</span>
                        <span style={{ color: C.textMuted, fontSize: 11 }}>คลิกอัปโหลด</span>
                        <input type="file" accept="image/*" style={{ display: "none" }} onChange={async e => { const b64 = await readFileAsBase64(e.target.files[0]); setForm(p => ({ ...p, id_card_back: b64 })); onSave({ ...form, id_card_back: b64 }); addLog("แก้ไข", "พนักงาน", `อัปโหลดบัตรประชาชน (หลัง) ${emp.full_name}`); }} />
                      </label>
                    )}
                  </div>
                </div>

                {/* สถานะ */}
                <div style={{ marginTop: 16, padding: "12px 16px", background: C.surface2, borderRadius: 8, border: `1px solid ${C.border}`, display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: C.textSub, fontSize: 13 }}>สถานะเอกสาร</span>
                  <span style={{
                    color: (form.id_card_front && form.id_card_back) ? C.accent : form.id_card_front ? C.warn : C.danger,
                    fontSize: 13, fontWeight: 700,
                  }}>
                    {(form.id_card_front && form.id_card_back) ? "✓ ครบถ้วน" : form.id_card_front ? "⚠ ขาดด้านหลัง" : "✗ ยังไม่มีเอกสาร"}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* ─── BANK ─── */}
          {tab === "bank" && (editing ? (
            <div>
              <FieldEdit label="ธนาคาร" value={form.bank} onChange={f("bank")} options={["กสิกรไทย","ไทยพาณิชย์","กรุงไทย","กรุงเทพ","ออมสิน"]} />
              <FieldEdit label="เลขบัญชี" value={form.bank_account} onChange={f("bank_account")} />
            </div>
          ) : (
            <>
              <InfoRow label="ธนาคาร" value={emp.bank} />
              <InfoRow label="เลขบัญชี" value={emp.bank_account} mono />
              <InfoRow label="ชื่อบัญชี" value={emp.full_name} />
            </>
          ))}

          {/* ─── EMERGENCY ─── */}
          {tab === "emergency" && (editing ? (
            <div>
              <FieldEdit label="ชื่อผู้ติดต่อ" value={form.emergency_name} onChange={f("emergency_name")} />
              <FieldEdit label="เบอร์โทร" value={form.emergency_phone} onChange={f("emergency_phone")} />
            </div>
          ) : (
            <>
              <InfoRow label="ชื่อผู้ติดต่อ" value={emp.emergency_name} />
              <InfoRow label="เบอร์โทรศัพท์" value={emp.emergency_phone} mono />
            </>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── SYSTEM LOG PAGE ─────────────────────────────────────────
function LogPage({ logs }) {
  const [filter, setFilter] = useState("ทั้งหมด");
  const actions = ["ทั้งหมด", "เพิ่ม", "แก้ไข", "ลบ", "อนุมัติ", "อัตโนมัติ"];
  const filtered = filter === "ทั้งหมด" ? logs : logs.filter(l => l.action === filter);

  const actionIcon = { เพิ่ม: "＋", แก้ไข: "✏", ลบ: "✕", อนุมัติ: "✓", อัตโนมัติ: "⟳" };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ color: C.text, fontSize: 24, fontWeight: 800, margin: 0 }}>Log ระบบ</h1>
        <div style={{ color: C.textMuted, fontSize: 12, marginTop: 3 }}>{logs.length} รายการทั้งหมด</div>
      </div>

      {/* Filter */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
        {actions.map(a => (
          <button key={a} onClick={() => setFilter(a)} style={{
            padding: "7px 14px", borderRadius: 8, border: `1px solid ${filter === a ? C.accent : C.border}`,
            background: filter === a ? C.accentBg : "transparent",
            color: filter === a ? C.accent : C.textSub,
            cursor: "pointer", fontSize: 12, fontWeight: filter === a ? 700 : 400, fontFamily: "inherit",
          }}>{a}</button>
        ))}
      </div>

      <Card>
        {filtered.length === 0 && <div style={{ padding: 40, textAlign: "center", color: C.textMuted }}>ไม่มีรายการ</div>}
        {filtered.map((log, i) => (
          <div key={log.id}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: 14, padding: "15px 22px", transition: "background 0.1s" }}
              onMouseEnter={e => e.currentTarget.style.background = C.surface2}
              onMouseLeave={e => e.currentTarget.style.background = "transparent"}
            >
              {/* Icon */}
              <div style={{
                width: 34, height: 34, borderRadius: "50%", flexShrink: 0,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 14, fontWeight: 800,
                background: log.action === "เพิ่ม" ? C.accentBg : log.action === "ลบ" ? C.dangerBg : log.action === "แก้ไข" ? C.blueBg : log.action === "อนุมัติ" ? C.warnBg : C.surface2,
                color: log.action === "เพิ่ม" ? C.accent : log.action === "ลบ" ? C.danger : log.action === "แก้ไข" ? C.blue : log.action === "อนุมัติ" ? C.warn : C.textSub,
                border: `1px solid currentColor`,
              }}>
                {actionIcon[log.action] || "·"}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4, flexWrap: "wrap" }}>
                  <Tag type={log.action} />
                  <span style={{ color: C.textSub, fontSize: 12 }}>{log.target}</span>
                  <span style={{ color: C.textMuted, fontSize: 11, marginLeft: "auto" }}>🕐 {log.ts}</span>
                </div>
                <div style={{ color: C.text, fontSize: 13, fontWeight: 500, marginBottom: 3 }}>{log.detail}</div>
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <Avatar name={log.user} size={18} />
                  <span style={{ color: C.textSub, fontSize: 12 }}>{log.user}</span>
                </div>
              </div>
            </div>
            {i < filtered.length - 1 && <Divider />}
          </div>
        ))}
      </Card>
    </div>
  );
}

// ─── OTHER PAGES ─────────────────────────────────────────────
function Dashboard({ employees, onSelectEmp }) {
  const present = ATTENDANCE.filter(a => a.status === "normal").length;
  const absent  = ATTENDANCE.filter(a => a.status === "absent").length;
  const today   = new Date().toLocaleDateString("th-TH", { weekday: "long", year: "numeric", month: "long", day: "numeric" });
  return (
    <div>
      <div style={{ marginBottom: 26 }}>
        <div style={{ color: C.textMuted, fontSize: 12, marginBottom: 3 }}>{today}</div>
        <h1 style={{ color: C.text, fontSize: 24, fontWeight: 800, margin: 0 }}>ภาพรวมวันนี้</h1>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 14, marginBottom: 26 }}>
        {[
          { label: "พนักงานทั้งหมด", value: employees.length, color: C.blue   },
          { label: "มาทำงาน",         value: present,           color: C.accent, sub: `${Math.round(present/employees.length*100)}%` },
          { label: "ขาดงาน",          value: absent,            color: C.danger },
        ].map(s => (
          <Card key={s.label} style={{ padding: "18px 20px", position: "relative", overflow: "hidden" }}>
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, ${s.color}90, transparent)` }} />
            <div style={{ color: C.textMuted, fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 8 }}>{s.label}</div>
            <div style={{ color: s.color, fontSize: 38, fontWeight: 800, lineHeight: 1 }}>{s.value}</div>
            {s.sub && <div style={{ color: C.textMuted, fontSize: 11, marginTop: 4 }}>{s.sub}</div>}
          </Card>
        ))}
      </div>
      <Card>
        <div style={{ padding: "14px 20px", display: "flex", justifyContent: "space-between" }}>
          <span style={{ color: C.text, fontWeight: 700 }}>การเข้างานวันนี้</span>
          <span style={{ color: C.textMuted, fontSize: 12 }}>{ATTENDANCE.length} คน</span>
        </div>
        <Divider />
        {ATTENDANCE.map((a, i) => {
          const emp = employees.find(e => e.emp_id === a.emp_id);
          return (
            <div key={a.emp_id}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "11px 20px", cursor: "pointer", transition: "background 0.1s" }}
                onClick={() => emp && onSelectEmp(emp)}
                onMouseEnter={e => e.currentTarget.style.background = C.surface2}
                onMouseLeave={e => e.currentTarget.style.background = "transparent"}
              >
                <Avatar name={a.full_name} size={32} />
                <div style={{ flex: 1, color: C.text, fontWeight: 600, fontSize: 13 }}>{a.full_name}</div>
                <Tag type={a.status} />
                <div style={{ color: C.textSub, fontSize: 12, minWidth: 42, textAlign: "right", fontFamily: "monospace" }}>{a.check_in || "—"}</div>
                <div style={{ color: C.textMuted, fontSize: 12, minWidth: 42, textAlign: "right", fontFamily: "monospace" }}>{a.check_out || "—"}</div>
              </div>
              {i < ATTENDANCE.length - 1 && <Divider />}
            </div>
          );
        })}
      </Card>
    </div>
  );
}

function Employees({ employees, setEmployees, addLog }) {
  const [selected, setSelected] = useState(null);
  const [showAdd, setShowAdd] = useState(false);
  const [search, setSearch] = useState("");
  const blank = { full_name:"", daily_wage:"", position:"พนักงาน", phone:"", national_id:"", start_date: new Date().toISOString().split("T")[0], status:"active", role:"employee", bank:"", bank_account:"", address:"", ot:0, advance:0, work_days:0, leave_days:0, absent_days:0, emergency_name:"", emergency_phone:"", note:"" };
  const [newEmp, setNewEmp] = useState({ ...blank });

  const filtered = employees.filter(e => e.full_name.includes(search) || e.emp_code?.includes(search) || e.position.includes(search));

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 18 }}>
        <div>
          <h1 style={{ color: C.text, fontSize: 24, fontWeight: 800, margin: 0 }}>พนักงาน</h1>
          <div style={{ color: C.textMuted, fontSize: 12, marginTop: 3 }}>{employees.length} คนในระบบ</div>
        </div>
        <Btn onClick={() => setShowAdd(true)}>+ เพิ่มพนักงาน</Btn>
      </div>
      <div style={{ position: "relative", marginBottom: 16 }}>
        <span style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: C.textMuted }}>🔍</span>
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="ค้นหาชื่อ รหัส ตำแหน่ง..." style={{ width: "100%", background: C.surface, border: `1px solid ${C.border}`, borderRadius: 9, padding: "10px 14px 10px 36px", color: C.text, fontSize: 13, fontFamily: "inherit", outline: "none", boxSizing: "border-box" }} />
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(250px,1fr))", gap: 12 }}>
        {filtered.map(emp => (
          <Card key={emp.emp_id} onClick={() => setSelected(emp)} style={{ padding: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
              <Avatar name={emp.full_name} size={44} photo={emp.photo} />
              <div style={{ flex: 1 }}>
                <div style={{ color: C.text, fontWeight: 700, fontSize: 14 }}>{emp.full_name}</div>
                <div style={{ color: C.textSub, fontSize: 11, marginTop: 2 }}>{emp.emp_code} · {emp.position}</div>
              </div>
              <Tag type={emp.role} />
            </div>
            <Divider />
            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 12 }}>
              <div><div style={{ color: C.textMuted, fontSize: 10, marginBottom: 2 }}>ค่าแรง/วัน</div><div style={{ color: C.accent, fontWeight: 800, fontSize: 18 }}>฿{emp.daily_wage?.toLocaleString()}</div></div>
              <div style={{ textAlign: "right" }}><div style={{ color: C.textMuted, fontSize: 10, marginBottom: 2 }}>เบอร์โทร</div><div style={{ color: C.textSub, fontSize: 11, fontFamily: "monospace" }}>{emp.phone || "—"}</div></div>
            </div>
          </Card>
        ))}
      </div>

      {selected && (
        <EmployeeDetail emp={selected} onClose={() => setSelected(null)} addLog={addLog}
          onSave={u => { setEmployees(employees.map(e => e.emp_id === u.emp_id ? u : e)); setSelected(u); }} />
      )}

      {showAdd && (
        <div style={{ position: "fixed", inset: 0, background: "#000c", backdropFilter: "blur(4px)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 300, padding: 20 }} onClick={() => setShowAdd(false)}>
          <div style={{ background: C.surface, border: `1px solid ${C.borderLight}`, borderRadius: 16, padding: 26, width: "100%", maxWidth: 500, maxHeight: "90vh", overflowY: "auto" }} onClick={e => e.stopPropagation()}>
            <div style={{ color: C.text, fontWeight: 700, fontSize: 16, marginBottom: 20 }}>เพิ่มพนักงานใหม่</div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 14px" }}>
              <FieldEdit label="ชื่อ-นามสกุล" value={newEmp.full_name} onChange={v => setNewEmp({...newEmp, full_name:v})} />
              <FieldEdit label="ค่าแรง/วัน (฿)" value={newEmp.daily_wage} onChange={v => setNewEmp({...newEmp, daily_wage:v})} type="number" />
              <FieldEdit label="ตำแหน่ง" value={newEmp.position} onChange={v => setNewEmp({...newEmp, position:v})} options={["พนักงาน","หัวหน้างาน","ขับรถ","คลังสินค้า"]} />
              <FieldEdit label="เบอร์โทร" value={newEmp.phone} onChange={v => setNewEmp({...newEmp, phone:v})} />
              <FieldEdit label="เลขบัตรประชาชน" value={newEmp.national_id} onChange={v => setNewEmp({...newEmp, national_id:v})} />
              <FieldEdit label="ธนาคาร" value={newEmp.bank} onChange={v => setNewEmp({...newEmp, bank:v})} options={["","กสิกรไทย","ไทยพาณิชย์","กรุงไทย","กรุงเทพ"]} />
              <FieldEdit label="เลขบัญชี" value={newEmp.bank_account} onChange={v => setNewEmp({...newEmp, bank_account:v})} />
              <div style={{ gridColumn:"1/-1" }}><FieldEdit label="ที่อยู่" value={newEmp.address} onChange={v => setNewEmp({...newEmp, address:v})} /></div>
            </div>
            <div style={{ display: "flex", gap: 10 }}>
              <Btn style={{ flex: 1 }} onClick={() => {
                if (!newEmp.full_name || !newEmp.daily_wage) return;
                const id = Math.max(...employees.map(e => e.emp_id)) + 1;
                const emp = { ...newEmp, emp_id: id, emp_code: `EMP${String(id).padStart(3,"0")}`, daily_wage: Number(newEmp.daily_wage) };
                setEmployees([...employees, emp]);
                addLog("เพิ่ม", "พนักงาน", `เพิ่มพนักงาน ${newEmp.full_name} (${emp.emp_code}) ค่าแรง ฿${newEmp.daily_wage}/วัน`);
                setShowAdd(false); setNewEmp({...blank});
              }}>บันทึก</Btn>
              <Btn variant="ghost" style={{ flex: 1 }} onClick={() => setShowAdd(false)}>ยกเลิก</Btn>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Leave({ employees, addLog }) {
  const [leaves, setLeaves] = useState([
    { id: 1, full_name: "ทอง",  leave_type: "sick",     start_date: "2026-05-12", end_date: "2026-05-12", total_days: 1, reason: "ไม่สบาย",       status: "pending" },
    { id: 2, full_name: "ดู",   leave_type: "personal", start_date: "2026-05-13", end_date: "2026-05-14", total_days: 2, reason: "ธุระส่วนตัว",    status: "pending" },
    { id: 3, full_name: "เขียว",leave_type: "vacation", start_date: "2026-05-20", end_date: "2026-05-22", total_days: 3, reason: "พักผ่อน",        status: "approved" },
    { id: 4, full_name: "จอ",   leave_type: "sick",     start_date: "2026-04-10", end_date: "2026-04-10", total_days: 1, reason: "ปวดหัว",          status: "rejected" },
  ]);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ emp_id:"", leave_type:"sick", start_date:"", end_date:"", reason:"" });
  const pending = leaves.filter(l => l.status === "pending");
  const history = leaves.filter(l => l.status !== "pending");
  const typeLabel = { sick:"ลาป่วย", personal:"ลากิจ", vacation:"ลาพักร้อน" };

  const approve = (l) => { setLeaves(leaves.map(x => x.id===l.id ? {...x,status:"approved"} : x)); addLog("อนุมัติ","ใบลา",`อนุมัติใบ${typeLabel[l.leave_type]}ของ ${l.full_name} ${l.total_days} วัน`); };
  const reject  = (l) => { setLeaves(leaves.map(x => x.id===l.id ? {...x,status:"rejected"} : x)); addLog("แก้ไข","ใบลา",`ปฏิเสธใบ${typeLabel[l.leave_type]}ของ ${l.full_name}`); };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 22 }}>
        <div><h1 style={{ color: C.text, fontSize: 24, fontWeight: 800, margin: 0 }}>การลา</h1><div style={{ color: C.textMuted, fontSize: 12, marginTop: 3 }}>{pending.length} รายการรออนุมัติ</div></div>
        <Btn onClick={() => setShowAdd(true)}>+ บันทึกการลา</Btn>
      </div>
      {pending.length > 0 && <>
        <div style={{ color: C.textSub, fontSize: 11, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 10 }}>รออนุมัติ</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 22 }}>
          {pending.map(l => (
            <Card key={l.id} style={{ padding: "15px 18px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <Avatar name={l.full_name} size={40} />
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}><span style={{ color: C.text, fontWeight: 700 }}>{l.full_name}</span><Tag type={l.leave_type} /></div>
                  <div style={{ color: C.textSub, fontSize: 12 }}>{l.start_date}{l.total_days>1?` – ${l.end_date}`:""} · {l.total_days} วัน{l.reason&&` · ${l.reason}`}</div>
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  <Btn size="sm" onClick={() => approve(l)}>✓ อนุมัติ</Btn>
                  <Btn size="sm" variant="danger" onClick={() => reject(l)}>✗ ปฏิเสธ</Btn>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </>}
      <div style={{ color: C.textSub, fontSize: 11, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 10 }}>ประวัติ</div>
      <Card>{history.map((l, i) => (
        <div key={l.id}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 18px" }}>
            <Avatar name={l.full_name} size={32} />
            <div style={{ flex: 1 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}><span style={{ color: C.text, fontWeight: 600, fontSize: 13 }}>{l.full_name}</span><Tag type={l.leave_type} /></div>
              <div style={{ color: C.textMuted, fontSize: 11 }}>{l.start_date} · {l.total_days} วัน</div>
            </div>
            <Tag type={l.status} />
          </div>
          {i < history.length-1 && <Divider />}
        </div>
      ))}</Card>
      {showAdd && (
        <div style={{ position:"fixed",inset:0,background:"#000c",backdropFilter:"blur(4px)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:300,padding:20 }} onClick={() => setShowAdd(false)}>
          <div style={{ background:C.surface,border:`1px solid ${C.borderLight}`,borderRadius:16,padding:26,width:"100%",maxWidth:420 }} onClick={e=>e.stopPropagation()}>
            <div style={{ color:C.text,fontWeight:700,fontSize:16,marginBottom:18 }}>บันทึกการลา</div>
            <FieldEdit label="พนักงาน" value={form.emp_id} onChange={v=>setForm({...form,emp_id:v})} options={[{value:"",label:"เลือกพนักงาน"},...employees.map(e=>({value:e.emp_id,label:e.full_name}))]} />
            <FieldEdit label="ประเภท" value={form.leave_type} onChange={v=>setForm({...form,leave_type:v})} options={[{value:"sick",label:"ลาป่วย"},{value:"personal",label:"ลากิจ"},{value:"vacation",label:"ลาพักร้อน"}]} />
            <div style={{ display:"grid",gridTemplateColumns:"1fr 1fr",gap:12 }}>
              <FieldEdit label="วันเริ่ม" value={form.start_date} onChange={v=>setForm({...form,start_date:v})} type="date" />
              <FieldEdit label="วันสิ้นสุด" value={form.end_date} onChange={v=>setForm({...form,end_date:v})} type="date" />
            </div>
            <FieldEdit label="เหตุผล" value={form.reason} onChange={v=>setForm({...form,reason:v})} />
            <div style={{ display:"flex",gap:10 }}>
              <Btn style={{flex:1}} onClick={() => {
                if (!form.emp_id||!form.start_date) return;
                const emp = employees.find(e=>e.emp_id===Number(form.emp_id));
                const days = form.end_date ? Math.ceil((new Date(form.end_date)-new Date(form.start_date))/86400000)+1 : 1;
                const newLeave = {id:Date.now(),full_name:emp.full_name,...form,total_days:days,status:"pending"};
                setLeaves([newLeave,...leaves]);
                addLog("เพิ่ม","ใบลา",`บันทึกใบ${typeLabel[form.leave_type]} ${emp.full_name} ${days} วัน`);
                setShowAdd(false);
              }}>บันทึก</Btn>
              <Btn variant="ghost" style={{flex:1}} onClick={()=>setShowAdd(false)}>ยกเลิก</Btn>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Payroll({ employees }) {
  const [sel, setSel] = useState(null);
  const period = "6 พ.ค. — 5 มิ.ย. 2569";
  const calc = (e) => { const d=e.work_days||22; return { days:d, ot:e.ot||0, adv:e.advance||0, total:d*e.daily_wage+(e.ot||0)-(e.advance||0) }; };

  const printSlip = (emp, p) => {
    const win = window.open("", "_blank");
    win.document.write(`
      <html><head><meta charset="UTF-8"><title>สลิปเงินเดือน ${emp.full_name}</title>
      <style>
        body { font-family: 'Sarabun', sans-serif; margin: 0; background: #fff; color: #111; }
        @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700;800&display=swap');
        .slip { max-width: 420px; margin: 40px auto; padding: 32px; border: 1px solid #ddd; border-radius: 12px; }
        .header { text-align: center; margin-bottom: 24px; border-bottom: 2px solid #111; padding-bottom: 16px; }
        .company { font-size: 22px; font-weight: 800; }
        .sub { font-size: 13px; color: #666; }
        .emp { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; padding: 14px; background: #f8f8f8; border-radius: 8px; }
        .emp-name { font-size: 17px; font-weight: 700; }
        .emp-sub { font-size: 12px; color: #666; }
        .row { display: flex; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid #eee; font-size: 14px; }
        .row.total { border-top: 2px solid #111; border-bottom: none; margin-top: 8px; padding-top: 14px; font-weight: 800; font-size: 18px; }
        .green { color: #00a855; }
        .red { color: #e53935; }
        .footer { text-align: center; margin-top: 24px; font-size: 11px; color: #aaa; }
      </style></head><body>
      <div class="slip">
        <div class="header">
          <div class="company">♻ มนทชัย รีไซเคิล</div>
          <div class="sub">สลิปเงินเดือน · รอบ ${period}</div>
        </div>
        <div class="emp">
          <div style="width:48px;height:48px;border-radius:50%;background:#00e67620;border:2px solid #00e67650;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:800;color:#00a855">${emp.full_name.charAt(0)}</div>
          <div><div class="emp-name">${emp.full_name}</div><div class="emp-sub">${emp.emp_code} · ${emp.position}</div></div>
        </div>
        <div class="row"><span>วันทำงาน</span><span>${p.days} วัน</span></div>
        <div class="row"><span>อัตราค่าแรง</span><span>฿${emp.daily_wage?.toLocaleString()} / วัน</span></div>
        <div class="row"><span>ค่าแรงรวม</span><span>฿${(p.days*emp.daily_wage)?.toLocaleString()}</span></div>
        <div class="row"><span>OT</span><span class="green">+ ฿${p.ot.toLocaleString()}</span></div>
        <div class="row"><span>เบิกล่วงหน้า</span><span class="red">- ฿${p.adv.toLocaleString()}</span></div>
        <div class="row total"><span>รับสุทธิ</span><span class="green">฿${p.total.toLocaleString()}</span></div>
        <div class="footer">พิมพ์เมื่อ ${new Date().toLocaleString("th-TH")} · มนทชัย รีไซเคิล HR System</div>
      </div>
      <script>window.onload=()=>{window.print();}</script>
      </body></html>
    `);
    win.document.close();
  };

  return (
    <div>
      <div style={{ marginBottom: 22 }}><h1 style={{ color:C.text,fontSize:24,fontWeight:800,margin:0 }}>เงินเดือน</h1><div style={{ color:C.textMuted,fontSize:12,marginTop:3 }}>รอบ {period}</div></div>
      <div style={{ display:"grid",gridTemplateColumns:"repeat(auto-fill,minmax(220px,1fr))",gap:12 }}>
        {employees.map(emp => { const p=calc(emp); return (
          <Card key={emp.emp_id} onClick={()=>setSel({emp,...p})} style={{padding:16}}>
            <div style={{ display:"flex",alignItems:"center",gap:12,marginBottom:12 }}>
              <Avatar name={emp.full_name} size={38} photo={emp.photo} />
              <div><div style={{ color:C.text,fontWeight:700,fontSize:13 }}>{emp.full_name}</div><div style={{ color:C.textMuted,fontSize:11 }}>{emp.position}</div></div>
            </div>
            <Divider />
            <div style={{ display:"flex",justifyContent:"space-between",alignItems:"flex-end",marginTop:12 }}>
              <div><div style={{ color:C.textMuted,fontSize:10,marginBottom:2 }}>รับสุทธิ</div><div style={{ color:C.accent,fontWeight:800,fontSize:20 }}>฿{p.total.toLocaleString()}</div></div>
              <div style={{ textAlign:"right" }}><div style={{ color:C.textMuted,fontSize:10 }}>{p.days} วัน</div><div style={{ color:C.textSub,fontSize:11 }}>฿{emp.daily_wage}/วัน</div></div>
            </div>
          </Card>
        );})}
      </div>
      {sel && (
        <div style={{ position:"fixed",inset:0,background:"#000c",backdropFilter:"blur(4px)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:300,padding:20 }} onClick={()=>setSel(null)}>
          <div style={{ background:C.surface,border:`1px solid ${C.borderLight}`,borderRadius:16,padding:26,width:"100%",maxWidth:400 }} onClick={e=>e.stopPropagation()}>
            <div style={{ display:"flex",alignItems:"center",gap:14,marginBottom:20,padding:"14px 16px",background:C.accentBg,borderRadius:10,border:`1px solid ${C.accent}20` }}>
              <Avatar name={sel.emp.full_name} size={46} photo={sel.emp.photo} />
              <div><div style={{ color:C.text,fontWeight:700,fontSize:16 }}>{sel.emp.full_name}</div><div style={{ color:C.textSub,fontSize:12 }}>รอบ {period}</div></div>
            </div>
            {[["วันทำงาน",`${sel.days} วัน`,C.text],["ค่าแรง/วัน",`฿${sel.emp.daily_wage?.toLocaleString()}`,C.text],["ค่าแรงรวม",`฿${(sel.days*sel.emp.daily_wage)?.toLocaleString()}`,C.text],["OT",`+ ฿${sel.ot.toLocaleString()}`,C.accent],["เบิกล่วงหน้า",`- ฿${sel.adv.toLocaleString()}`,C.danger]].map(([k,v,col])=>(
              <div key={k} style={{ display:"flex",justifyContent:"space-between",padding:"10px 0",borderBottom:`1px solid ${C.border}` }}>
                <span style={{ color:C.textSub,fontSize:13 }}>{k}</span><span style={{ color:col,fontSize:13,fontFamily:"monospace",fontWeight:600 }}>{v}</span>
              </div>
            ))}
            <div style={{ display:"flex",justifyContent:"space-between",alignItems:"center",padding:"14px 0 16px" }}>
              <span style={{ color:C.text,fontWeight:700 }}>รับสุทธิ</span>
              <span style={{ color:C.accent,fontWeight:800,fontSize:26 }}>฿{sel.total.toLocaleString()}</span>
            </div>
            <button onClick={() => printSlip(sel.emp, sel)} style={{ width:"100%", padding:"13px", borderRadius:10, border:"none", background:C.accent, color:"#000", fontWeight:800, fontSize:14, fontFamily:"inherit", cursor:"pointer", display:"flex", alignItems:"center", justifyContent:"center", gap:8 }}>
              📄 พิมพ์ / ดาวน์โหลด PDF
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── APP ─────────────────────────────────────────────────────
const NAV = [
  { id: "dashboard", label: "ภาพรวม",   icon: "▣" },
  { id: "employees", label: "พนักงาน",   icon: "◎" },
  { id: "leave",     label: "การลา",     icon: "◷", badge: 2 },
  { id: "payroll",   label: "เงินเดือน", icon: "◈" },
  { id: "log",       label: "Log ระบบ",  icon: "☰" },
];

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [employees, setEmployees] = useState(initEmployees);
  const [logs, setLogs] = useState(initLogs);
  const [detailEmp, setDetailEmp] = useState(null);

  const addLog = (action, target, detail) => {
    setLogs(prev => [{ id: Date.now(), ts: nowStr(), user: "จ๊อด", action, target, detail }, ...prev]);
  };

  return (
    <div style={{ minHeight: "100vh", background: C.bg, color: C.text, fontFamily: "'Sarabun', sans-serif", display: "flex" }}>
      <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;500;600;700;800&display=swap" rel="stylesheet" />

      {/* Sidebar */}
      <div style={{ width: 210, minHeight: "100vh", background: C.surface, borderRight: `1px solid ${C.border}`, display: "flex", flexDirection: "column", flexShrink: 0, position: "sticky", top: 0, height: "100vh" }}>
        <div style={{ padding: "20px 16px 18px", borderBottom: `1px solid ${C.border}` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 32, height: 32, borderRadius: 8, background: C.accent, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16 }}>♻</div>
            <div><div style={{ color: C.text, fontWeight: 800, fontSize: 14 }}>มนทชัย</div><div style={{ color: C.textMuted, fontSize: 9, letterSpacing: "0.1em", textTransform: "uppercase" }}>Recycle HR</div></div>
          </div>
        </div>
        <nav style={{ flex: 1, padding: "12px 8px" }}>
          {NAV.map(n => {
            const active = page === n.id;
            return (
              <button key={n.id} onClick={() => setPage(n.id)} style={{ width: "100%", padding: "10px 12px", display: "flex", alignItems: "center", gap: 9, background: active ? C.accentBg : "transparent", border: "none", borderRadius: 8, color: active ? C.accent : C.textSub, fontSize: 13, fontWeight: active ? 700 : 400, cursor: "pointer", fontFamily: "inherit", transition: "all 0.15s", marginBottom: 2 }}
                onMouseEnter={e => { if (!active) e.currentTarget.style.background = C.surface2; }}
                onMouseLeave={e => { if (!active) e.currentTarget.style.background = "transparent"; }}
              >
                <span style={{ fontSize: 13, opacity: active ? 1 : 0.4 }}>{n.icon}</span>
                <span style={{ flex: 1, textAlign: "left" }}>{n.label}</span>
                {n.badge && <span style={{ background: C.warn, color: "#000", borderRadius: 10, padding: "1px 6px", fontSize: 10, fontWeight: 800 }}>{n.badge}</span>}
                {n.id === "log" && logs.length > 0 && <span style={{ background: C.blue + "30", color: C.blue, borderRadius: 10, padding: "1px 6px", fontSize: 10, fontWeight: 800 }}>{logs.length}</span>}
              </button>
            );
          })}
        </nav>
        <div style={{ padding: "12px 14px", borderTop: `1px solid ${C.border}` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
            <Avatar name="จ๊อด" size={28} />
            <div><div style={{ color: C.text, fontSize: 12, fontWeight: 700 }}>จ๊อด</div><div style={{ color: C.accent, fontSize: 10 }}>● Admin</div></div>
          </div>
        </div>
      </div>

      {/* Main */}
      <div style={{ flex: 1, padding: "34px 42px", overflowY: "auto" }}>
        {page === "dashboard" && <Dashboard employees={employees} onSelectEmp={emp => { setDetailEmp(emp); setPage("employees"); }} />}
        {page === "employees" && <Employees employees={employees} setEmployees={setEmployees} addLog={addLog} />}
        {page === "leave"     && <Leave employees={employees} addLog={addLog} />}
        {page === "payroll"   && <Payroll employees={employees} />}
        {page === "log"       && <LogPage logs={logs} />}
      </div>

      {detailEmp && page === "employees" && (
        <EmployeeDetail emp={detailEmp} onClose={() => setDetailEmp(null)} addLog={addLog}
          onSave={u => { setEmployees(employees.map(e => e.emp_id === u.emp_id ? u : e)); setDetailEmp(null); }} />
      )}
    </div>
  );
}
// HRFULL_V2_TEST
