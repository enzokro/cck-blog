from fasthtml.common import *
from monsterui.all import *
from blog_helpers import main_layout, blog_routes

# set the theme
theme = os.getenv("THEME", "slate")
theme = getattr(Theme, theme).headers(highlightjs=True)

## sets the favicon
favicon = Favicon(light_icon="/blog/static/imgs/logo.png", dark_icon="/blog/static/imgs/logo.png")

# make sure we can find our images
img_route = Mount("/blog/static/imgs", StaticFiles(directory="blog/static/imgs"))

# our custom markdown styling
md_style = Link(rel="stylesheet", href="/blog/static/styles/style.css")

# load my greeting
about_me = Path('greeting.md').readlines()

# create the app
app, rt = fast_app(
    hdrs=[theme, favicon, md_style],
    routes=[img_route],
    # live=True,
    body_wrap=main_layout,
)

# create the main route
@rt
def index():
    return Title("cck's site"), Div(
        Section(
            DivCentered(
                Img(src="blog/static/imgs/LandingPage.png", cls="rounded-full w-64 h-64 object-cover"),
                H1("Chris Kroenke"),
                cls="space-y-4 mt-12"
            ),
        ),
        Section(
            Article(render_md(about_me),
                    cls="prose mx-auto max-w-3xl"),
            cls=("mt-12")
        )
    )

# load in our blog routes
blog_routes.to_app(app)


# run the app
serve(port=8080)