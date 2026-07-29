"""### Notes regarding the blog approach

The blog posts are currently prepared using Obscidian. This means that the saved markdown is not the default mistletoe but a variant.  In particular images are handled differently.  In Obscidian the format is ![[image_path]].  There is also an option to control the size of the image using a format such as ![[image_path|250]].  This is built into Obsidian and renders ok within their app.  I have then added a justification option which is left, center, right, as follows: ![[image_path|250|right]].

In the process_upload function images are uploaded to a path using the post slug as a directory name.  The slug is generated from the post title changed to lowercase and spaces replaced by underscores, and then truncated at 60 characters.  Thus a post titled "A visit to Spain" would have a slug of "a_visit_to_spain" and the images would be places in a folder: static/image/post_images/a_visit_to_spain.

When displaying a post, the markdown is rendered as normal. After rendering a function process_obsician_images is used to generate css for the images based upon the obscidian image definition as above.  A similar approach is taken to processing strava embeddings since Strava does not support iframes. Strava embeddings are encoded as {{strava:17555511761}}, where the number is the strava ride id.

Core imports: `fastlite` for SQLite database, `fasthtml` and `monsterui` for web UI, `fasthtml_auth` for authentication, and `frontmatter` for parsing markdown with YAML metadata.

`AppState` holds all shared application state: the posts database, table references, and auth manager. Passed around instead of using globals.

Creates the three database tables: `Posts` (blog content), `Tags` (category names), and `PostTags` (many-to-many junction table linking posts to tags).

Main app factory: initializes both databases, sets up authentication with `fasthtml-auth`, configures headers and static files, and returns the app plus an `AppState` instance.

Route collector decorator. Stores routes in `_routes` list for later registration. Supports both `@route` (path from function name) and `@route('/custom/path')` syntax.

Registers all routes collected by `@route` with the given app. Call this in your `app.py` after importing the module.

Homepage intro section: returns an `Article` with welcome text and links to About and Blog pages using HTMX-enabled navigation.

`hx_attrs` returns HTMX attributes for partial page updates. `hx_link` creates an anchor that uses both regular `href` and HTMX `hx-get` for SPA-like navigation.

Navigation bar with brand logo/name on the left and page links (About, Blog) on the right. Uses flexbox for layout.

Custom X (Twitter) icon as inline SVG—UIkit doesn't include the new X logo.

`social_link` creates social media icon links with appropriate `rel` attributes for security. `footer` assembles the page footer with social icons.

Page layout wrapper. On HTMX requests, returns just the content (for partial swap). On full page loads, wraps content with navbar and footer.

Checks if a slug already exists in the database. Returns the post ID if found, `False` otherwise. Used for update-vs-insert logic.

Creates or updates a post. Generates slug from title, handles tag creation/linking in the junction table. Updates existing posts if slug matches.

Route to display a single blog post. Fetches by slug, parses the datetime, renders markdown content with `render_md`, processes Obsidian images and Strava embeds.

Homepage route: displays intro section, a divider, and the latest posts as cards.

Returns all tag names from the tags table as a list.

Fetches all tags associated with a specific post via the `post_tags` junction table.

Main post retrieval function. Optionally filters by tags and limits results. Returns dicts with parsed datetime and tag list attached.

Creates a clickable tag button. Clicking adds/removes the tag from the current filter. Selected tags are styled differently.

Builds the tag filter bar: all tag pills plus a "Clear" button to reset filters.

Small styled badge for displaying a tag name on post cards.b

Blog listing route. Parses tag filter from URL, fetches matching posts, renders tag filter + post cards. Uses HTMX OOB swap to update both filter and list on tag clicks.

Extracts the first image path from a post's markdown content for use as a thumbnail.

Renders a post summary card with title, excerpt, date, tags, and optional thumbnail. Entire card is clickable via HTMX.

Processes uploaded files. For `.md` files: parses frontmatter, rewrites image paths, saves to database. For images: saves to post-specific subfolder.

Admin upload handler (POST): processes markdown files first (to get slug), then images. Returns a results table showing success/failure for each file.

Rewrites simple image filenames like `![](image.jpg)` to full paths like `![](/static/image/post_images/{slug}/image.jpg)`. Called at upload time.

`convert_obsidian_images` converts Obsidian's `![[image.ext]]` syntax to standard markdown. `load_md_file` loads a markdown file and optionally converts image syntax.

Loads and renders the About page from a markdown file, converting Obsidian image syntax to proper paths.

Route to display the About page.

#### Develop Markdown Renderer
Note - for now strava, images and youtube embeddings will be handled by separate functions after page rendering.  At a later data this can be integrated into the EnhancedRenderer class once appropriate tokens are defined for each

#### Develop Strava iFrame embedding
In your markdown, use:
`{{strava:12345678}}`
This will be replaced with an embedded Strava activity

Returns a Strava embed div with the given activity ID. The Strava embed.js script (loaded in headers) will transform this into a full embed.

Post-processes rendered HTML to find `{{strava:ID}}` placeholders and replace them with actual Strava embed divs.

#### Process Image Embeddings from Obscidian
we can set image size, and justification within Obscidan using the nomenclature:

![['image_name'|'size(w)'|'size(h)'|'justification']]

where justification is optional and can be 'left'|'center'|'right'
and size(w) and size(h) are optional (if only one is provided it will apply to the width)

Obsidian image syntax examples:
```
![[image.jpg|300]]           - width 300px
![[image.jpg|300|right]]     - float right, text wraps
![[image.jpg|300x200|center]] - fixed size, centered
```

#### Develop iframe approach for youtube material
Note that the you tube link must be on a separate line (in Obscidian this means a blank line above and below to force a `<p>, </p>` pair of tags)
At present adding youtube playlists or time stamps is not supported

Docs: https://fromLittleAcorns.github.io/my-blogblog_v5.html.md"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_blog_v5.ipynb.

# %% auto #0
__all__ = ['yt_hdrs', 'AppState', 'create_database_tables', 'create_post_database', 'create_app', 'route', 'register_routes',
           'logout', 'intro', 'hx_attrs', 'hx_link', 'is_logged_in', 'navbar', 'x_icon', 'social_link', 'footer',
           'layout', 'slug_exists', 'get_slug', 'blogpost', 'index', 'get_tags', 'get_post_tags', 'get_posts',
           'tag_pill', 'tag_filter', 'tag_badge', 'decode_tag_str', 'sentinal', 'blog', 'get_more_posts',
           'get_post_image', 'check_if_admin', 'post_card', 'add_post', 'process_upload', 'create_poster_image',
           'create_save_poster', 'get', 'save_pending', 'load_pending', 'clear_pending', 'do_upload', 'post',
           'rewrite_image_paths', 'convert_obsidian_images', 'load_md_file', 'about_content', 'about',
           'EnhancedRenderer', 'strava_embed', 'process_strava_embeddings', 'process_komoot_embed', 'process_gallery',
           'process_obsidian_images', 'preprocess_markdown', 'process_you_tube_embed', 'process_bunny_embed',
           'process_cdn_images', 'sitemap']

# %% ../nbs/05_blog_v5.ipynb #6a381e96
from fastlite import Database
from pathlib import Path
from datetime import datetime, timedelta
import my_blog.config as config
from urllib.parse import quote, unquote
from fasthtml.common import *
from monsterui.all import *
from fasthtml_auth import AuthManager
from fasthtml.jupyter import *
import ffmpeg
import re
import frontmatter
import my_blog.config as config

# %% ../nbs/05_blog_v5.ipynb #3a049b85
@dataclass
class AppState:
    pdb: Database # for managing posts
    posts_t: Table
    tags_t: Table
    post_tags_t: Table
    auth: AuthManager
    db: Database # For managing users and authorising access

# %% ../nbs/05_blog_v5.ipynb #1b911c99
def create_database_tables(pdb: Database # database to save posts and all associated tag tables
    ): 

    class Posts:
        id: int # primary key
        title: str # post title
        slug: str # unique slug based upon title
        content: str # The post content in markdown
        created: datetime # date and time created
        updated: datetime # date and time modified
        published: bool # is post published
        excerpt: str # short summary of the post
        private: bool # post only visible to logged in users

    posts = pdb.create(Posts, pk='id', defaults={'published': False, 'private':False}, transform=True)
    posts.create_index(['slug'], unique=True, if_not_exists=True)

    class Tags:
        id: int # primary key
        name: str # unique
    
    tags = pdb.create(Tags, pk='id', transform=True)
    tags.create_index(['name'], unique=True, if_not_exists=True)

    class PostTags:
        post_id: int # foreign key > posts.id
        tag_id: int # foreign key > tags.id
    
    post_tags = pdb.create(PostTags, pk=['post_id', 'tag_id'], transform=True)

    


# %% ../nbs/05_blog_v5.ipynb #95894ac6
def create_post_database(db_path: str # path to posts database
                        )-> Database: # Creates all the required database tables if they don't already exist
    pdb = Database(db_path)
    pdb.execute("PRAGMA foreign_keys = ON")
    create_database_tables(pdb)
    return pdb

# %% ../nbs/05_blog_v5.ipynb #85b497d5
yt_hdrs = (
    Script(f"""
