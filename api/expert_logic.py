# Expert logic for selected crops

# (crop definitions would go here)


def get_crop_knowledge(crop_name):
    crop_knowledge = {
        "rice": rice_knowledge_base,
        "maize": maize_knowledge_base,
        "pigeonpeas": pigeonpeas_knowledge_base,
        "mango": mango_knowledge_base,
        "grapes": grapes_knowledge_base,
        "watermelon": watermelon_knowledge_base,
        "apple": apple_knowledge_base,
        "orange": orange_knowledge_base,
        "papaya": papaya_knowledge_base,
        "coconut": coconut_knowledge_base,
        "cotton": cotton_knowledge_base,
        "coffee": coffee_knowledge_base,
    }
    return crop_knowledge.get(crop_name.lower())


def get_crop_section(crop_name, section):
    crop = get_crop_knowledge(crop_name)
    if crop:
        return crop.get(section)
    return None


def get_crop_stages(crop_name):
    crop = get_crop_knowledge(crop_name)
    if not crop:
        return None
    stages = crop.get("growth_stages_and_management")
    if isinstance(stages, dict):
        return list(stages.values())
    elif isinstance(stages, list):
        return stages
    return None
