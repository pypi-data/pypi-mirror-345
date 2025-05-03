"""
Orangeqs Sphinx theme.

The theme is a customized version of `pydata-sphinx-theme`.
"""

from pathlib import Path

from orangeqs.sphinx import __version__


# For more details, see:
# https://www.sphinx-doc.org/en/master/development/theming.html#distribute-your-theme-as-a-python-package
def setup(app):
    here = Path(__file__).parent.resolve()
    # Include component templates
    app.add_html_theme("orangeqs_sphinx_theme", str(here))
    return {"version": __version__, "parallel_read_safe": True}
