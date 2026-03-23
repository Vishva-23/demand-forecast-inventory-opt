import { useState, useMemo } from "react";
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart, ReferenceLine } from "recharts";

const DEMAND_RAW = [{"d":"2023-01-02","s":"WM-PRO-BLK","w":"Cork-IE","v":40},{"d":"2023-01-09","s":"WM-PRO-BLK","w":"Cork-IE","v":37},{"d":"2023-01-16","s":"WM-PRO-BLK","w":"Cork-IE","v":42},{"d":"2023-01-23","s":"WM-PRO-BLK","w":"Cork-IE","v":50},{"d":"2023-01-30","s":"WM-PRO-BLK","w":"Cork-IE","v":40},{"d":"2023-02-06","s":"WM-PRO-BLK","w":"Cork-IE","v":42},{"d":"2023-02-13","s":"WM-PRO-BLK","w":"Cork-IE","v":57},{"d":"2023-02-20","s":"WM-PRO-BLK","w":"Cork-IE","v":53},{"d":"2023-02-27","s":"WM-PRO-BLK","w":"Cork-IE","v":46},{"d":"2023-03-06","s":"WM-PRO-BLK","w":"Cork-IE","v":56},{"d":"2023-03-13","s":"WM-PRO-BLK","w":"Cork-IE","v":50},{"d":"2023-03-20","s":"WM-PRO-BLK","w":"Cork-IE","v":52},{"d":"2023-03-27","s":"WM-PRO-BLK","w":"Cork-IE","v":59},{"d":"2023-04-03","s":"WM-PRO-BLK","w":"Cork-IE","v":44},{"d":"2023-04-10","s":"WM-PRO-BLK","w":"Cork-IE","v":46},{"d":"2023-04-17","s":"WM-PRO-BLK","w":"Cork-IE","v":56},{"d":"2023-04-24","s":"WM-PRO-BLK","w":"Cork-IE","v":53},{"d":"2023-05-01","s":"WM-PRO-BLK","w":"Cork-IE","v":65},{"d":"2023-05-08","s":"WM-PRO-BLK","w":"Cork-IE","v":55},{"d":"2023-05-15","s":"WM-PRO-BLK","w":"Cork-IE","v":51},{"d":"2023-05-22","s":"WM-PRO-BLK","w":"Cork-IE","v":79},{"d":"2023-05-29","s":"WM-PRO-BLK","w":"Cork-IE","v":62},{"d":"2023-06-05","s":"WM-PRO-BLK","w":"Cork-IE","v":65},{"d":"2023-06-12","s":"WM-PRO-BLK","w":"Cork-IE","v":52},{"d":"2023-06-19","s":"WM-PRO-BLK","w":"Cork-IE","v":60},{"d":"2023-06-26","s":"WM-PRO-BLK","w":"Cork-IE","v":66},{"d":"2023-07-03","s":"WM-PRO-BLK","w":"Cork-IE","v":55},{"d":"2023-07-10","s":"WM-PRO-BLK","w":"Cork-IE","v":70},{"d":"2023-07-17","s":"WM-PRO-BLK","w":"Cork-IE","v":61},{"d":"2023-07-24","s":"WM-PRO-BLK","w":"Cork-IE","v":64},{"d":"2023-07-31","s":"WM-PRO-BLK","w":"Cork-IE","v":61},{"d":"2023-08-07","s":"WM-PRO-BLK","w":"Cork-IE","v":89},{"d":"2023-08-14","s":"WM-PRO-BLK","w":"Cork-IE","v":67},{"d":"2023-08-21","s":"WM-PRO-BLK","w":"Cork-IE","v":57},{"d":"2023-08-28","s":"WM-PRO-BLK","w":"Cork-IE","v":75},{"d":"2023-09-04","s":"WM-PRO-BLK","w":"Cork-IE","v":55},{"d":"2023-09-11","s":"WM-PRO-BLK","w":"Cork-IE","v":67},{"d":"2023-09-18","s":"WM-PRO-BLK","w":"Cork-IE","v":47},{"d":"2023-09-25","s":"WM-PRO-BLK","w":"Cork-IE","v":51},{"d":"2023-10-02","s":"WM-PRO-BLK","w":"Cork-IE","v":62},{"d":"2023-10-09","s":"WM-PRO-BLK","w":"Cork-IE","v":65},{"d":"2023-10-16","s":"WM-PRO-BLK","w":"Cork-IE","v":57},{"d":"2023-10-23","s":"WM-PRO-BLK","w":"Cork-IE","v":52},{"d":"2023-10-30","s":"WM-PRO-BLK","w":"Cork-IE","v":49},{"d":"2023-11-06","s":"WM-PRO-BLK","w":"Cork-IE","v":39},{"d":"2023-11-13","s":"WM-PRO-BLK","w":"Cork-IE","v":41},{"d":"2023-11-20","s":"WM-PRO-BLK","w":"Cork-IE","v":41},{"d":"2023-11-27","s":"WM-PRO-BLK","w":"Cork-IE","v":49},{"d":"2023-12-04","s":"WM-PRO-BLK","w":"Cork-IE","v":43},{"d":"2023-12-11","s":"WM-PRO-BLK","w":"Cork-IE","v":30},{"d":"2023-12-18","s":"WM-PRO-BLK","w":"Cork-IE","v":41},{"d":"2023-12-25","s":"WM-PRO-BLK","w":"Cork-IE","v":36},{"d":"2024-01-01","s":"WM-PRO-BLK","w":"Cork-IE","v":35},{"d":"2024-01-08","s":"WM-PRO-BLK","w":"Cork-IE","v":43},{"d":"2024-01-15","s":"WM-PRO-BLK","w":"Cork-IE","v":47},{"d":"2024-01-22","s":"WM-PRO-BLK","w":"Cork-IE","v":48},{"d":"2024-01-29","s":"WM-PRO-BLK","w":"Cork-IE","v":38},{"d":"2024-02-05","s":"WM-PRO-BLK","w":"Cork-IE","v":43},{"d":"2024-02-12","s":"WM-PRO-BLK","w":"Cork-IE","v":50},{"d":"2024-02-19","s":"WM-PRO-BLK","w":"Cork-IE","v":58},{"d":"2024-02-26","s":"WM-PRO-BLK","w":"Cork-IE","v":48},{"d":"2024-03-04","s":"WM-PRO-BLK","w":"Cork-IE","v":53},{"d":"2024-03-11","s":"WM-PRO-BLK","w":"Cork-IE","v":48},{"d":"2024-03-18","s":"WM-PRO-BLK","w":"Cork-IE","v":49},{"d":"2024-03-25","s":"WM-PRO-BLK","w":"Cork-IE","v":68},{"d":"2024-04-01","s":"WM-PRO-BLK","w":"Cork-IE","v":75},{"d":"2024-04-08","s":"WM-PRO-BLK","w":"Cork-IE","v":62},{"d":"2024-04-15","s":"WM-PRO-BLK","w":"Cork-IE","v":74},{"d":"2024-04-22","s":"WM-PRO-BLK","w":"Cork-IE","v":68},{"d":"2024-04-29","s":"WM-PRO-BLK","w":"Cork-IE","v":59},{"d":"2024-05-06","s":"WM-PRO-BLK","w":"Cork-IE","v":70},{"d":"2024-05-13","s":"WM-PRO-BLK","w":"Cork-IE","v":84},{"d":"2024-05-20","s":"WM-PRO-BLK","w":"Cork-IE","v":66},{"d":"2024-05-22","s":"WM-PRO-BLK","w":"Cork-IE","v":79},{"d":"2024-05-27","s":"WM-PRO-BLK","w":"Cork-IE","v":85},{"d":"2024-06-03","s":"WM-PRO-BLK","w":"Cork-IE","v":45},{"d":"2024-06-10","s":"WM-PRO-BLK","w":"Cork-IE","v":76},{"d":"2024-06-17","s":"WM-PRO-BLK","w":"Cork-IE","v":69},{"d":"2024-06-24","s":"WM-PRO-BLK","w":"Cork-IE","v":65},{"d":"2024-07-01","s":"WM-PRO-BLK","w":"Cork-IE","v":70},{"d":"2024-07-08","s":"WM-PRO-BLK","w":"Cork-IE","v":51},{"d":"2024-07-15","s":"WM-PRO-BLK","w":"Cork-IE","v":67},{"d":"2024-07-22","s":"WM-PRO-BLK","w":"Cork-IE","v":74},{"d":"2024-07-29","s":"WM-PRO-BLK","w":"Cork-IE","v":88},{"d":"2024-08-05","s":"WM-PRO-BLK","w":"Cork-IE","v":65},{"d":"2024-08-12","s":"WM-PRO-BLK","w":"Cork-IE","v":62},{"d":"2024-08-19","s":"WM-PRO-BLK","w":"Cork-IE","v":65},{"d":"2024-08-26","s":"WM-PRO-BLK","w":"Cork-IE","v":80}];