function loadYouTube(el) {{
    var tmpl = document.getElementById('yt-template');
    var iframe = tmpl.content.firstElementChild.cloneNode(true);
    var id = el.getAttribute('data-video-id');
    iframe.src = "https://www.youtube.com/embed/" + id + "?autoplay=1&origin={config.ORIGIN}";
    el.replaceWith(iframe);
}}
"""),
    Template(
        Iframe(
            frameborder="0",
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share",
            referrerpolicy="strict-origin-when-cross-origin",
            allowfullscreen=True,
            cls="w-full aspect-video rounded-lg my-6",
            title="YouTube video player"
            ),
            id="yt-template"
    ),
)

# %% ../nbs/05_blog_v5.ipynb #6be13b13
def create_app():
    # Create databases and apps, return these within and AppState class.
    # Once created then create the server with srv = serve()
    # Add the routes with rt = app.route
    pdb = create_post_database(config.POSTS_DB_PATH)
    posts_t = pdb.t.posts
    tags_t = pdb.t.tags
    post_tags_t = pdb.t.post_tags
    # Initialize auth database
    auth = AuthManager(
        db_path=str(config.USERS_DB_PATH),
        config={
            'allow_registration': config.ALLOW_REGISTRATION,
            'public_paths': ['/', '/about', r'/blog.*', r'/post.*', '/googleada316577537ad2b.html', '/sitemap.xml'],  # Let anybody see the site apart from the admin and auth routes
            'login_path': '/auth/login',
        }
    )
    db = auth.initialize()
    # Set db password
    admin = auth.get_user(config.ADMIN_USERNAME)
    if admin and config.ADMIN_PASSWORD: auth.user_repo.update(admin.id, password=config.ADMIN_PASSWORD, email=config.ADMIN_EMAIL)
    beforeware = auth.create_beforeware()
    hdrs = (*Theme.blue.headers(highlightjs=True), Script(src="https://unpkg.com/hyperscript.org@0.9.12"),
        Script(src="https://www.googletagmanager.com/gtag/js?id=G-DP7YB96KHH", async_=True),
        Script("window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date()); gtag('config', 'G-DP7YB96KHH');"),
        *yt_hdrs,
        Link(rel="icon", type="image/png", href="/static/image/john_pixelated.png"))
    app = FastHTML(
        before=beforeware,
        secret_key=config.SECRET_KEY,
        hdrs=hdrs,
        exts='ws'  # Enable WebSocket support
    )
    config.STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")
    auth.setup_oauth(app=app, redirect_url=config.OAUTH_REDIRECT, allow_oauth_user_create=False)
    auth.register_routes(app, include_admin=True)
    state = AppState(
        pdb=pdb,
        posts_t=posts_t,
        tags_t=tags_t,
        post_tags_t=post_tags_t,
        auth=auth,
        db=db
    )
    return app, state

# %% ../nbs/05_blog_v5.ipynb #169ca000
def create_app():
    # Create databases and apps, return these within and AppState class.
    # Once created then create the server with srv = serve()
    # Add the routes with rt = app.route
    pdb = create_post_database(config.POSTS_DB_PATH)
    posts_t = pdb.t.posts
    tags_t = pdb.t.tags
    post_tags_t = pdb.t.post_tags
    # Initialize auth database
    auth = AuthManager(
        db_path=str(config.USERS_DB_PATH),
        config={
            'allow_registration': config.ALLOW_REGISTRATION,
            'public_paths': ['/', '/about', r'/blog.*', r'/post.*', '/googleada316577537ad2b.html', '/sitemap.xml'],  # Let anybody see the site apart from the admin and auth routes
            'login_path': '/auth/login',
        }
    )
    db = auth.initialize()
    # Set db password
    admin = auth.get_user(config.ADMIN_USERNAME)
    if admin and config.ADMIN_PASSWORD: auth.user_repo.update(admin.id, password=config.ADMIN_PASSWORD, email=config.ADMIN_EMAIL)
    beforeware = auth.create_beforeware()
    hdrs = (*Theme.blue.headers(highlightjs=True), Script(src="https://unpkg.com/hyperscript.org@0.9.12"),
        Script(src="https://www.googletagmanager.com/gtag/js?id=G-DP7YB96KHH", async_=True),
        Script("window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date()); gtag('config', 'G-DP7YB96KHH');"),
        Script("""
