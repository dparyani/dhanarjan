"""Data processing utilities."""


def convert_sek(value):
    """Convert Swedish currency format to numeric"""
    if isinstance(value, str):
        # Remove 'kr' and whitespace
        value = value.replace(" kr", "").strip()
        # Remove all spaces
        value = value.replace(" ", "")
        # Convert to numeric
        try:
            return float(value)
        except ValueError:
            return 0.0
    return float(value) if isinstance(value, (int, float)) else 0.0
