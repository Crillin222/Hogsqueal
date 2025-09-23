import re
import resources_rc

resources_rc.qInitResources()

def parse_robot_file(file_path):
    """
    Reads a .robot file and extracts commented Feature blocks.
    Each Feature starts with '# Feature' and continues until the next Feature or end of file.

    Returns:
    - features: list of strings (each complete feature)
    - stats: dict with feature and scenario counts
    """
    features = []
    current_feature = []
    inside_feature = False

    feature_count = 0
    scenario_count = 0

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            # Detect start of a Feature
            if stripped.lower().startswith("# feature"):
                if current_feature:
                    features.append("\n".join(current_feature))
                    current_feature = []
                inside_feature = True
                feature_count += 1
                current_feature.append(stripped.lstrip("#").strip())
            elif inside_feature:
                if stripped.startswith("#"):
                    content = stripped.lstrip("#").strip()
                    current_feature.append(content)
                    if content.lower().startswith("scenario"):
                        scenario_count += 1
                elif stripped == "":
                    continue
                else:
                    continue
        # If file ends inside a Feature
        if current_feature:
            features.append("\n".join(current_feature))

    stats = {
        "features": feature_count,
        "scenarios": scenario_count
    }
    return features, stats
