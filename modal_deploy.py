import modal

app = modal.App("cckblog")


@app.function(
    image=modal.Image.debian_slim(python_version="3.12")
    .pip_install_from_pyproject("pyproject.toml")
    .add_local_dir("blog", remote_path="/root/blog", ignore=["__pycache__"])
    .add_local_file("blog_helpers.py", remote_path="/root/blog_helpers.py")
    .add_local_file("greeting.md", remote_path="/root/greeting.md")
    .add_local_file("main.py", remote_path="/root/main.py"),
    allow_concurrent_inputs=100,  # TODO
    container_idle_timeout=3 * 60,
    secrets=[modal.Secret.from_dotenv()],
)
@modal.asgi_app()
def serve():
    from main import app

    return app