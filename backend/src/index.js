import express from "express";
import cors from "cors";
import consumptionRoutes from "./routes/consumption.js";
import anomalyRoutes from "./routes/anomalies.js";

const app = express();
app.use(cors());
app.use(express.json());

app.get("/health", (_, res) => res.json({ status: "ok" }));
app.use("/api/consumption", consumptionRoutes);
app.use("/api/anomalies", anomalyRoutes);

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => console.log(`GridWise backend on :${PORT}`));