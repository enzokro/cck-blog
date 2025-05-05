"""
A script to run the blog application with series functionality.
Run this with: python run_test.py
"""
from fasthtml.common import *
from monsterui.all import *
import os
from pathlib import Path
from main import app

print("Blog with Series functionality - Test Run")
print("-" * 50)
print("Available routes:")
print("- Main blog: http://127.0.0.1:8000/blog")
print("- Series listing: http://127.0.0.1:8000/blog/series")
print("- Series details: http://127.0.0.1:8000/blog/series_detail?series_name=guidance-expts")
print("- Series details: http://127.0.0.1:8000/blog/series_detail?series_name=llms-course")
print("-" * 50)

# Create blog directories if they don't exist
for series_dir in ["guidance-expts", "llms-course"]:
    full_path = Path(f"blog/series/{series_dir}")
    full_path.mkdir(parents=True, exist_ok=True)

# Simulate series metadata for test posts
def init_test_posts():
    """Create example metadata for test files if they don't exist."""
    for series, posts in {
        "guidance-expts": [
            ("guidance-expts-1/guidance-expt-1.ipynb", "Guidance Experiments - Part 1", 1),
            ("guidance-expts-2/guidance-expt-2.ipynb", "Guidance Experiments - Part 2", 2),
            ("guidance-expts-3/guidance-expt-3.ipynb", "Guidance Experiments - Part 3", 3)
        ],
        "llms-course": [
            ("00_overview/overview.ipynb", "LLMs Course - Overview", 1),
            ("01_env/environment.ipynb", "LLMs Course - Environment Setup", 2),
            ("02_nbdev/nbdev.ipynb", "LLMs Course - NBDev Integration", 3)
        ]
    }.items():
        for post_path, title, order in posts:
            full_path = Path(f"blog/series/{series}/{post_path}")
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if not full_path.exists():
                # Create a minimal notebook structure with metadata
                notebook_content = f"""{{
    "cells": [
        {{
            "cell_type": "markdown",
            "metadata": {{}},
            "source": "---\\ntitle: \\"{title}\\"\\nauthor: \\"Chris Kroenke\\"\\ndate: \\"2023-{order:02d}-01\\"\\ndescription: \\"Part of the {series} series\\"\\ntags: [\\"python\\", \\"{series}\\"]\\nseries: \\"{series}\\"\\nseries_order: {order}\\n---\\n\\n# {title}\\n\\nThis is a sample post in the {series} series."
        }},
        {{
            "cell_type": "markdown",
            "metadata": {{}},
            "source": "## Content\\n\\nThis is some content for the {title} post.\\n\\nIt's part of the {series} series."
        }}
    ],
    "metadata": {{
        "kernelspec": {{
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        }}
    }},
    "nbformat": 4,
    "nbformat_minor": 4
}}"""
                full_path.write_text(notebook_content)
                print(f"Created test notebook: {full_path}")

# Initialize test posts
init_test_posts()

# Run the application
if __name__ == "__main__":
    serve() 