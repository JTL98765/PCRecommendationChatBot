USE_CASE_SPECS = {
    "gaming":   {"min_ram_gb": 16, "graphics_type": "discrete"},
    "work":     {"min_ram_gb": 8,  "graphics_type": "integrated"},
    "study":    {"min_ram_gb": 4,  "graphics_type": "integrated"},
    "creative": {"min_ram_gb": 16, "graphics_type": "discrete"},
    "casual":   {"min_ram_gb": 4,  "graphics_type": "integrated"},
}

def get_use_case_specs(use_case: str) -> dict:
    return USE_CASE_SPECS.get(use_case, USE_CASE_SPECS["casual"])