const FORECAST = [
  {w:1,a:63,hw:76.1,hw_lo:63.5,hw_up:88.6,bs:77.3,bs_lo:69.1,bs_up:86.7},
  {w:2,a:72,hw:53.5,hw_lo:35.7,hw_up:71.2,bs:57.0,bs_lo:44.8,bs_up:69.0},
  {w:3,a:66,hw:58.1,hw_lo:36.4,hw_up:79.8,bs:60.9,bs_lo:45.1,bs_up:74.5},
  {w:4,a:73,hw:70.7,hw_lo:45.7,hw_up:95.8,bs:73.7,bs_lo:55.2,bs_up:91.4},
  {w:5,a:55,hw:74.3,hw_lo:46.2,hw_up:102.3,bs:74.1,bs_lo:59.1,bs_up:92.6},
  {w:6,a:56,hw:65.2,hw_lo:34.5,hw_up:96.0,bs:67.8,bs_lo:47.9,bs_up:86.5},
  {w:7,a:53,hw:59.6,hw_lo:26.4,hw_up:92.8,bs:59.5,bs_lo:38.6,bs_up:85.5},
  {w:8,a:43,hw:56.3,hw_lo:20.8,hw_up:91.7,bs:57.5,bs_lo:33.4,bs_up:78.6},
  {w:9,a:53,hw:44.9,hw_lo:7.2,hw_up:82.5,bs:49.0,bs_lo:25.2,bs_up:72.4},
  {w:10,a:50,hw:47.2,hw_lo:7.6,hw_up:86.9,bs:50.8,bs_lo:20.1,bs_up:78.3},
  {w:11,a:46,hw:47.3,hw_lo:5.7,hw_up:88.9,bs:48.3,bs_lo:20.8,bs_up:77.1},
  {w:12,a:43,hw:56.6,hw_lo:13.2,hw_up:100.1,bs:59.4,bs_lo:33.1,bs_up:87.5},
  {w:13,a:34,hw:49.8,hw_lo:4.5,hw_up:95.0,bs:56.7,bs_lo:29.5,bs_up:81.5},
  {w:14,a:39,hw:34.8,hw_lo:0,hw_up:81.7,bs:39.2,bs_lo:6.3,bs_up:73.1},
  {w:15,a:39,hw:47.6,hw_lo:0,hw_up:96.2,bs:48.9,bs_lo:19.9,bs_up:81.2},
  {w:16,a:36,hw:41.9,hw_lo:0,hw_up:92.0,bs:42.0,bs_lo:11.1,bs_up:73.2},
];

