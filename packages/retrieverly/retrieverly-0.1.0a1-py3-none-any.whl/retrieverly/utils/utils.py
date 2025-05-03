import shutil

def check_poppler_installed() -> bool:
    """Checks if poppler utilities (specifically pdftoppm) are likely installed."""
    try:
        # Try running pdftoppm -v, which should be part of poppler-utils
        result = shutil.which("pdftoppm")
        return result is not None
    except Exception:
        return False