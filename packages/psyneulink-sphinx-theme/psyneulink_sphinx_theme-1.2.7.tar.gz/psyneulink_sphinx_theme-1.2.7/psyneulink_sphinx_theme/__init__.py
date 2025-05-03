"""Pytorch Sphinx theme.

From https://github.com/shiftlab/psyneulink_sphinx_theme.

"""
from os import path

__version__ = '1.2.7'
__version_full__ = __version__


def get_html_theme_path():
    """Return list of HTML theme paths."""
    cur_dir = path.abspath(path.dirname(path.dirname(__file__)))
    return cur_dir

# See http://www.sphinx-doc.org/en/stable/theming.html#distribute-your-theme-as-a-python-package
def setup(app):
    from sphinx import version_info as sphinx_version

    app.add_html_theme('psyneulink_sphinx_theme', path.abspath(path.dirname(__file__)))

    # Below code copied from sphinx_rtd_theme
    # Since Sphinx 6, jquery isn't bundled anymore and we need to ensure that
    # the sphinxcontrib-jquery extension is enabled.
    # See: https://dev.readthedocs.io/en/latest/design/sphinx-jquery.html
    if sphinx_version >= (6, 0, 0):
        # Documentation of Sphinx guarantees that an extension is added and
        # enabled at most once.
        # See: https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx.application.Sphinx.setup_extension
        app.setup_extension("sphinxcontrib.jquery")
        # However, we need to call the extension's callback since setup_extension doesn't do it
        # See: https://github.com/sphinx-contrib/jquery/issues/23
        from sphinxcontrib.jquery import add_js_files as jquery_add_js_files
        jquery_add_js_files(app, app.config)
