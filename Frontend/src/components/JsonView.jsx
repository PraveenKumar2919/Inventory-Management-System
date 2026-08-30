// Turns an arbitrary DRF report JSON payload into readable cards/tables
// without needing one hand-built component per report endpoint.

function isPlainObject(v) {
  return v !== null && typeof v === "object" && !Array.isArray(v);
}

function prettyLabel(key) {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function prettyValue(v) {
  if (v === null || v === undefined || v === "") return "—";
  if (typeof v === "number") {
    if (!Number.isInteger(v)) return v.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    return v.toLocaleString("en-IN");
  }
  if (typeof v === "boolean") return v ? "Yes" : "No";
  return String(v);
}

function isScalar(v) {
  return v === null || ["string", "number", "boolean"].includes(typeof v);
}

// A row of objects -> auto-columned manifest table.
function ObjectTable({ rows }) {
  const columns = Array.from(
    rows.reduce((set, row) => {
      if (isPlainObject(row)) Object.keys(row).forEach((k) => set.add(k));
      return set;
    }, new Set())
  );

  if (columns.length === 0) {
    // array of scalars
    return (
      <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13 }}>
        {rows.map((r, i) => <li key={i}>{prettyValue(r)}</li>)}
      </ul>
    );
  }

  return (
    <div className="table-wrap">
      <table className="manifest">
        <thead>
          <tr>{columns.map((c) => <th key={c}>{prettyLabel(c)}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {columns.map((c) => {
                const val = row?.[c];
                const numeric = typeof val === "number";
                return (
                  <td key={c} className={numeric ? "cell-num" : ""}>
                    {isPlainObject(val) || Array.isArray(val) ? <JsonBlock data={val} depth={2} /> : prettyValue(val)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function KvGrid({ obj }) {
  const entries = Object.entries(obj).filter(([, v]) => isScalar(v));
  const complex = Object.entries(obj).filter(([, v]) => !isScalar(v));
  return (
    <>
      {entries.length > 0 && (
        <div className="kv-grid">
          {entries.map(([k, v]) => (
            <div className="kv-item" key={k}>
              <div className="kv-label">{prettyLabel(k)}</div>
              <div className="kv-value">{prettyValue(v)}</div>
            </div>
          ))}
        </div>
      )}
      {complex.map(([k, v]) => (
        <div key={k} style={{ marginTop: 14 }}>
          <div className="kv-label" style={{ marginBottom: 8 }}>{prettyLabel(k)}</div>
          <JsonBlock data={v} depth={2} />
        </div>
      ))}
    </>
  );
}

export function JsonBlock({ data }) {
  if (data === null || data === undefined) return <span className="cell-muted">—</span>;

  if (Array.isArray(data)) {
    if (data.length === 0) return <span className="cell-muted">No records.</span>;
    return <ObjectTable rows={data} />;
  }

  if (isPlainObject(data)) {
    return <KvGrid obj={data} />;
  }

  return <span>{prettyValue(data)}</span>;
}

// Top-level report renderer: scalar fields become KPI stat cards,
// object fields become titled panels, array fields become tables.
export default function ReportRenderer({ data }) {
  if (!isPlainObject(data)) return <JsonBlock data={data} />;

  const scalarEntries = Object.entries(data).filter(([, v]) => isScalar(v));
  const sectionEntries = Object.entries(data).filter(([, v]) => !isScalar(v));

  return (
    <div>
      {scalarEntries.length > 0 && (
        <div className="stat-grid">
          {scalarEntries.map(([k, v]) => (
            <div className="stat-card" key={k}>
              <div className="stat-label">{prettyLabel(k)}</div>
              <div className="stat-value">{prettyValue(v)}</div>
            </div>
          ))}
        </div>
      )}

      {sectionEntries.map(([k, v]) => (
        <div className="panel" key={k} style={{ marginBottom: 16 }}>
          <div className="panel-head">
            <h3>{prettyLabel(k)}</h3>
            {Array.isArray(v) && <span className="pill-count">{v.length} records</span>}
          </div>
          <div className={Array.isArray(v) ? "panel-body-flush" : "panel-body"}>
            <JsonBlock data={v} depth={1} />
          </div>
        </div>
      ))}
    </div>
  );
}
