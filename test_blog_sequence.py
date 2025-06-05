import os
import json
import sys

# Add the project directory to Python path
sys.path.append('.')

# Simulate the blog_details logic
def test_blog_details_logic():
    json_path = os.path.join('templates', 'public', 'blogs.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        blogs = data.get('blogs', [])
    
    print("Testing blog sequence logic:")
    print("=" * 50)
    
    for blog in blogs:
        slug = blog.get('slug')
        title = blog.get('title')
        blog_id = blog.get('id')
        
        # Find current blog and its index
        current_blog_index = -1
        for i, b in enumerate(blogs):
            if b.get('slug') == slug:
                current_blog_index = i
                break
        
        # Get next 2 blogs in sequence (wrap around if at end)
        related_blogs = []
        if current_blog_index != -1 and len(blogs) > 1:
            total_blogs = len(blogs)
            
            for i in range(1, 3):  # Get next 2 blogs
                next_index = (current_blog_index + i) % total_blogs
                related_blogs.append(blogs[next_index])
        
        print(f"Blog {blog_id}: {title}")
        print(f"  Slug: {slug}")
        print(f"  Next blogs shown:")
        for related in related_blogs:
            print(f"    - Blog {related.get('id')}: {related.get('title')}")
        print()

if __name__ == "__main__":
    test_blog_details_logic()
