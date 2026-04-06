import os
os.environ.setdefault("DEBUG", "true")

from fasthtml.common import serve
from my_blog import core_v5
from my_blog.admin_v1 import register_admin_routes
from my_blog.core_v5 import create_app, register_routes
import my_blog.config as config

# Initialize the app
app, state = create_app()
core_v5.state = state
register_admin_routes(app, state)
register_routes(app)

serve(port=config.PORT, reload=True)
