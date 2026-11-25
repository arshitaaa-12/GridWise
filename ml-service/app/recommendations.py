def generate_recommendations(anomaly_row: dict, shap_summary: list) -> list[str]:
    recs = []
    hour = int(anomaly_row.get("hour", 12))
    z = float(anomaly_row.get("residual_z", 0))
    top_features = [s.lower() for s in shap_summary]

    if hour < 6 and z > 2: recs.append("Unusual nighttime spike — check appliances left on overnight.")
    if z > 3: recs.append("Consumption far above forecast — inspect HVAC, water heater, or EV charging.")
    if any("temperature" in f for f in top_features): recs.append("Temperature strongly influenced this spike — review setpoints.")
    if any("lag" in f or "rolling" in f for f in top_features): recs.append("Recent usage suggests sustained load — check for continuously running equipment.")
    if not recs: recs.append("Monitor consumption over next 24h; anomaly was not strongly explained.")
    return recs