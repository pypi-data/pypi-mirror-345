import datetime
import warnings

import kumoai

warnings.filterwarnings(
    'ignore',
    message="The default value for 'linkcheck_report_timeouts_as_broken'",
    category=DeprecationWarning, module='sphinx')

author = 'Kumo.AI'
project = 'kumoai'
version = kumoai.__version__
copyright = f'{datetime.datetime.now().year}, {author}'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_copybutton',
    'sphinx_autodoc_typehints',
]

html_theme = 'sphinx_book_theme'
html_logo = '../assets/kumo-logo.svg'
html_favicon = '../assets/kumo-favicon.png'
html_theme_options = {
    'navigation_depth': 2,
    'extra_footer': f'<div>Version: {kumoai.__version__}</div>'
}
templates_path = ['_templates']
autodoc_member_order = 'bysource'
autodoc_class_signature = 'separated'
copybutton_prompt_text = r'>>> |\.\.\. '
copybutton_prompt_is_regexp = True

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('http://pandas.pydata.org/pandas-docs/dev', None),
    'requests': ('https://requests.readthedocs.io/en/stable/', None),
}

doctest_global_setup = """
import os

os.environ['SNOWFLAKE_USER'] = '...'
os.environ['SNOWFLAKE_PASSWORD'] = '...'
"""


def rst_jinja_render(app, _, source):
    if hasattr(app.builder, 'templates'):
        rst_context = {'kumoai': kumoai}
        source[0] = app.builder.templates.render_string(source[0], rst_context)


def setup(app):
    app.connect('source-read', rst_jinja_render)
