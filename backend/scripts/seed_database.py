import os
import sys
import argparse

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import engine, Base, init_db
from scripts.generate_data import SyntheticDataGenerator

def seed(mode: str = "starter", seed_num: int = 20261022):
    print(f"=== Resetting and Seeding Database ({mode} mode, seed: {seed_num}) ===")
    Base.metadata.drop_all(bind=engine)
    init_db()
    generator = SyntheticDataGenerator(mode=mode, seed=seed_num)
    generator.run()
    print("=== Database Seed Completed Successfully ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed database with synthetic supply chain data")
    parser.add_argument("--mode", choices=["starter", "full"], default="starter")
    parser.add_argument("--seed", type=int, default=20261022)
    args = parser.parse_args()
    seed(mode=args.mode, seed_num=args.seed)
