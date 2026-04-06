from fasthtml.common import FastHTML, serve
from my_blog import core_v5
from my_blog.admin_v1 import (register_admin_routes, post_edit, save_post, replace_iframe, replace_strava, post, 
    load_post, edit_layout, delete_post, download_post)
from my_blog.core_v5 import *
import my_blog.config as config

# Initialize and run the app
app, state = create_app()
core_v5.state = state
register_admin_routes(app, state)
register_routes(app)  # Register all @route decorated handlers
# srv = JupyUvi(app)  # For notebook testing
serve(port=config.PORT)