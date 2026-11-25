import fs from "fs";
import { parse } from "csv-parse/sync";
import { pool } from "./src/db.js";

async function seed() {
  const records = parse(fs.readFileSync("../ml-service/data/consumption.csv", "utf-8"), { columns: true, skip_empty_lines: true });
  console.log(`Inserting ${records.length} rows...`);
  for (let i = 0; i < records.length; i += 500) {
    const chunk = records.slice(i, i + 500);
    const values = [], params = [];
    chunk.forEach((r, idx) => {
      const offset = idx * 5;
      values.push(`($${offset + 1}, $${offset + 2}, $${offset + 3}, $${offset + 4}, $${offset + 5})`);
      params.push(1, r.timestamp, parseFloat(r.consumption_kwh), parseFloat(r.temperature_c), parseFloat(r.humidity_pct));
    });
    await pool.query(`INSERT INTO consumption_readings (building_id, timestamp, consumption_kwh, temperature_c, humidity_pct) VALUES ${values.join(",")} ON CONFLICT DO NOTHING`, params);
    console.log(`Inserted ${i + chunk.length}/${records.length}`);
  }
  console.log("✅ Seed complete");
  await pool.end();
}
seed().catch(console.error);