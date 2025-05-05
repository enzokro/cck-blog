"""
Test script to validate series functionality.
Run this with: python test_series.py
"""
from pathlib import Path
from blog_helpers import group_posts_by_series, get_all_post_metadata

def test_series_detection():
    """Test if series posts are correctly identified."""
    all_posts = get_all_post_metadata()
    
    # Print all detected posts
    print("All posts:")
    for post in all_posts:
        is_series = post.get("is_series", False)
        series_name = post.get("series", "N/A")
        print(f"- {post['fpath']}: is_series={is_series}, series={series_name}")
    
    # Print series grouping
    print("\nGrouped series:")
    series_groups = group_posts_by_series()
    for series_name, posts in series_groups.items():
        print(f"\nSeries: {series_name} ({len(posts)} posts)")
        for i, post in enumerate(posts, 1):
            print(f"  {i}. {post['title']} - {post['fpath']}")

if __name__ == "__main__":
    test_series_detection() 