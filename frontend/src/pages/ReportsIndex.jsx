import { Link } from "react-router-dom";
import reports, { REPORT_GROUPS } from "../reportsConfig";
import { IconArrowUpRight } from "../components/Icons";

export default function ReportsIndex() {
  return (
    <div>
      <div className="page-head">
        <div>
          <div className="page-eyebrow">Analytics</div>
          <h1 className="page-title">Reports desk</h1>
          <p className="page-desc">{reports.length} live reports pulled straight from the analytics API — pick one to run it.</p>
        </div>
      </div>

      {REPORT_GROUPS.map((group) => {
        const items = reports.filter((r) => r.group === group);
        if (items.length === 0) return null;
        return (
          <div className="panel" key={group} style={{ marginBottom: 16 }}>
            <div className="panel-head"><h3>{group}</h3><span className="pill-count">{items.length}</span></div>
            <div className="table-wrap">
              <table className="manifest">
                <tbody>
                  {items.map((r) => (
                    <tr key={r.slug}>
                      <td className="cell-strong">{r.title}</td>
                      <td className="cell-code cell-muted">{r.endpoint}</td>
                      <td style={{ textAlign: "right" }}>
                        <Link to={`/reports/${r.slug}`} className="btn btn-secondary btn-sm">
                          Open <IconArrowUpRight width={12} height={12} />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
      })}
    </div>
  );
}
