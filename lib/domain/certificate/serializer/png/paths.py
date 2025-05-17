from pathlib import Path


def get_png_template_path() -> Path:
    template = Path(__file__).parent / "templates" / "template.png"
    if not template.exists():
        raise FileNotFoundError(f"certificate png template not found at {template!s}")
    return template
