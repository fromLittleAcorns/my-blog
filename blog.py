from fasthtml.common import FastHTML, serve
from my_blog import core_v5
from my_blog.core_v5 import *

# Initialize and run the app
app, state = create_app()
core_v5.state = state
register_routes(app)  # Register all @route decorated handlers
# srv = JupyUvi(app)  # For notebook testing
serve(port=8000)