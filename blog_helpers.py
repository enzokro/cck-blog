"""
Borrowed from: https://github.com/DrChrisLevy/DrChrisLevy.github.io/blob/main/blog.py

This is where new posts are added.
"""
import yaml
from pathlib import Path
from execnb.nbio import read_nb
from fastcore.ansi import ansi2html
from fastcore.foundation import L
from fastcore.basics import *
from fastcore.xtras import *
from fasthtml.common import *
from monsterui.all import *
from collections import defaultdict
import functools

# create the navbar
brand = A(DivLAligned(
    Img(src="/blog/static/imgs/logo.png", width=45, height=45, alt="Site Logo", cls="site-logo"),
    H3("Chris Kroenke's Site", cls="font-bolder pl-2"),
    cls="flex items-center",
), href="/")

navbar = NavBar(
    A('Blog', href="/blog", cls=("text-lg", "font-bold", "px-4", "py-2", "border-2", "rounded-md", "mr-2")),
    A('Series', href="/blog/series", cls=("text-lg", "font-bold", "px-4", "py-2", "border-2", "rounded-md", "mr-2")),
    brand=brand,
)

def main_layout(content, req):
    return Div(
        navbar,
        Container(content)
    )


# stick it all in a function

def get_blog_list():
    post_path = Path('./blog/')
    posts = post_path.ls()

    to_ignore = [
        '.DS_Store',
        '_TEMPLATE',
        'series',
        'static',
        '00_api_tests.ipynb',
        '01_update_posts.ipynb',
    ]

    posts = L(p for p in posts if p.name not in to_ignore)

    # add series here, in order you'd like them to appear
    series = [
        'llms-course',
        'guidance-expts',
    ]

    # NOTE: the /series/ path is important, we use it to group posts
    for s in series:
        series_posts = post_path / 'series' / s
        series_posts = series_posts.ls()
        series_posts = L(p for p in series_posts if p.name not in to_ignore).sorted()
        posts.extend(series_posts)

    # group the full list of articles to be rendered

    articles = []
    for p in posts:
        stem = p.stem
        name = str(p).replace('./blog/', 'blog/')
        full_name = Path(name) / stem
        post_name = f'{full_name}.ipynb'
        articles.append(post_name)

    return articles




def extract_directives(cell):
    """Extract Quarto directives (starting with # |) from a notebook cell.
    Returns a dict of directive names and their values."""
    directives = {}
    if cell.source:
        lines = cell.source.split("\n")
        for line in lines:
            if line.startswith("# |"):
                # Remove '# |' and split into directive and value
                parts = line[3:].strip().split(":")
                if len(parts) >= 2:
                    key = parts[0].strip() + ":"  # Add back the colon to match your format
                    value = ":".join(parts[1:]).strip()
                    directives[key] = [value]  # Store value in a list to match nbdev format
                else:
                    # Handle boolean directives without values
                    # directives[parts[0].strip() + ':'] = ['true']
                    # TODO
                    pass
    return directives


blog_routes = APIRouter(prefix="/blog", body_wrap=main_layout)


def get_meta_from_nb(nb):
    return yaml.safe_load(nb.cells[0].source.split("---")[1])


def render_code_output(cell, directives, wrapper=Footer):
    if not cell.outputs:
        return ""
    # TODO: {"{'warning:': ['false']}", "{'output:': ['false']}", "{'echo:': ['false']}"}
    #   HANDLE other cases/directives
    if "include:" in directives and directives["include:"][0] == "false":
        return ""
    if "output:" in directives and directives["output:"][0] == "false":
        return ""

    def render_output(out):
        otype = out["output_type"]
        if otype == "stream":
            txt = ansi2html("".join(out["text"]))
            xtra = "" if out["name"] == "stdout" else "class='stderr'"
            is_err = "<span class" in txt
            return Safe(f"<pre {xtra}><code class='{'nohighlight hljs' if is_err else ''}'>{txt}</code></pre>")
        elif otype in ("display_data", "execute_result"):
            data = out["data"]
            _g = lambda t: "".join(data[t]) if t in data else None
            if d := _g("text/html"):
                return Safe(apply_classes(d))
            if d := _g("application/javascript"):
                return Safe(f"<script>{d}</script>")
            if d := _g("text/markdown"):
                return render_md(d)
            if d := _g("text/latex"):
                return Safe(f'<div class="math">${d}$</div>')
            if d := _g("image/jpeg"):
                return Safe(f'<img src="data:image/jpeg;base64,{d}"/>')
            if d := _g("image/png"):
                return Safe(f'<img src="data:image/png;base64,{d}"/>')
            if d := _g("text/plain"):
                return Safe(f"<pre><code>{d}</code></pre>")
            if d := _g("image/svg+xml"):
                return Safe(d)
        return ""

    res = Div(*map(render_output, cell.outputs))
    if res:
        return wrapper(res)


