#!/usr/bin/env python3

def seed_categories_and_products():
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    from modular_system.database.connection import init_db, get_engine
    from sqlalchemy import text
    
    init_db()
    engine = get_engine()
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, slug FROM organizations WHERE slug = 'fs'"))
        org_row = result.fetchone()
        
        if not org_row:
            print("Organization 'fs' not found")
            return
        
        org_id, org_slug = org_row
        print(f"Using organization: {org_slug} (ID: {org_id})")
        
        categories_data = [
            {"name": "Electronics", "slug": "electronics", "description": "Electronic devices and gadgets"},
            {"name": "Clothing", "slug": "clothing", "description": "Fashion and apparel"},
            {"name": "Books", "slug": "books", "description": "Books and literature"},
            {"name": "Home & Garden", "slug": "home-garden", "description": "Home improvement and garden supplies"},
            {"name": "Sports", "slug": "sports", "description": "Sports equipment and gear"},
            {"name": "Toys", "slug": "toys", "description": "Toys and games"},
            {"name": "Beauty", "slug": "beauty", "description": "Beauty and personal care"},
            {"name": "Automotive", "slug": "automotive", "description": "Car parts and accessories"},
            {"name": "Food", "slug": "food", "description": "Food and beverages"},
            {"name": "Health", "slug": "health", "description": "Health and wellness products"}
        ]
        
        created_categories = {}
        for cat_data in categories_data:
            result = conn.execute(text("SELECT id FROM categories WHERE slug = :slug"), {'slug': cat_data['slug']})
            existing = result.fetchone()
            
            if existing:
                print(f"Category '{cat_data['name']}' already exists")
                created_categories[cat_data['slug']] = existing[0]
            else:
                result = conn.execute(text("""
                    INSERT INTO categories (organization_id, name, slug, description)
                    VALUES (:org_id, :name, :slug, :description)
                """), {
                    'org_id': org_id,
                    'name': cat_data['name'],
                    'slug': cat_data['slug'],
                    'description': cat_data['description']
                })
                conn.commit()
                created_categories[cat_data['slug']] = result.lastrowid
                print(f"Created category: {cat_data['name']}")
        
        products_data = [
            {"name": "Smartphone", "slug": "smartphone", "description": "Latest smartphone", "price": 699.99, "stock": 50, "category_slug": "electronics"},
            {"name": "Laptop", "slug": "laptop", "description": "High-performance laptop", "price": 1299.99, "stock": 30, "category_slug": "electronics"},
            {"name": "T-Shirt", "slug": "tshirt", "description": "Cotton t-shirt", "price": 19.99, "stock": 100, "category_slug": "clothing"},
            {"name": "Jeans", "slug": "jeans", "description": "Denim jeans", "price": 49.99, "stock": 75, "category_slug": "clothing"},
            {"name": "Python Book", "slug": "python-book", "description": "Learn Python programming", "price": 29.99, "stock": 25, "category_slug": "books"},
            {"name": "Novel", "slug": "novel", "description": "Bestselling novel", "price": 14.99, "stock": 40, "category_slug": "books"},
            {"name": "Lawn Mower", "slug": "lawn-mower", "description": "Electric lawn mower", "price": 249.99, "stock": 15, "category_slug": "home-garden"},
            {"name": "Garden Tools", "slug": "garden-tools", "description": "Basic garden tool set", "price": 39.99, "stock": 35, "category_slug": "home-garden"},
            {"name": "Tennis Racket", "slug": "tennis-racket", "description": "Professional tennis racket", "price": 89.99, "stock": 20, "category_slug": "sports"},
            {"name": "Yoga Mat", "slug": "yoga-mat", "description": "Non-slip yoga mat", "price": 24.99, "stock": 60, "category_slug": "sports"}
        ]
        
        for prod_data in products_data:
            result = conn.execute(text("SELECT id FROM products WHERE name = :name"), {'name': prod_data['name']})
            existing = result.fetchone()
            
            if existing:
                print(f"Product '{prod_data['name']}' already exists")
                continue
            
            category_id = created_categories.get(prod_data['category_slug'])
            if not category_id:
                print(f"Category '{prod_data['category_slug']}' not found for product '{prod_data['name']}'")
                continue
            
            result = conn.execute(text("""
                INSERT INTO products (organization_id, category_id, name, description, price, stock)
                VALUES (:org_id, :category_id, :name, :description, :price, :stock)
            """), {
                'org_id': org_id,
                'category_id': category_id,
                'name': prod_data['name'],
                'description': prod_data['description'],
                'price': int(prod_data['price'] * 100),  # Convert to cents (integer)
                'stock': prod_data['stock']
            })
            conn.commit()
            print(f"Created product: {prod_data['name']}")
    
    print("Seeding completed!")

if __name__ == "__main__":
    seed_categories_and_products()
