import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/client";
import { apiErrorMessage } from "../api/client";
import { reportBySlug } from "../reportsConfig";
import { LoadingRow, Banner, EmptyState } from "../components/Kit";
import ReportRenderer from "../components/JsonView";
import { IconChart, IconRefresh } from "../components/Icons";

const PERIODS = [
  { value: "today", label: "Today" },
  { value: "week", label: "This week" },
  { value: "month", label: "This month" },
  { value: "year", label: "This year" },
  { value: "all", label: "All time" },
];

export default function ReportView() {
  const { slug } = useParams();
  const report = reportBySlug(slug);

  const [period, setPeriod] = useState("month");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  function load() {
    if (!report) return;
    setLoading(true);
    setError("");

    const params = {};
    if (report.filter === "period") params.period = period;
    if (report.filter === "date-range") {
      if (!startDate || !endDate) {
        setLoading(false);
        setError("Choose a start and end date to run this report.");
        setData(null);
        return;
      }
      params.start_date = startDate;
      params.end_date = endDate;
    }

    api
      .get(report.endpoint, { params })
      .then((res) => setData(res.data))
      .catch((err) => setError(apiErrorMessage(err, "Couldn't load this report.")))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug, period]);

  if (!report) {
    return <EmptyState icon={IconChart} title="Unknown report" body="This report doesn't exist." />;
  }

  return (
    <div>
      <div className="page-head">
        <div>
          <div className="page-eyebrow">Analytics · {report.group}</div>
          <h1 className="page-title">{report.title}</h1>
          <p className="page-desc mono" style={{ fontSize: 12 }}>{report.endpoint}</p>
        </div>
        <div className="page-actions">
          {report.filter === "period" && (
            <div className="seg">
              {PERIODS.map((p) => (
                <button key={p.value} className={period === p.value ? "active" : ""} onClick={() => setPeriod(p.value)}>
                  {p.label}
                </button>
              ))}
            </div>
          )}
          {report.filter === "date-range" && (
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
              <span className="cell-muted">to</span>
              <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
              <button className="btn btn-primary btn-sm" onClick={load}>Run</button>
            </div>
          )}
          <button className="btn btn-secondary btn-icon" onClick={load} aria-label="Refresh" title="Refresh">
            <IconRefresh width={15} height={15} />
          </button>
        </div>
      </div>

      {error && <Banner type="error">{error}</Banner>}
      {loading ? <LoadingRow label="Running report…" /> : data ? <ReportRenderer data={data} /> : null}
    </div>
  );
}
