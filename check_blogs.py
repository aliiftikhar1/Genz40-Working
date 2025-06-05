import json

# Load and check blog structure
with open('templates/public/blogs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

blogs = data.get('blogs', [])
print(f'Total blogs: {len(blogs)}')
print()

for blog in blogs:
    print(f"Blog {blog.get('id', 'NO_ID')}: {blog.get('title', 'NO_TITLE')}")
    print(f"  Slug: {blog.get('slug', 'NO_SLUG')}")
    print(f"  Has author: {'author' in blog}")
    print(f"  Has content: {'content' in blog}")
    print()
