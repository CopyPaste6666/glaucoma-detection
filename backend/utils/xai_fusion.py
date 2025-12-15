# backend/utils/xai_fusion.py

def build_xai_table(gradcam, lime, region_masks):
    rows = []

    for name, mask in region_masks:
        g = (gradcam * mask).sum() / (mask.sum() + 1e-6)
        l = (lime * mask).sum() / (mask.sum() + 1e-6)
        combined = 0.6 * g + 0.4 * l

        rows.append({
            "Region": name,
            "Grad-CAM Score": round(float(g), 6),
            "LIME Score": round(float(l), 6),
            "Combined Score": round(float(combined), 6)
        })

    max_c = max(r["Combined Score"] for r in rows)

    for r in rows:
        r["Normalized Combined Score"] = round(
            r["Combined Score"] / max_c, 6
        )

    return rows
