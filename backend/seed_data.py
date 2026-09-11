import os
import sys

# Ensure the script can import from the backend module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models.bird import Bird
from models.category import Category

def seed_data():
    # Ensure tables exist
    create_db_and_tables()

    with Session(engine) as session:
        # 1. Create a Category
        cat_name = "Budgerigar"
        category = session.exec(select(Category).where(Category.name == cat_name)).first()
        if not category:
            category = Category(name=cat_name, description="Common pet parakeet")
            session.add(category)
            session.commit()
            session.refresh(category)

        # 2. Check if we already have the birds, to avoid unique constraint errors
        existing_bird = session.exec(select(Bird).where(Bird.ring_id == "GP-001")).first()
        if existing_bird:
            print("Seed data already exists. Skipping.")
            return

        print("Seeding multi-generational bird data...")

        # Generation 1: Grandparents
        grandpa = Bird(
            ring_id="GP-001",
            name="Apollo",
            mutation="Normal Green",
            sex="male",
            category_id=category.id,
            status="deceased"
        )
        grandma = Bird(
            ring_id="GP-002",
            name="Athena",
            mutation="Lutino",
            sex="female",
            category_id=category.id,
            status="deceased"
        )
        session.add(grandpa)
        session.add(grandma)
        session.commit()
        session.refresh(grandpa)
        session.refresh(grandma)

        # Generation 2: Parents
        father = Bird(
            ring_id="P-001",
            name="Zeus",
            mutation="Olive Green",
            sex="male",
            category_id=category.id,
            father_id=grandpa.id,
            mother_id=grandma.id,
            status="in_stock"
        )
        mother = Bird(
            ring_id="P-002",
            name="Hera",
            mutation="Albino",
            sex="female",
            category_id=category.id,
            status="in_stock"
        )
        session.add(father)
        session.add(mother)
        session.commit()
        session.refresh(father)
        session.refresh(mother)

        # Generation 3: Children
        child1 = Bird(
            ring_id="C-001",
            name="Ares",
            mutation="Normal Green",
            sex="male",
            category_id=category.id,
            father_id=father.id,
            mother_id=mother.id,
            status="in_stock"
        )
        child2 = Bird(
            ring_id="C-002",
            name="Aphrodite",
            mutation="Lutino",
            sex="female",
            category_id=category.id,
            father_id=father.id,
            mother_id=mother.id,
            status="in_stock"
        )
        session.add(child1)
        session.add(child2)
        session.commit()
        session.refresh(child1)
        session.refresh(child2)

        print(f"Seed complete!")
        print(f"Grandpa ID: {grandpa.id}, Grandma ID: {grandma.id}")
        print(f"Father ID: {father.id}, Mother ID: {mother.id}")
        print(f"Child 1 ID: {child1.id}, Child 2 ID: {child2.id}")
        print("Use Child 1 ID or Child 2 ID to test the ancestry endpoint, or Grandpa ID to test the descendants endpoint.")

if __name__ == "__main__":
    seed_data()
