"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type ClusterKeyword = {
  keyword: string;
  occurrences: number;
  weight: number;
};

type ProductRow = {
  asin: string;
  image: string | null;
  price: number | null;
  cluster_keywords_present: number;
  frequency_in_cluster_results: number;
  average_position: number;
  frequency_near_konzept: number;
};

type WordFromTitle = {
  keyword: string;
  occurrences: number;
};

type ClusterResult = {
  main_keyword: string;
  cluster_keywords: ClusterKeyword[];
  all_words_from_titles: WordFromTitle[];
  product_titles: string[];
  products: ProductRow[];
  total_keyword_occurrences: number;
};

function escapeCsvField(s: string): string {
  if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ClusterResult | null>(null);

  function downloadCsv() {
    if (!data) return;
    const rows: string[] = [];
    rows.push("=== Top 30 cluster keywords (keyword,occurrences,weight_percent) ===");
    rows.push("keyword,occurrences,weight_percent");
    data.cluster_keywords.forEach((kw) => {
      rows.push(`${escapeCsvField(kw.keyword)},${kw.occurrences},${((kw.weight ?? 0) * 100).toFixed(2)}`);
    });
    rows.push("");
    rows.push("=== Product titles (from dessertgläser search pages) ===");
    rows.push("product_title");
    data.product_titles.forEach((title) => {
      rows.push(escapeCsvField(title));
    });
    const csv = rows.join("\r\n");
    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `dessertglaeser-keywords-and-titles-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  async function runAnalysis() {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      const res = await fetch(`${API_BASE}/api/cluster/run`, { method: "POST" });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `HTTP ${res.status}`);
      }
      const json: ClusterResult = await res.json();
      setData(json);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 1200, margin: "0 auto", padding: "2rem 1.5rem" }}>
      <h1 style={{ fontSize: "1.75rem", marginBottom: "0.5rem" }}>
        Amazon.de Cluster – Dessertgläser
      </h1>
      <p style={{ color: "var(--muted)", marginBottom: "1.5rem" }}>
        Thematic cluster (top 30 from titles) and product table with frequency
        next to KONZEPT brand. Data from amazon.de via Oxylabs.
      </p>

      <button
        type="button"
        onClick={runAnalysis}
        disabled={loading}
        style={{
          padding: "0.6rem 1.2rem",
          background: "var(--accent)",
          color: "var(--bg)",
          border: "none",
          borderRadius: 6,
          fontWeight: 600,
          cursor: loading ? "not-allowed" : "pointer",
          opacity: loading ? 0.7 : 1,
        }}
      >
        {loading ? "Running analysis…" : "Run cluster analysis"}
      </button>

      {error && (
        <div
          style={{
            marginTop: "1rem",
            padding: "1rem",
            background: "rgba(248,81,73,0.15)",
            border: "1px solid rgba(248,81,73,0.4)",
            borderRadius: 8,
            color: "#f85149",
          }}
        >
          {error}
        </div>
      )}

      {data && (
        <>
          <div style={{ marginTop: "1.5rem", display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            <button
              type="button"
              onClick={downloadCsv}
              style={{
                padding: "0.5rem 1rem",
                background: "var(--surface)",
                color: "var(--text)",
                border: "1px solid var(--border)",
                borderRadius: 6,
                fontWeight: 500,
                cursor: "pointer",
              }}
            >
              Download CSV (keywords + product titles)
            </button>
          </div>
          <section style={{ marginTop: "1.5rem" }}>
            <h2 style={{ fontSize: "1.25rem", marginBottom: "0.75rem" }}>
              Top 30 cluster keywords (occurrences & weight)
            </h2>
            <p style={{ color: "var(--muted)", marginBottom: "0.5rem" }}>
              Main keyword: <strong>{data.main_keyword}</strong> · Total
              occurrences: {data.total_keyword_occurrences}
            </p>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
                gap: "0.5rem",
                marginBottom: "1rem",
              }}
            >
              {data.cluster_keywords.map((kw) => (
                <div
                  key={kw.keyword}
                  style={{
                    padding: "0.5rem 0.75rem",
                    background: "var(--surface)",
                    border: "1px solid var(--border)",
                    borderRadius: 6,
                    fontSize: "0.85rem",
                  }}
                >
                  <span style={{ fontWeight: 600 }}>{kw.keyword}</span>
                  <span style={{ color: "var(--muted)", marginLeft: "0.5rem" }}>
                    {kw.occurrences} · {((kw.weight ?? 0) * 100).toFixed(2)}%
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section style={{ marginTop: "2rem" }}>
            <h2 style={{ fontSize: "1.25rem", marginBottom: "0.75rem" }}>
              Products table
            </h2>
            <div style={{ overflowX: "auto", border: "1px solid var(--border)", borderRadius: 8 }}>
              <table>
                <thead>
                  <tr>
                    <th>ASIN</th>
                    <th>Image</th>
                    <th>Price</th>
                    <th>Cluster keywords present</th>
                    <th>Frequency in cluster results</th>
                    <th>Average position</th>
                    <th>Frequency near KONZEPT</th>
                  </tr>
                </thead>
                <tbody>
                  {data.products.map((p) => (
                    <tr key={p.asin}>
                      <td>
                        <a
                          href={`https://www.amazon.de/dp/${p.asin}`}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {p.asin}
                        </a>
                      </td>
                      <td>
                        {p.image ? (
                          <img
                            src={p.image}
                            alt=""
                            width={48}
                            height={48}
                            style={{ objectFit: "contain" }}
                          />
                        ) : (
                          "—"
                        )}
                      </td>
                      <td>
                        {p.price != null
                          ? `€ ${Number(p.price).toFixed(2)}`
                          : "—"}
                      </td>
                      <td>{p.cluster_keywords_present}</td>
                      <td>{p.frequency_in_cluster_results}</td>
                      <td>{p.average_position.toFixed(2)}</td>
                      <td>{p.frequency_near_konzept}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </main>
  );
}
