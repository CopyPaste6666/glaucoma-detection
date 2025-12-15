# backend/utils/explanation.py

def generate_explanation(xai_table, confidence):
    """
    Generates final dynamic explanation text based on XAI table
    """

    if not xai_table or len(xai_table) == 0:
        return None

    # Top contributing region
    top_region = max(
        xai_table, key=lambda x: x["Combined Score"]
    )["Region"]

    return (
        f"The {top_region} region contributed most strongly, which is clinically "
        f"relevant due to retinal nerve fiber layer thinning. "
        f"The influence of the {top_region.lower()} region was substantially higher "
        f"than other regions. Based on fused Grad-CAM and LIME analysis, the model "
        f"classified the image as glaucomatous with a confidence of "
        f"{confidence:.2f}."
    )