def render_code_input(cell, directives, lang="python"):
    code = f"""```{lang}\n{cell.source}\n```\n"""
    if "include:" in directives and directives["include:"][0] == "false":
        return ""
    if "echo:" in directives and directives["echo:"][0] == "false":
        return ""
    if "code-fold:" in directives and directives["code-fold:"][0] == "true":
        return Details(Summary("See Code"), render_md(code))
    return render_md(code)


def remove_directives(cell):
    "Remove #| directives from start of cell"
    lines = cell.source.split("\n")
    while lines and lines[0].startswith("# |"):
        lines.pop(0)
    cell.source = "\n".join(lines)


def render_nb(nb):
    "Render a notebook as a list of html elements"
    res = []
    meta = get_meta_from_nb(nb)
    res.append(Div(H1(meta["title"]), Subtitle(meta.get("subtitle", "")), cls="my-9"))
    for cell in nb.cells[1:]:
        if cell["cell_type"] == "code":
            directives = extract_directives(cell)
            remove_directives(cell)
            _output = render_code_output(cell, directives)
            res.append(render_code_input(cell, directives))
            res.append(Card(_output, cls='mb-8') if _output else "")
        elif cell["cell_type"] == "markdown":
            res.append(render_md(cell.source))
    return res


def get_meta_from_md(fpath: str):
    with open(fpath, "r") as f:
        content = f.read()
    # Split on '---' and check if we have frontmatter
    parts = content.split("---")
    if len(parts) >= 3:
        # The frontmatter is the second part (index 1)
        meta = yaml.safe_load(parts[1])
        # The markdown content is the third part (index 2)
        markdown_content = parts[2].strip()
        return meta, markdown_content
    return {}, ""

# Efficient metadata caching
@functools.lru_cache(maxsize=1)
def get_all_post_metadata():
    """Cache and retrieve metadata for all blog posts."""
    fpaths = get_blog_list() #Path("blog_list.txt").read_text().splitlines()
    metas = []
    
    for fpath in fpaths:
        try:
            folder = fpath.split("/")[1] if "/" in fpath else ""
            if fpath.endswith(".md"):
                _meta, _ = get_meta_from_md(fpath)
            else:
                _meta = get_meta_from_nb(read_nb(fpath))
                
            _meta["fpath"] = fpath
            _meta["folder"] = folder
            _meta["image"] = f'../blog/static/imgs/{_meta.get("image", "")}'
            
            # Determine if post is part of a series based on path
            _meta["is_series"] = "/series/" in fpath
            
            # Extract series name from path if it's a series post
            if _meta["is_series"]:
                parts = fpath.split("/")
                if len(parts) >= 3:
                    _meta.setdefault("series", parts[2])
            
            metas.append(_meta)
        except Exception as e:
            print(f"Error processing {fpath}: {str(e)}")
            
    return metas

def group_posts_by_series():
    """Group blog posts by series with appropriate sorting."""
    metas = get_all_post_metadata()
    series_groups = defaultdict(list)
    
    # Group posts by series
    for meta in metas:
        if meta.get("is_series"):
            series_name = meta.get("series")
            if series_name:
                series_groups[series_name].append(meta)
    
    # Sort posts within each series by order and date
    for series, posts in series_groups.items():
        posts.sort(key=lambda x: (
            x.get("series_order", float('inf')),  # Primary sort by series_order
            x.get("date", "")                      # Secondary sort by date
        ))
    
    return series_groups

def create_series_navigation(current_meta, current_fpath):
    """Create navigation for series posts."""
    if not current_meta.get("is_series"):
        return None
        
    series_groups = group_posts_by_series()
    series_name = current_meta.get("series")
    
    if not series_name or series_name not in series_groups:
        return None
        
    posts = series_groups[series_name]
    current_idx = next((i for i, p in enumerate(posts) if p["fpath"] == current_fpath), -1)
    
    if current_idx == -1:
        return None
    
    # Create navigation links
    prev_link = ""
    if current_idx > 0:
        prev_post = posts[current_idx - 1]
        prev_link = A(
            "← " + prev_post["title"],
            href=blog_post.to(fpath=prev_post["fpath"]),
            cls="text-sm hover:underline"
        )
    
    next_link = ""
    if current_idx < len(posts) - 1:
        next_post = posts[current_idx + 1]
        next_link = A(
            next_post["title"] + " →",
            href=blog_post.to(fpath=next_post["fpath"]),
            cls="text-sm hover:underline text-right"
        )
    
    return Card(
        H4(f"Series: {series_name}", cls="font-bold"),
        P(f"Part {current_meta.get('series_order', current_idx + 1)} of {len(posts)}"),
        DivFullySpaced(
            prev_link,
            A("View All", href=series_detail.to(series_name=series_name), cls="text-sm"),
            next_link
        ),
        cls="mb-6 p-4 bg-gray-50"
    )

