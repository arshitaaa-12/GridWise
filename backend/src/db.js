import pg from "pg";
import dotenv from "dotenv";
dotenv.config();

export const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL });

export async function getReadings(buildingId, limit = 720) {
  const res = await pool.query(
    `SELECT timestamp, consumption_kwh, temperature_c, humidity_pct FROM consumption_readings WHERE building_id = $1 ORDER BY timestamp DESC LIMIT $2`,
    [buildingId, limit]
  );
  return res.rows.reverse();
}

export async function saveAnomalies(buildingId, anomalies) {
  for (const a of anomalies) {
    await pool.query(
      `INSERT INTO anomalies (building_id, detected_at, actual_kwh, expected_kwh, method, severity, shap_explanation, recommendation) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)`,
      [buildingId, a.timestamp, a.consumption_kwh, a.predicted_kwh, "hybrid", Math.abs(a.residual_z) > 4 ? "high" : "medium", JSON.stringify(a.explanation), a.recommendations.join(" ")]
    );
  }
}

export async function listAnomalies(buildingId) {
  const res = await pool.query(`SELECT * FROM anomalies WHERE building_id=$1 ORDER BY detected_at DESC LIMIT 100`, [buildingId]);
  return res.rows;
}