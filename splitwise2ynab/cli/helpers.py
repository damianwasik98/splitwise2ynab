def parse_groups_str(groups_str: str) -> list[str]:
    return [g.strip() for g in groups_str.split(",")]