const INVENTORY = [
  {node:"Cork-IE",rq_ss:22,rq_inv:626,rq_cost:125.19,bs_ss:31,bs_inv:59,bs_cost:11.73,gsm_ss:37,gsm_inv:66,gsm_cost:13.10},
  {node:"Amsterdam-NL",rq_ss:27,rq_inv:705,rq_cost:140.93,bs_ss:38,bs_inv:74,bs_cost:14.72,gsm_ss:47,gsm_inv:82,gsm_cost:16.45},
  {node:"Shanghai-CN",rq_ss:30,rq_inv:738,rq_cost:147.63,bs_ss:42,bs_inv:80,bs_cost:16.09,gsm_ss:51,gsm_inv:90,gsm_cost:17.97},
  {node:"Tokyo-JP",rq_ss:19,rq_inv:596,rq_cost:119.16,bs_ss:27,bs_inv:53,bs_cost:10.51,gsm_ss:33,gsm_inv:59,gsm_cost:11.72},
  {node:"Louisville-US",rq_ss:34,rq_inv:793,rq_cost:158.50,bs_ss:48,bs_inv:92,bs_cost:18.42,gsm_ss:59,gsm_inv:103,gsm_cost:20.57},
  {node:"Toronto-CA",rq_ss:15,rq_inv:514,rq_cost:102.87,bs_ss:22,bs_inv:41,bs_cost:8.19,gsm_ss:27,gsm_inv:46,gsm_cost:9.17},
];