function loadYouTube(el) {
    var tmpl = document.getElementById('yt-template');
    var iframe = tmpl.content.firstElementChild.cloneNode(true);
    var id = el.getAttribute('data-video-id');
    iframe.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&origin=" + window.location.origin;
    el.replaceWith(iframe);
}
"""),
        Template(
            Iframe(
                frameborder="0",
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share",
                referrerpolicy="strict-origin-when-cross-origin",
                allowfullscreen=True,
                cls="w-full aspect-video rounded-lg my-6",
                title="YouTube video player"
            ),
            id="yt-template"
        ),
        Link(rel="icon", type="image/png", href="/static/image/john_pixelated.png"))
    app = FastHTML(
        before=beforeware,
        secret_key=config.SECRET_KEY,
        hdrs=hdrs,
        exts='ws'  # Enable WebSocket support
    )
    config.STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")
    auth.setup_oauth(app=app, redirect_url=config.OAUTH_REDIRECT, allow_oauth_user_create=False)
    auth.register_routes(app, include_admin=True)
    state = AppState(
        pdb=pdb,
        posts_t=posts_t,
        tags_t=tags_t,
        post_tags_t=post_tags_t,
        auth=auth,
        db=db
    )
    return app, state

# %% ../nbs/05_blog_v5.ipynb #962ff0b2
# Route collection for deferred registration
_routes = []

def route(path=None):
    """Decorator to collect routes without registering them immediately.
    Use @route('/path') or @route() for function-name-based paths."""
    def decorator(f):
        _routes.append((path, f))
        return f
    if callable(path):  # @route without parens
        f, path = path, None
        _routes.append((path, f))
        return f
    return decorator

# %% ../nbs/05_blog_v5.ipynb #21d398cd
def register_routes(app):
    """Register all collected routes with the app."""
    for path, handler in _routes:
        if path:
            app.route(path)(handler)
        else:
            app.route(handler)

# %% ../nbs/05_blog_v5.ipynb #491704df
@route(f"/admin/logout")
def logout(sess):
    """ Overwrite logout route from fasthtml_auth to return users to home page after logging out
    """
    print("MY LOGOUT CALLED")
    sess.clear()
    return Response(status_code=200, headers={"HX-Redirect": "/"})


# %% ../nbs/05_blog_v5.ipynb #7e9d1570
def intro():
    return Article(
        H3("Welcome to my Blog Site", cls="text-2xl font-semibold mb-4"),
        Div(cls="text-base gap-1 text-muted-foreground leading-relaxed space-y-4")(
        P("I created this site to keep a record of things I am interested in.  As such it will largely cover motorhome trips, cycling events and routes that I have done and enjoyed, coding and software development activities I am interested in or engaged with, and technology that I think is worth looking at.  You can find out more about me on my ", hx_link("About", "/about"), " page"),

        P("This site is developed using fastHTML and the Solveit platform, both technologies developed by Jeremy Howard and ",A('Answer.ai', href='https://answer.ai', target="_blank", rel="noopener noreferrer", cls="text-primary underline"), " The desgn was originally based upon the site of ", A('Jack Hogan.', href='https://jackhogan.net/', target="_blank", rel="noopener noreferrer", cls="text-primary underline"), "but has evolved to be database driven for both users and posts, as well as to incorporate infinite scroll amongst other things"

        " See my latest blog posts below or find the full list on my ", hx_link("Blog", "/blog"), " page, where posts can be readily filtered by topic.")
        )
    )


# %% ../nbs/05_blog_v5.ipynb #e502d740
def hx_attrs(target="#main-content"): return dict(hx_target=target, hx_push_url="true", hx_swap="innerHTML show:window:top")

def hx_link(txt, href, cls="text-primary underline", target="#main-content", **kw):
    # Utility function to configure the update of the target (by default the #main-content) using hx_get. Falls back to html if not htmx
    return A(txt, href=href, hx_get=href, cls=cls, **hx_attrs(target), **kw)

# %% ../nbs/05_blog_v5.ipynb #d09ae8e2
def is_logged_in(req):
    auth_user_name = req.scope.get('session', {}).get('auth')
    return True if auth_user_name else False


# %% ../nbs/05_blog_v5.ipynb #1f69321c
def navbar(req: Request):
    # Check if logged in user
    logged_in = is_logged_in(req)
    if logged_in:
        log_link = hx_link(UkIcon("user"), "/admin/logout") 
    else:
        log_link = A(UkIcon('log-in'), href="/auth/login", cls="uk-button uk-button-default uk-button-xs")
    brand = A(Img(src="/static/image/john_pixelated.png", alt="John Richmond", cls="w-6 h-6 rounded-full"), Span("John Richmond "), href="/", hx_get="/", cls="flex items-center gap-2 text-lg font-bold", **hx_attrs())
    links = Div(hx_link("About", "/about"), hx_link("Blog", "/blog"), log_link, cls="flex gap-4 items-center")
    return Nav(Div(brand, links, cls="flex items-center gap-2 justify-between p-4"), cls="border rounded-lg shadow bg-background")

# %% ../nbs/05_blog_v5.ipynb #991ad9c7
def x_icon(): return Svg(ft_hx("path", d="M12.6.75h2.454l-5.36 6.142L16 15.25h-4.937l-3.867-5.07-4.425 5.07H.316l5.733-6.57L0 .75h5.063l3.495 4.633L12.601.75Zm-.86 13.028h1.36L4.323 2.145H2.865z"), width=20, height=20, fill="currentColor", viewBox="0 0 16 16", aria_hidden="true")



# %% ../nbs/05_blog_v5.ipynb #6c3ca569
def social_link(icon, href, **kw):
    kw = dict(rel="nofollow noindex") if k == "mail" else dict(target="_blank", rel="noopener noreferrer")
    return A(x_icon() if k == "twitter" else UkIcon(icon, width=20, height=20), href=href, cls="hover:text-primary transition-colors", target="_blank", rel="noopener noreferrer", **kw)

def social_link(k, v):
    ext = dict(rel="nofollow noindex") if k == "mail" else {} if k == "rss" else dict(target="_blank", rel="noopener noreferrer")
    return A(x_icon() if k == "twitter" else UkIcon(k, width=20, height=20), href=v, aria_label=k.title(), cls="hover:text-primary transition-colors", **ext)


def footer():
    links = dict(twitter="https://x.com/@johnWrichmond", youtube="https://youtube.com/@confusedjohn46a", github="https://github.com/fromLittleAcorns")
    icons = Div(*[social_link(k, v) for k, v in links.items()], social_link("mail", "mailto:confusedjohn46@gmail.com"), cls="flex justify-center gap-6 text-muted-foreground")
    return Footer(Divider(), icons, cls="max-w-2xl mx-auto px-6 mt-auto mb-6")

# %% ../nbs/05_blog_v5.ipynb #e31ffc1b
def layout(req, *content, htmx, title=None):
    ''' title here is used to set the browser tab label in the <head> section and will not be visible on the page.  The article title is appended into the main content and shows below the navbar
    '''
    if htmx and htmx.request: return (Title(title), *content)
    main = Main(*content, cls='w-full max-w-2xl mx-auto px-6 py-8 space-y-8', id="main-content")
    return Title(title), Div(Div(navbar(req), cls='max-w-2xl mx-auto px-4 mt-4'), main, footer(), cls="flex flex-col min-h-screen")

# %% ../nbs/05_blog_v5.ipynb #80c4cbeb
def slug_exists(slug):
    if bool(list(state.posts_t.rows_where("slug = ?", [slug], limit=1))):
        return list(state.posts_t.rows_where("slug = ?", [slug], limit=1))[0]['id']
    else:
        return False

# %% ../nbs/05_blog_v5.ipynb #954e2a1d
def get_slug(title):
    slug = title.lower().replace(" ", "-")
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')[:60]
    return slug


# %% ../nbs/05_blog_v5.ipynb #91dae216
@route('/blog/{slug}')
def blogpost(htmx, req, slug: str):
    is_admin = check_if_admin(req)
    logged_in = is_logged_in(req)
    row = state.posts_t.rows_where("slug = ?", [slug], limit=1)
    p = next((dict(r) for r in row), None)
    if not p:
        return layout(req, H2("Not Found"), P("Post not found."), title="Not Found", htmx=htmx)
    if p.get('private') and not logged_in:
        return layout(req, H2("Not Found"), P("Please login to access this post."), title="Private post", htmx=htmx)
    p['created'] = datetime.fromisoformat(p['created']) if isinstance(p['created'], str) else p['created']
    image_base = f"/static/image/post_images/{slug}"
    # Firstly create the full image paths based upon the static image path and the slug
    content = preprocess_markdown(p['content'], image_base=image_base)
    content = render_md(content, renderer=EnhancedRenderer)
    content = process_cdn_images(content)
    content = Div(content, uk_lightbox="animation: slide")
    content = process_strava_embeddings(content)
    content = process_komoot_embed(content)
    content = process_bunny_embed(content, slug)
    # content = process_you_tube_embed(content)
    admin_btns = Div(
        A("Edit", href=f'/admin/edit/{slug}', cls="uk-btn uk-btn-default uk-btn-xs"),
        # Button("Delete", hx_post=f"/admin/delete/{p['slug']}", hx_confirm="Delete this post?", 
        #    cls=["uk-btn uk-btn-default uk-btn-xs"]),
        Button("Delete", hx_post=f"/admin/delete/{slug}", hx_confirm="Delete this post?", 
            hx_swap="innerHTML", cls="uk-btn uk-btn-default uk-btn-xs"),
        A("Download", href=f"/admin/download/{p['slug']}", cls=[ButtonT.default, "uk-btn-xs"]),
        cls='flex gap-1'
    ) if is_admin else Div()
    return layout(req, H1(p['title'], cls="text-3xl font-bold mb-2"), Span(p['created'].strftime('%B %d, %Y'), cls="text-muted-foreground text-sm mb-8 block"), content, 
    admin_btns, Script(src="https://strava-embeds.com/embed.js"), title=p['title'], htmx=htmx)

# %% ../nbs/05_blog_v5.ipynb #a1c2acd2
@route
def index(req, htmx):
    logged_in = is_logged_in(req)
    posts = get_posts(n=6, logged_in=logged_in)
    items = [A(H3(p['title']), P(p['excerpt'], cls="text-muted-foreground"), Span(p['created'].strftime('%d %b %Y'), cls="text-sm text-muted-foreground"), href=f"/blog/{p['slug']}", hx_get=f"/blog/{p['slug']}", cls="block border-b pb-4 hover:bg-muted/50 transition-colors", **hx_attrs()) for p in posts]
    content = Div(*items, cls="space-y-4") if items else P("No posts yet.", cls="text-muted-foreground")
    return layout(req, (intro(), Divider(), Section(H3("Latest Posts", cls="text-xl font-semibold mb-4"), content)), title="Welcome to my Blog", htmx=htmx)

# %% ../nbs/05_blog_v5.ipynb #514f8dc1
def get_tags(tags_tbl):
    tags = [row.name for row in tags_tbl()]
    return tags


# %% ../nbs/05_blog_v5.ipynb #273bf4f9
def get_post_tags(post_id: int):
    query = """
    SELECT name FROM tags WHERE id IN (SELECT tag_id FROM post_tags WHERE post_id=?)
    """
    tag_name_dicts = state.pdb.q(query, [post_id])
    tag_names = [name['name'] for name in tag_name_dicts]
    return tag_names

# %% ../nbs/05_blog_v5.ipynb #31e79c0d
def get_posts(
        n: Union[int, None]=None, # number of posts to load
        tags: Union[List, None] = None, # list of tags
        logged_in: bool=False, # is user logged in
        offset: Union [int, None]=None # where to start to load posts once ordered
        )->list: # list of posts
    if tags:
        place_holders = ','.join('?' * len(tags))
        private_posts_query = '' if logged_in else 'AND p.private = False '
        query = f"""
            SELECT DISTINCT p.* FROM posts p
            JOIN post_tags pt ON p.id = pt.post_id
            JOIN tags t ON pt.tag_id = t.id
            WHERE t.name IN ({place_holders}) AND p.published = True {private_posts_query}
            ORDER BY p.created DESC
        """
        if n: query += f" LIMIT {n}"
        if offset: query += f" OFFSET {offset}"
        posts = state.pdb.q(query, tags)
    else:
        posts = list(state.posts_t.rows_where("published = ? AND (private = False OR ?)", [True, logged_in], 
            order_by="created DESC", limit=n, offset=offset))
        posts = [dict(r) for r in posts]

    for p in posts:
        p['created'] = datetime.fromisoformat(p['created']) if isinstance(p['created'], str) else p['created']
        p['tags'] = get_post_tags(p['id'])
    return posts

# %% ../nbs/05_blog_v5.ipynb #88bb55a3
def tag_pill(tag_name, selected_tags):
    if tag_name in selected_tags:
        new_tags = selected_tags - {tag_name}
        selected = True
    else:
        new_tags = selected_tags | {tag_name}
        selected = False
    link = f"/blog?tags={','.join(new_tags)}" if new_tags else "/blog"
    cls = [ButtonT.primary if selected else ButtonT.secondary, ButtonT.sm, "rounded-lg"]
    return Button(tag_name, cls=cls, hx_get=link, **hx_attrs("#posts-list"))

# %% ../nbs/05_blog_v5.ipynb #d34579b6
def tag_filter(selected):
    # Return a div containing all of the tags and their selection status. We also need a button to clear the current selection
    selected: set # a set containing the names of the selected tags
    tags = get_tags(state.tags_t)
    tag_pills = [tag_pill(tag_name, selected) for tag_name in tags]
    clear_btn = Button("X Clear", cls=[ButtonT.default, ButtonT.sm, "rounded-lg"], hx_get="/blog", **hx_attrs("#posts-list"))
    return Div(P("Filter: "), *tag_pills, clear_btn, cls="flex flex-wrap gap-2 items-center", id="tag-filter")

# %% ../nbs/05_blog_v5.ipynb #36362347
def tag_badge(name):
    return Span(name, cls="text-xs px-2 py-1 rounded bg-muted")

# %% ../nbs/05_blog_v5.ipynb #82972f75
def decode_tag_str(tag_str: str):
    # Decode a string containing a list of items with comma separation, needed to decode a list sent as a url parameter. 
    # Returns a set of unique items
    selected = {unquote(t.strip()) for t in (tag_str or '').split(',') if t.strip()}
    return selected

# %% ../nbs/05_blog_v5.ipynb #6ef80d65
def sentinal(
        n:int, # number of posts to load
        offset:int=None, # where to start the load
        tags: str=None # a list of active tags separated by commas
        )->Div: # Div to add to the end of the list of posts to act as a sentinal
    " Create a div to add to the end of the posts on the blog. When it becomes visible then it activates the load of more posts"
    get_str = f"/loadmore?offset={offset}&n={n}"
    if tags: 
        get_str += f"&tags={tags}"
    sentinal = Div(
        hx_get=get_str,    
        hx_trigger="intersect once",
        hx_swap="outerHTML",
        hx_target="this"
    )
    return sentinal

# %% ../nbs/05_blog_v5.ipynb #a29d4fec
@route
def blog(htmx, req, tags:str=None):
    logged_in = is_logged_in(req)
    posts_to_load = 10
    # selected is a SET of the name of the selected tags
    selected = decode_tag_str(tags)
    filtered = get_posts(n=posts_to_load, tags=selected, logged_in=logged_in)
    tag_filter_div = tag_filter(selected)
    items = [post_card(p, req) for p in filtered]
    if len(items) == posts_to_load:
        items.append(sentinal(offset=posts_to_load, n=posts_to_load, tags=tags))
    post_content = Div(*items, cls="space-y-2", id="posts-list") if items else P("No posts yet.", cls="text-muted-foreground", id="posts-list")
    if htmx and htmx.target == "posts-list":
        tag_filter_div.attrs['hx-swap-oob'] = 'true'
        return post_content, tag_filter_div
    return layout(req, H2("Blog"), tag_filter_div, Divider(cls=('my-2')), post_content, title="Blog", htmx=htmx)

# %% ../nbs/05_blog_v5.ipynb #3851743c
@route("/loadmore")
def get_more_posts(req, n: int, offset: int, tags: str=None):
    logged_in = is_logged_in(req)
    selected_tags = decode_tag_str(tags)
    posts = get_posts(n=n, tags=selected_tags, logged_in=logged_in, offset=offset)
    items = [post_card(p, req) for p in posts]
    if len(items) == n:
        new_sentinal = sentinal(offset=offset+n, n=n, tags=tags)
        return (*items, new_sentinal)
    return (*items,)



# %% ../nbs/05_blog_v5.ipynb #38248430
def get_post_image(p):
    content = p["content"]
    slug = get_slug(p['title'])
    
    # Collect all image-like matches with their positions
    matches = []
    
    # 1. Obsidian images
    for m in re.finditer(r"!\[\[([^|\]]+?)(?:\|[^\]]+)?\]\]", content):
        img_name = m.group(1)
        img_path = Path(config.POST_IMAGE_DIR) / slug / img_name
        if img_path.exists():
            matches.append((m.start(), img_path))
    
    # 2. CDN images — download thumbnail
    cdn_pattern = rf'!\[[^\]]*\]\(https://{re.escape(config.CDN)}/([^)]+)\)'
    for m in re.finditer(cdn_pattern, content):
        img_name = Path(m.group(1)).name
        img_path = Path(config.POST_IMAGE_DIR) / slug / img_name
        if not img_path.exists():
            img_path.parent.mkdir(parents=True, exist_ok=True)
            r = httpx.get(f"https://{config.CDN}/{m.group(1)}?w=300")
            if r.status_code == 200:
                img_path.write_bytes(r.content)
            else:
                continue
        matches.append((m.start(), img_path))
    
    # 3. Bunny video embeds — use poster image
    for m in re.finditer(r'\{\{bunny:([A-Za-z0-9_/-]*/)?([A-Za-z0-9_\-]+)(\.mp4|\.webm)\}\}', content):
        path = m.group(1) or ''
        file_name = m.group(2)
        path_prefix = path.replace('/', '_') if path else ''
        poster_name = f"{path_prefix}{file_name}{config.POSTER_SUFFIX}.jpg"
        poster_path = config.POSTER_DIR / slug / poster_name
        if poster_path.exists():
            matches.append((m.start(), poster_path))
    
    if matches:
        matches.sort(key=lambda x: x[0])
        return matches[0][1]
    return None

# %% ../nbs/05_blog_v5.ipynb #7f1ad1ed
def check_if_admin(req):
    sess = req.scope.get('session', {})
    auth_username = sess.get('auth')
    user = state.auth.get_user(auth_username) if auth_username else None
    check_admin = is_admin = user and user.role == 'admin'
    return check_admin

# %% ../nbs/05_blog_v5.ipynb #62ecd6cc
def post_card(p, req):
    "Post summary card with optional admin controls"
    is_admin = check_if_admin(req)
    img_url = get_post_image(p)
    slug = p['slug']
    link_attrs = dict(href=f"/blog/{slug}", hx_get=f"/blog/{slug}", **hx_attrs())
    admin_btns = Div(
        A("Edit", href=f'/admin/edit/{slug}', cls="uk-btn uk-btn-default uk-btn-xs"),
        # Button("Delete", hx_post=f"/admin/delete/{p['slug']}", hx_confirm="Delete this post?", 
        #    cls=["uk-btn uk-btn-default uk-btn-xs"]),
        Button("Delete", hx_post=f"/admin/delete/{slug}", hx_confirm="Delete this post?", 
            hx_target="#main-content", hx_swap="innerHTML", 
            cls="uk-btn uk-btn-default uk-btn-xs"),
        A("Download", href=f"/admin/download/{p['slug']}", cls=[ButtonT.default, "uk-btn-xs"]),
        cls='flex gap-1'
    ) if is_admin else Div()
    return Div(cls="flex gap-4 p-3 -mx-3 rounded-lg border-b pb-4 hover:bg-muted/50 hover:shadow-lg transition-all")(
        Div(cls="flex-1")(
            A(H3(p['title']), P(p['excerpt'], cls="text-muted-foreground"), **link_attrs),
            Div(cls='flex justify-between items-center mt-2')(
                Div(Span(p['created'].strftime('%d %b %Y'), cls="text-sm text-muted-foreground mr-2"),
                    *[tag_badge(tag) for tag in p["tags"]], cls="flex items-center gap-2 flex-wrap"),
                admin_btns)),
        A(Img(src=img_url, cls="max-w-36 h-auto object-contain rounded"), **link_attrs) if img_url else None)

# %% ../nbs/05_blog_v5.ipynb #b0f1fe99
def add_post(title, content, excerpt="", tags=None, published=True, created=None, updated=None, slug: str=None, private: bool=False):
    if not slug:
        slug = get_slug(title)
    posts = state.pdb.t.posts
    tags_tbl = state.pdb.t.tags
    post_tags = state.pdb.t.post_tags
    now = datetime.now()
    post_id = slug_exists(slug)
    create_save_poster(content, slug)
    if post_id:
        post = posts.update(dict(id=post_id, title=title, slug=slug, content=content, excerpt=excerpt,
                                 created=created or now, updated=now, published=published, private=private))
        state.pdb.execute("DELETE FROM post_tags WHERE post_id = ?", [post_id])
    else:
        post = posts.insert(dict(title=title, slug=slug, content=content, excerpt=excerpt,
                                 created=created or now, updated=updated or now, published=published, private=private))
    post_id = post['id'] if isinstance(post, dict) else post.id
    if tags:
        if isinstance(tags, str): tags = [tags]
        for tag in tags:
            existing = list(tags_tbl.rows_where("name = ?", [tag], limit=1))
            if existing: tag_id = existing[0]['id']
            else:
                result = tags_tbl.insert(dict(name=tag))
                tag_id = result['id'] if isinstance(result, dict) else result.id
            if not list(post_tags.rows_where("post_id = ? AND tag_id = ?", [post_id, tag_id])):
                post_tags.insert(dict(post_id=post_id, tag_id=tag_id))
    return post_id

# %% ../nbs/05_blog_v5.ipynb #f75481a2
def process_upload(content: bytes, filename: str, slug:str=None, overwrite: bool=False):
    file_path = Path(filename)
    if file_path.suffix == '.md':
        try:
            md_text = content.decode('utf-8')
            post = frontmatter.loads(md_text)
            title = post.metadata['title']
            tags = post.metadata['tags']
            excerpt = post.metadata['excerpt']
            created = post.metadata.get('created')
            updated = post.metadata.get('updated')
            private = post.metadata.get('private', False)
            # Get the slug from the post if it exists, if not then create a slug
            slug = post.metadata.get('slug') or get_slug(title)
            if not overwrite and slug_exists(slug):
                return 'confirm', "Post already exists. Overwrite?", slug
            try:
                if overwrite:
                    add_post(slug=slug, title=title, content=post.content, excerpt=excerpt, tags=tags, created=created,
                    updated=updated, private=private)
                else:
                    add_post(title=title, content=post.content, excerpt=excerpt, tags=tags, created=created, updated=updated, private=private)
            except Exception as e:
                print(f'Error on save attempt: {e}')
                return False, f"Unable to save post: {e}", None
            return True, "Post saved", slug
        except Exception as e:
            return False, f"Error processing md: {type(e).__name__}: {e}", None
    elif file_path.suffix in ['.jpg', '.png', '.jpeg', '.tif', '.svg']:
        path_to_save = Path(config.POST_IMAGE_DIR) / Path(slug) / file_path.name
        path_to_save.parent.mkdir(parents=True, exist_ok=True)
        path_to_save.write_bytes(content)
        return True, f"File {path_to_save.name} saved", slug
    else:
        return False, f"Unknown file type {file_path.suffix}", slug

# %% ../nbs/05_blog_v5.ipynb #88b7a955
def create_poster_image(url, path_to_save):
    # Create a function to find instances of bunny.net video in the post and if they exist then create and save a thumbnail.  
    # The thumbnail will be saved in the folder static/posters/{slug}/{name}_poster.jpg
    try:
        out, _ = (
            ffmpeg.input(url, ss=0)
            .output(str(path_to_save), vframes=1, loglevel='error')
            .run(overwrite_output=True)
        )
        return True
    except Exception as e:
        print(f"Image processing exception: {e}")
        return False

# %% ../nbs/05_blog_v5.ipynb #d2dbefaf
def create_save_poster(content: NotStr, slug: str):
    content = str(content)
    pattern = r'''
    (<p[^>]*>)?
    (\s*)?
    \{\{bunny:(?P<path>[A-Za-z0-9_/-]*/)?(?P<name>[A-Za-z0-9_]+)(?P<suffix>(\.mp4|\.webm))\}\}
    (\s*)?
    (</p>)?
    '''

    def generate_save_poster(match):
        path = match['path'] or ''
        file_name = match['name']
        suffix = match['suffix']
        
        # Build unique poster filename: folder_path_filename_poster.jpg
        path_prefix = path.replace('/', '_') if path else ''
        poster_name = f"{path_prefix}{file_name}{config.POSTER_SUFFIX}.jpg"
        
        dir_full_path = config.POSTER_DIR / slug
        dir_full_path.mkdir(exist_ok=True)
        path_to_save = dir_full_path / poster_name
        
        url = f"https://{config.CDN}/{path}{file_name}{suffix}"

        result = create_poster_image(url, path_to_save)
        if not result:
            print(f'error processing poster: {file_name}')

    content = re.sub(pattern, generate_save_poster, content, flags=re.VERBOSE + re.MULTILINE)


# %% ../nbs/05_blog_v5.ipynb #ec27541d
@route('/admin/upload')
def get(htmx):
    # Create file upload form for the post
    return Div(Div(A('Cancel', href='/', cls=f"{ButtonT.secondary} px-4 py-2"), Upload("Upload Button!", id='upload1', multiple=True), cls='flex gap-2'),
               Div(id='upload-message'),
               Form(
                UploadZone(DivCentered(Span("Upload Zone"), UkIcon("upload")), id='upload2', accept=['.md', '.jpg', '.jpeg', 'png', 'svg', 'gif'], multiple=True,
                hx_target='#upload-message', hx_trigger='change', hx_post='/admin/upload', hx_swap='innerHTML', hx_encoding="multipart/form-data"),
                cls='space-y-4')
    )

# %% ../nbs/05_blog_v5.ipynb #ffe86d0d
def save_pending(slug: str, md_name: str, md_content: bytes, images: list[tuple[str, bytes]]):
    """Save md content and images to temp storage keyed by slug.
    images is a list of (filename, bytes) tuples."""
    import pickle
    Path(f'/tmp/pending_{slug}.pkl').write_bytes(pickle.dumps({'name': md_name, 'md': md_content, 'images': images}))

# %% ../nbs/05_blog_v5.ipynb #4d043c1a
def load_pending(slug: str):
    """Returns (md_content, images) or None if not found."""
    import pickle
    p = Path(f'/tmp/pending_{slug}.pkl')
    if not p.exists(): return None
    data = pickle.loads(p.read_bytes())
    return data['name'], data['md'], data['images']

# %% ../nbs/05_blog_v5.ipynb #9fb636a4
def clear_pending(slug: str):
    Path(f'/tmp/pending_{slug}.pkl').unlink(missing_ok=True)

# %% ../nbs/05_blog_v5.ipynb #67efba69
def do_upload(md_files, img_files, slug: str=None, overwrite: bool=False):
    results = []
    for name, content in md_files:
        success, message, slug_from_title = process_upload(content, name, overwrite=overwrite)
        if not slug:
            slug = slug_from_title
        if success == 'confirm':
            save_pending(slug, name, content, img_files)
            return 'confirm', slug
        results.append((name, success, message))
    for name, content in img_files:
        success, message, _ = process_upload(content, name, slug=slug)
        results.append((name, success, message))
    header = ["Name", "Success", "Message"]
    return 'done', TableFromLists(header, [[r[0], r[1], r[2]] for r in results])

# %% ../nbs/05_blog_v5.ipynb #f5cc3377
@route('/admin/upload')
def post(upload2: list[UploadFile]):
    files = [(f.filename, f.file.read()) for f in upload2]
    md_files = [(n, c) for n, c in files if n.endswith('.md')]
    img_files = [(n, c) for n, c in files if not n.endswith('.md')]
    status, result = do_upload(md_files, img_files)
    if status == 'confirm':
        slug = result
        # return a confirmation dialog - result is the slug
        return Div(P("Post already exists. Overwrite?"),
                   Button("Yes, overwrite", hx_post=f"/admin/upload/overwrite?slug={slug}", hx_target="#upload-message", hx_swap="innerHTML"),
                   Button("Cancel", cls=ButtonT.secondary, hx_get="/admin/upload", hx_target="#upload-message", hx_swap="innerHTML"))
    return Div(H2("Upload results"), result)

# %% ../nbs/05_blog_v5.ipynb #461bf991
@route('/admin/upload/overwrite')
def post(slug: str):
    pending = load_pending(slug)
    if not pending: return Alert("No pending upload found", cls=AlertT.warning)
    md_name, md_content, img_files = pending
    status, result = do_upload([(md_name, md_content)], img_files, slug=slug, overwrite=True)
    clear_pending(slug)
    return Div(H2("Upload results"), result)

# %% ../nbs/05_blog_v5.ipynb #de66363e
def rewrite_image_paths(content: str, slug: str) -> str:
    # img_ptn = r"!\[.*?\]\((/static/image/post_images/[^)]+)\)"
    img_ptn = r"(!\[.*?\])\(([^/)]+\.(jpg|jpeg|png|gif|svg))\)"
    replacement = rf"\1(/static/image/post_images/{slug}/\2)"
    return re.sub(img_ptn, replacement, content, flags=re.IGNORECASE)

# %% ../nbs/05_blog_v5.ipynb #1ee544b2
def convert_obsidian_images(content: str, image_base: str = "/static/image/about") -> str:
    """Convert Obsidian ![[image.ext]] syntax to standard markdown ![](/path/image.ext)"""
    # pattern = r'!\[\[([^\]]+\.(jpg|jpeg|png|gif|svg))\]\]'
    pattern = r'!\[\[([^|\]\n]+\.(?:jpg|jpeg|png|gif|svg))(?:[\\|][^\]]+)?\]\]'
    replacement = rf'![]({image_base}/\1)'
    return re.sub(pattern, replacement, content, flags=re.IGNORECASE)

def load_md_file(path: str, image_base: str = None) -> str:
    """Load markdown file, optionally converting Obsidian image syntax"""
    content = Path(path).read_text()
    if image_base:
        content = convert_obsidian_images(content, image_base)
    return content

# %% ../nbs/05_blog_v5.ipynb #c59a1712
def about_content():
    md = load_md_file(config.STATIC_DIR / "content/About.md", image_base="/static/image/about")
    return render_md(md)

# %% ../nbs/05_blog_v5.ipynb #cd6f7060
@route
def about(req, htmx):
    return layout(req, about_content(),title="About Me", htmx=htmx)

# %% ../nbs/05_blog_v5.ipynb #b49fbacf
from mistletoe import Document
from monsterui.franken import FrankenRenderer

# %% ../nbs/05_blog_v5.ipynb #71f9e091
class EnhancedRenderer(FrankenRenderer):
    def _is_external(self, url):
        return url.startswith(('http://', 'https://', '//'))

    def render_link(self, token):
        target = self.escape_url(token.target)      
        title = f' title="{self.escape_html(token.title)}"' if token.title else ''
        inner = self.render_inner(token)

        # Determine if we need the new tab attributes
        extra_attrs = ' target="_blank" rel="noopener noreferrer"' if self._is_external(target) else ''

        return f'<a href="{target}"{extra_attrs}{title}>{inner}</a>'

    def render_autolink(self, token):
        target = self.escape_url(token.target)
        inner = self.render_inner(token)
        
        # Autolinks are almost always external, but we'll check anyway
        extra_attrs = ' target="_blank" rel="noopener noreferrer"' if self._is_external(target) else ''
        
        return f'<a href="{target}"{extra_attrs}>{inner}</a>'

    def render_paragraph(self, token):
        if self._suppress_ptag_stack[-1]: return self.render_inner(token)
        return f'<p class="text-lg leading-relaxed mb-6">{self.render_inner(token)}</p>'

# %% ../nbs/05_blog_v5.ipynb #ab467a70
def strava_embed(activity_id: str):
    return Div(cls="strava-embed-placeholder", data_embed_type="activity", data_embed_id=activity_id, data_style="standard")

# %% ../nbs/05_blog_v5.ipynb #ac1c56c6
def process_strava_embeddings(page: NotStr):
    page = str(page)
    # Pattern to match {{strava:ID}} possibly wrapped in <p> tags
    pattern_placeholder = r'(<p[^>]*>)?\s*\{\{strava:(\d+)\}\}\s*(</p>)?'
    
    def replace_strava(match):
        activity_id = match.group(2)
        return to_xml(strava_embed(activity_id))
    
    page = re.sub(pattern_placeholder, replace_strava, page)
    return NotStr(page)

# %% ../nbs/05_blog_v5.ipynb #c71cf180
def process_komoot_embed(page: NotStr):
    page = str(page)
    pattern = r'(<p[^>]*>)?\s*\{\{komoot:(\d+)\|([A-Za-z0-9]+)(?:\|(gallery|classic))?\}\}\s*(</p>)?'
    
    def replace_komoot(match):
        tour_id = match.group(2)
        share_token = match.group(3)
        layout = match.group(4) or 'classic'
        if layout == 'gallery':
            src = f"https://www.komoot.com/tour/{tour_id}/embed?share_token={share_token}&layout=gallery&gallery=1"
            height = "640"
        else:
            src = f"https://www.komoot.com/tour/{tour_id}/embed?share_token={share_token}&layout=classic&profile=1"
            height = "700"
        return f'<iframe src="{src}" width="100%" height="{height}" frameborder="0" scrolling="no"></iframe>'
    
    page = re.sub(pattern, replace_komoot, page)
    return NotStr(page)

# %% ../nbs/05_blog_v5.ipynb #14861dcb
def process_gallery(content: str) -> str:
    """Find {{gallery:N}}...{{/gallery}} blocks, convert markdown images to <img> tags,
    strip size hints, and wrap in grid div."""
    
    # First convert standard markdown images to <img> tags
    md_img_pattern = r'!\[(?P<alt>[^\]]*)\]\((?P<url>[^)]+)\)'
    fig_pattern = r'(<img[^>]*>)\s*\n>\s*([^\n]+)'

    def md_to_img(match):
        alt = match.group('alt')
        url = match.group('url')
        return f'<img src="{url}" alt="{alt}">'
    
    strip_hints = re.compile(
        r'(!\[\[[^\]\n]+\.(?:jpg|jpeg|png|gif|svg))(?:\|\d+)?(?:x\d+)?(?:\|(?:left|right|center))?\]\]',
        re.IGNORECASE
    )
    pattern = r'\{\{gallery:(\d+)\}\}(.*?)\{\{/gallery\}\}'

    def make_gallery(match):
        cols = match.group(1)
        inner = match.group(2).strip()
        # Strip Obsidian size/location hints
        inner = strip_hints.sub(lambda m: m.group(1) + ']]', inner)
        # Convert standard markdown images to <img> tags
        inner = re.sub(md_img_pattern, md_to_img, inner)
        # Catch captions and wrap the image in a figure then add a figcaption
        inner = re.sub(fig_pattern, lambda m: f'<figure>\n{m.group(1)}\n<figcaption style="font-size:0.85em; color:#666; text-align:center">{m.group(2).strip()}</figcaption>\n</figure>', inner)
        return f'<div class="grid grid-cols-{cols} gap-4">\n{inner}\n</div>'

    return re.sub(pattern, make_gallery, content, flags=re.DOTALL)



# %% ../nbs/05_blog_v5.ipynb #907bde85
def process_obsidian_images(content: str, image_base: str) -> str:
    pattern = r'''
        !\[\[(?P<image>[^\]\n]+\.(?:jpg|jpeg|png|gif|svg))
        (?:\|(?P<size1>\d+))?
        (?:x(?P<size2>\d+))?
        (?:\|(?P<location>left|right|center))?
        \]\]
        (?:\n>\s*(?P<caption>[^\n]+))?
    '''

    def make_element(match):
        m = match.groupdict()
        src = f"{image_base}/{m['image']}"
        loc = m.get('location')

        img_styles = []
        if m['size1']: img_styles.append(f"width: {m['size1']}px")
        if m['size2']: img_styles.append(f"height: {m['size2']}px")

        wrap_styles = []
        if loc == 'right':    wrap_styles = ['float: right', 'margin-left: 1rem']
        elif loc == 'left':   wrap_styles = ['float: left', 'margin-right: 1rem']
        elif loc == 'center': wrap_styles = ['display: block', 'margin: auto']

        # elif loc == 'center': wrap_styles = ['display: block', 'margin: auto', 'text-align: center']

        caption = m.get('caption')
        if caption:
            fig_style = "; ".join(wrap_styles) if wrap_styles else None
            img_tag = Img(src=src, style="; ".join(img_styles)) if img_styles else Img(src=src)
            return str(Figure(style=fig_style)(
                A(img_tag, href=src, data_type="image"),
                Figcaption(caption.strip(), style="font-size:0.85em; color:#666; text-align:center")
            ))

        all_styles = img_styles + wrap_styles
        img_tag = Img(src=src, style="; ".join(all_styles)) if all_styles else Img(src=src)
        return str(A(img_tag, href=src, data_type="image"))

    return re.sub(pattern, make_element, content, flags=re.MULTILINE + re.VERBOSE)

# %% ../nbs/05_blog_v5.ipynb #5befab34
def preprocess_markdown(content: str, image_base: str) -> str:
    content = process_gallery(content)
    content = process_obsidian_images(content, image_base)
    return content

# %% ../nbs/05_blog_v5.ipynb #7ccb6366
def process_you_tube_embed(page: NotStr):
        page = str(page)
        pattern_vb  = r'''
(<p[^>]*?>)? # find and capture <p> if it is there.  Allows for intermediate characters after p but only up to >
(\s*)?(<a[^>]*?>) # Find the <a and any href and class values up to the first >.  Optional
https?://(?:www\.)?(?:youtu\.be/|youtube\.com/watch\?v=)(?P<index>[A-Za-z0-9_-]{11}) # Catch the index of the youtube video
(</a>)? # Catch the terminating a tag if it exists
(</p>)? # Catch the terminating p tag if it exists
'''
        for match in re.finditer(pattern_vb, page, re.MULTILINE+re.VERBOSE):
            video_id = match['index']
            placeholder = Div(
                Img(src=f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                        cls="w-full aspect-video rounded-lg my-6"),
                cls="relative cursor-pointer",
                onclick="loadYouTube(this)",
                data_video_id=video_id  # becomes data-video-id in the HTML
                )
            placeholder = to_xml(placeholder)
            page = page.replace(match.group(0), placeholder)
        return NotStr(page)

# %% ../nbs/05_blog_v5.ipynb #aab11f90
def process_bunny_embed(page: NotStr, slug: str):
    page = str(page)
    pattern = r'''
    (<p[^>]*>)?
    (\s*)?
    \{\{bunny:(?P<path>[A-Za-z0-9_/-]*/)?(?P<name>[A-Za-z0-9_\-]+)(?P<suffix>(\.mp4|\.webm))\}\}
    (\s*)?
    (</p>)?
    '''
    
    def replace_bunny(match):
        path = match['path'] or ''
        file_name = match['name']
        suffix = match['suffix']
        video_type = suffix[1:]
        
        src = f"https://{config.CDN}/{path}{file_name}{suffix}"
        
        # Build poster path with flattened naming: folder_path_filename_poster.jpg
        path_prefix = path.replace('/', '_') if path else ''
        poster_name = f"{path_prefix}{file_name}{config.POSTER_SUFFIX}.jpg"
        poster_dir = config.PROJECT_ROOT / config.POSTER_DIR / slug
        poster_dir.mkdir(parents=True, exist_ok=True)
        poster_path = poster_dir / poster_name
        
        if not poster_path.exists():
            create_poster_image(src, poster_path)
            
        with open(poster_path, 'rb') as f:
            raw_bytes = f.read()
        poster = f"data:image/jpeg;base64,{base64.b64encode(raw_bytes).decode()}"
        
        return f'<video controls width="100%" poster="{poster}">\n  <source src="{src}" type="video/{video_type}">\n</video>'
    
    page = re.sub(pattern, replace_bunny, page, flags=re.VERBOSE + re.MULTILINE)
    return NotStr(page)


# %% ../nbs/05_blog_v5.ipynb #e3ee5ee0
def process_cdn_images(page: NotStr) -> NotStr:
    """Process <img> tags from CDN URLs.
    Wraps in <a> with clean href for lightbox, moves size params to style,
    and wraps with <figure>/<figcaption> if followed by a blockquote.
    
    Regex groups are:
    - `match.group(1)` — optional `<p>` opening tag (consume/discard)
    - `match.group(2)` — the full `<img>` tag
    - `match.group(3)` — the src URL
    - `match.group(4)` — remaining img attributes
    - `match.group(5)` — optional `</p>` closing tag (consume/discard)
    - `match.group(6)` — optional blockquote block
    - `match.group(7)` — caption text
    """
    page = str(page)
    
    # Match any img tag whose src contains the CDN domain
    pattern = r'(<p[^>]*>)?\s*(<img\s+src="(https://' + re.escape(config.CDN) + r'/[^"]*)"([^>]*)>)\s*(</p>)?\s*(<blockquote[^>]*>\s*<p[^>]*>([^<]+)</p>\s*</blockquote>)?'

    def replace_img(match):
        img_tag = match.group(2)
        src = match.group(3)
        rest = match.group(4)
        caption_block = match.group(6)
        caption_text = match.group(7)

        # Split URL and query string
        clean_url, _, query = src.partition('?')
        params = dict(p.split('=') for p in query.split('&') if '=' in p) if query else {}

        # Build styles from w/h params if present
        styles = []
        if 'w' in params: styles.append(f"width: {params['w']}px")
        if 'h' in params: styles.append(f"height: {params['h']}px")
        style_str = "; ".join(styles)

        # Merge with any existing style attribute
        if style_str:
            if 'style="' in rest:
                rest = rest.replace('style="', f'style="{style_str}; ')
            else:
                rest = f'{rest} style="{style_str}"'

        # Build the new img tag
        new_img = f'<img src="{src}"{rest}>'

        # Wrap in <a> for lightbox
        wrapped = f'<a href="{clean_url}">{new_img}</a>'

        # If there's a caption, wrap in figure
        if caption_block:
            return f'<figure>\n{wrapped}\n<figcaption style="font-size:0.85em; color:#666; text-align:center">{caption_text.strip()}</figcaption>\n</figure>'
        
        return wrapped

    page = re.sub(pattern, replace_img, page)
    return NotStr(page)


# %% ../nbs/05_blog_v5.ipynb #b47e6237
@route('/sitemap.xml')
def sitemap():
    slug_list = state.pdb.q("""SELECT p.slug FROM posts p WHERE p.private = False ORDER BY p.created""")
    slug_list = [slug['slug'] for slug in slug_list]
    base = "https://blog.therichmond4.co.uk"
    static_urls = ["/", "/about", "/blog"]
    urls = static_urls + [f"/blog/{slug}" for slug in slug_list]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += "\n".join(f"  <url><loc>{base}{u}</loc></url>" for u in urls)
    xml += "\n</urlset>"
    return Response(xml, media_type="application/xml")