def render_series_card(series_name, posts):
    """Create a card for an entire series."""
    first_post = posts[0] if posts else None
    image = first_post.get("image", "") if first_post else ""
    
    return Card(
        image and Img(src=image, cls="w-full h-48 object-cover rounded-t-lg"),
        CardBody(
            H3(series_name, cls="font-bold text-lg mb-2"),
            P(f"{len(posts)} posts in this series", cls="text-sm text-gray-600 mb-4"),
            Ol(
                *[Li(
                    A(
                        f"{post['title']}", 
                        href=blog_post.to(fpath=post["fpath"]),
                        cls="hover:underline"
                    ),
                    cls="mb-2"
                ) for i, post in enumerate(posts)],
                cls="list-decimal pl-6"
            ),
            A(
                "View Series", 
                href=series_detail.to(series_name=series_name),
                cls=("px-4", "py-2", "mt-4", "inline-block", ButtonT.primary)
            )
        ),
        cls="shadow-md hover:shadow-lg transition-shadow"
    )

@blog_routes
def series():
    """Display all available series."""
    series_groups = group_posts_by_series()
    
    if not series_groups:
        return Title("Blog Series"), Container(
            H1("Blog Series"),
            Card(
                P("No series found. Start creating series by adding series posts to your blog."),
                cls="p-4"
            )
        )
    
    # Create series cards
    series_cards = []
    for name, posts in series_groups.items():
        series_cards.append(render_series_card(name, posts))
    
    return Title("Blog Series"), Div(
        H1("Blog Series", cls="text-center py-8"),
        Div(*series_cards, cls="max-w-4xl mx-auto px-4 space-y-8")
    )

@blog_routes
def series_detail(series_name: str):
    """Show all posts in a specific series."""
    series_groups = group_posts_by_series()
    
    if series_name not in series_groups:
        return Title("Series Not Found"), Div(
            Alert("Series not found", cls=AlertT.danger)
        )
    
    posts = series_groups[series_name]
    
    return Title(f"Series: {series_name}"), Div(
        H1(series_name, cls="text-center py-6"),
        Div(
            *[blog_card(post) for post in posts],
            cls="max-w-4xl mx-auto px-4 space-y-6"
        )
    )

@blog_routes
def index():
    fpaths = get_blog_list() #Path("blog_list.txt").read_text().splitlines()
    metas = []
    for fpath in fpaths:
        folder = fpath.split("/")[1]
        if fpath.endswith(".md"):
            _meta, _ = get_meta_from_md(fpath)
        else:
            _meta = get_meta_from_nb(read_nb(fpath))
        _meta["fpath"] = fpath
        _meta["folder"] = folder
        _meta["image"] = f'../blog/static/imgs/{_meta.get("image", "")}'
        
        # Skip series posts in the main blog index
        if "/series/" in fpath:
            continue
            
        metas.append(_meta)
    metas.sort(key=lambda x: x["date"], reverse=True)
    return Title("Chris Kroenke's Blog"), Div(
        Div(H1("Articles", cls="mb-2"), Subtitle("Tech and related writings", cls=TextT.gray + TextT.lg), cls="text-center py-8"),
        Div(Grid(*map(blog_card, metas), cols=1), cls="max-w-4xl mx-auto px-4"),
    )


@blog_routes
def blog_post(fpath: str):
    # Add series path detection based on path
    is_series = "/series/" in fpath
    series_name = None
    if is_series:
        parts = fpath.split("/")
        if len(parts) >= 3:
            series_name = parts[2]

    if fpath.endswith(".md"):
        # Handle markdown files
        meta, markdown_content = get_meta_from_md(fpath)
        content = render_md(markdown_content)
        
        # Update meta with series info
        meta["is_series"] = is_series
        if series_name:
            meta.setdefault("series", series_name)
        
        # Create series navigation if applicable
        series_nav = create_series_navigation(meta, fpath)
        
        # For markdown, return everything in a Container
        return Title(meta.get('title', 'Blog Post')), Container(
            series_nav or "",
            content
        )
    else:
        # Handle notebook files
        nb = read_nb(fpath)
        meta = get_meta_from_nb(nb)
        
        # Update meta with series info
        meta["is_series"] = is_series
        if series_name:
            meta.setdefault("series", series_name)
        
        # Create series navigation if applicable
        series_nav = create_series_navigation(meta, fpath)
        
        # For notebooks, return the title, then the navigation (if any), 
        # then all the rendered notebook elements
        if series_nav:
            return Title(meta.get('title', 'Blog Post')), series_nav, *render_nb(nb)
        else:
            return Title(meta.get('title', 'Blog Post')), *render_nb(nb)


def blog_card(meta):
    def Tags(cats):
        return DivLAligned(map(Label, cats))

    return A(
        Card(
            DivLAligned(
                Img(src=meta.get("image", ""), style="width:200px"),
                Div(cls="space-y-3 w-full")(
                    H4(meta["title"]),
                    P(meta.get("description", "")),
                    DivFullySpaced(map(Small, [meta["author"], meta["date"]]), cls=TextT.meta),
                    DivFullySpaced(
                        Tags(meta.get("tags", [])), A("Read", cls=("uk-btn", ButtonT.primary, "h-6"), href=blog_post.to(fpath=meta["fpath"]))
                    ),
                ),
            ),
            cls=CardT.hover,
        ),
        href=blog_post.to(fpath=meta["fpath"]),
    )