const TRADEOFF = [
  {sl:80,rq:123.08,bs:8.74,gsm:9.45},{sl:85,rq:123.59,bs:9.47,gsm:10.33},
  {sl:90,rq:124.24,bs:10.38,gsm:11.45},{sl:91,rq:124.39,bs:10.60,gsm:11.72},
  {sl:92,rq:124.56,bs:10.84,gsm:12.01},{sl:93,rq:124.75,bs:11.10,gsm:12.33},
  {sl:94,rq:124.95,bs:11.39,gsm:12.69},{sl:95,rq:125.19,bs:11.73,gsm:13.10},
  {sl:96,rq:125.47,bs:12.12,gsm:13.58},{sl:97,rq:125.81,bs:12.60,gsm:14.17},
  {sl:98,rq:126.26,bs:13.24,gsm:14.96},{sl:99,rq:126.98,bs:14.26,gsm:16.20},
];

const tabs = ["Demand history", "Forecast comparison", "Inventory policies", "Service vs. cost"];
const COLORS = { primary: "#534AB7", secondary: "#1D9E75", tertiary: "#D85A30", accent: "#378ADD", muted: "#888780" };

function MetricCard({ label, value, sub }) {
  return (
    <div style={{ background: "var(--color-background-secondary)", borderRadius: "var(--border-radius-md)", padding: "0.75rem 1rem", minWidth: 0 }}>
      <div style={{ fontSize: 12, color: "var(--color-text-secondary)", marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 500, color: "var(--color-text-primary)" }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: "var(--color-text-tertiary)", marginTop: 2 }}>{sub}</div>}
    </div>
  );
}

