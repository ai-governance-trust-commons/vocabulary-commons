"""Preserve reviewed site chrome during evidence-only projection builds."""
import re

def preserve_chrome(path, generated):
    if not path.exists():
        return generated
    existing = path.read_text()
    for tag, cls in [('header', 'site-header'), ('footer', 'site-footer')]:
        pattern = rf'<{tag} class="{cls}">[\s\S]*?</{tag}>'
        old = re.search(pattern, existing)
        if old:
            generated, count = re.subn(pattern, lambda _: old[0], generated)
            if count != 1:
                raise ValueError(f"Expected one {tag} in {path}")
    return generated