function CustomTooltip({ active, payload, label, formatter }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "var(--color-background-primary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: "var(--border-radius-md)", padding: "8px 12px", fontSize: 12 }}>
      <div style={{ fontWeight: 500, marginBottom: 4, color: "var(--color-text-primary)" }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color, display: "flex", gap: 8, justifyContent: "space-between" }}>
          <span>{p.name}</span>
          <span style={{ fontWeight: 500 }}>{formatter ? formatter(p.value) : Math.round(p.value)}</span>
        </div>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const [tab, setTab] = useState(0);
  const [model, setModel] = useState("hw");

  const demandChart = useMemo(() => DEMAND_RAW.map(d => ({ date: d.d.slice(5), units: d.v })), []);

  const forecastChart = useMemo(() => FORECAST.map(f => ({
    week: `W${f.w}`,
    actual: f.a,
    forecast: model === "hw" ? f.hw : f.bs,
    lower: model === "hw" ? f.hw_lo : f.bs_lo,
    upper: model === "hw" ? f.hw_up : f.bs_up,
    band: [(model === "hw" ? f.hw_lo : f.bs_lo), (model === "hw" ? f.hw_up : f.bs_up)],
  })), [model]);

  const invChart = useMemo(() => INVENTORY.map(inv => ({
    name: inv.node.split("-")[0],
    "R,Q": inv.rq_cost,
    "Base-Stock": inv.bs_cost,
    "GSM": inv.gsm_cost,
  })), []);

  return (
    <div style={{ padding: "0.5rem 0" }}>
      <div style={{ display: "flex", gap: 6, marginBottom: "1.5rem", flexWrap: "wrap" }}>
        {tabs.map((t, i) => (
          <button key={i} onClick={() => setTab(i)} style={{
            padding: "6px 14px", fontSize: 13, borderRadius: "var(--border-radius-md)", cursor: "pointer",
            background: tab === i ? "var(--color-text-primary)" : "transparent",
            color: tab === i ? "var(--color-background-primary)" : "var(--color-text-secondary)",
            border: tab === i ? "none" : "0.5px solid var(--color-border-tertiary)",
            fontWeight: tab === i ? 500 : 400, transition: "all 0.15s",
          }}>{t}</button>
        ))}
      </div>

      {tab === 0 && (
        <div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: 10, marginBottom: "1.5rem" }}>
            <MetricCard label="SKU" value="WM-PRO-BLK" sub="Wireless Mouse Pro" />
            <MetricCard label="Location" value="Cork, IE" sub="EMEA region" />
            <MetricCard label="Avg weekly demand" value="56" sub="units/week" />
            <MetricCard label="Data span" value="104 wks" sub="Jan 2023 — Dec 2024" />
          </div>
          <div style={{ fontSize: 13, color: "var(--color-text-secondary)", marginBottom: 8 }}>Weekly demand (units) — Q4 seasonal dip visible in both years</div>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={demandChart}>
              <defs><linearGradient id="dg" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.15}/><stop offset="95%" stopColor={COLORS.primary} stopOpacity={0.01}/></linearGradient></defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-tertiary)" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} interval={12} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="units" stroke={COLORS.primary} fill="url(#dg)" strokeWidth={1.5} dot={false} name="Demand" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {tab === 1 && (
        <div>
          <div style={{ display: "flex", gap: 8, marginBottom: "1rem", alignItems: "center" }}>
            <span style={{ fontSize: 13, color: "var(--color-text-secondary)" }}>Model:</span>
            {[["hw", "Holt-Winters"], ["bs", "Bayesian STS"]].map(([k, label]) => (
              <button key={k} onClick={() => setModel(k)} style={{
                padding: "4px 12px", fontSize: 12, borderRadius: "var(--border-radius-md)", cursor: "pointer",
                background: model === k ? COLORS.primary : "transparent",
                color: model === k ? "#fff" : "var(--color-text-secondary)",
                border: model === k ? "none" : "0.5px solid var(--color-border-tertiary)",
              }}>{label}</button>
            ))}
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 10, marginBottom: "1.5rem" }}>
            <MetricCard label="MAPE" value={model === "hw" ? "19.2%" : "19.8%"} sub="lower is better" />
            <MetricCard label="RMSE" value={model === "hw" ? "10.9" : "11.6"} sub="units" />
            <MetricCard label="P10-P90 coverage" value={model === "hw" ? "87.5%" : "81.2%"} sub="target: 80%" />
          </div>
          <div style={{ fontSize: 13, color: "var(--color-text-secondary)", marginBottom: 8 }}>
            Forecast vs. actuals — shaded band = P10–P90 prediction interval (16-week test set)
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={forecastChart}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-tertiary)" />
              <XAxis dataKey="week" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} domain={[0, 120]} />
              <Tooltip content={<CustomTooltip />} />
              <Area dataKey="band" stroke="none" fill={model === "hw" ? COLORS.primary : COLORS.secondary} fillOpacity={0.12} name="P10-P90 band" />
              <Line type="monotone" dataKey="actual" stroke={COLORS.muted} strokeWidth={2} dot={{ r: 3, fill: COLORS.muted }} name="Actual" />
              <Line type="monotone" dataKey="forecast" stroke={model === "hw" ? COLORS.primary : COLORS.secondary} strokeWidth={2} dot={{ r: 3 }} name="Forecast P50" strokeDasharray="6 3" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}

      {tab === 2 && (
        <div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 10, marginBottom: "1.5rem" }}>
            <MetricCard label="(R,Q) heuristic" value="$125/wk" sub="Cork — high EOQ inventory" />
            <MetricCard label="Base-stock" value="$11.7/wk" sub="Cork — 90.6% cheaper" />
            <MetricCard label="Multi-echelon GSM" value="$13.1/wk" sub="Cork — network-aware" />
          </div>
          <div style={{ fontSize: 13, color: "var(--color-text-secondary)", marginBottom: 8 }}>Weekly holding cost by warehouse and policy (95% service level)</div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={invChart} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-tertiary)" />
              <XAxis type="number" tick={{ fontSize: 11 }} tickFormatter={v => `$${Math.round(v)}`} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 12 }} width={70} />
              <Tooltip content={<CustomTooltip formatter={v => `$${v.toFixed(2)}`} />} />
              <Bar dataKey="Base-Stock" fill={COLORS.secondary} radius={[0, 3, 3, 0]} barSize={14} />
              <Bar dataKey="GSM" fill={COLORS.primary} radius={[0, 3, 3, 0]} barSize={14} />
            </BarChart>
          </ResponsiveContainer>
          <div style={{ fontSize: 11, color: "var(--color-text-tertiary)", marginTop: 8 }}>
            Note: (R,Q) heuristic costs $100–160/wk per warehouse (off-chart scale) due to large EOQ batch sizes
          </div>
        </div>
      )}

      {tab === 3 && (
        <div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, minmax(0, 1fr))", gap: 10, marginBottom: "1.5rem" }}>
            <MetricCard label="Optimal operating point" value="95% SL" sub="Best cost-service balance" />
            <MetricCard label="Cost jump 95% → 99%" value="+22%" sub="Base-stock: $11.73 → $14.26" />
          </div>
          <div style={{ fontSize: 13, color: "var(--color-text-secondary)", marginBottom: 8 }}>
            Holding cost vs. service level — the knee of the curve shows diminishing returns above 95%
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={TRADEOFF}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-tertiary)" />
              <XAxis dataKey="sl" tick={{ fontSize: 11 }} tickFormatter={v => `${v}%`} label={{ value: "Service level", position: "insideBottom", offset: -2, fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={v => `$${v}`} domain={[0, 20]} label={{ value: "$/week", angle: -90, position: "insideLeft", fontSize: 11 }} />
              <Tooltip content={<CustomTooltip formatter={v => `$${v.toFixed(2)}/wk`} />} />
              <ReferenceLine x={95} stroke={COLORS.muted} strokeDasharray="4 4" />
              <Line type="monotone" dataKey="bs" stroke={COLORS.secondary} strokeWidth={2.5} dot={{ r: 3 }} name="Base-stock" />
              <Line type="monotone" dataKey="gsm" stroke={COLORS.primary} strokeWidth={2.5} dot={{ r: 3 }} name="Multi-echelon GSM" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <div style={{ marginTop: "1.5rem", padding: "0.75rem 1rem", background: "var(--color-background-secondary)", borderRadius: "var(--border-radius-md)", fontSize: 12, color: "var(--color-text-secondary)" }}>
        <span style={{ fontWeight: 500, color: "var(--color-text-primary)" }}>Tech stack:</span> Python (Pandas, NumPy, SciPy) | Statistical modelling (ST6030, ST6041) | Optimisation (CS6322) | Recharts
      </div>
    </div>
  );
}
