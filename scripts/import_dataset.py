"""
Script untuk import dataset makanan ke database
Usage: python scripts/import_dataset.py path/to/file.csv
"""

import sys
import os
import csv
import uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from app.database import settings

DATABASE_URL = (
    f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

def import_dataset(csv_path, mode='replace'):
    """
    Import dataset dari CSV ke database.
    
    Args:
        csv_path: Path ke file CSV
        mode: 'replace' (hapus semua lalu import) atau 'append' (tambah baru)
    """
    print(f"\n{'='*80}")
    print(f"📦 DATASET IMPORT TOOL")
    print(f"{'='*80}\n")
    
    # Check file exists
    if not os.path.exists(csv_path):
        print(f"❌ Error: File tidak ditemukan: {csv_path}")
        return
    
    # Count rows
    with open(csv_path, 'r', encoding='utf-8') as f:
        total_rows = sum(1 for line in f) - 1  # Exclude header
    
    print(f"📊 Dataset info:")
    print(f"   File: {csv_path}")
    print(f"   Total rows: {total_rows:,}")
    print(f"   Mode: {mode}")
    print()
    
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # If replace mode, delete all existing data
            if mode == 'replace':
                print(f"⚠️  REPLACE MODE: Menghapus semua data makanan yang ada...")
                conn.execute(text("DELETE FROM foods"))
                conn.commit()
                print(f"✅ Semua data makanan dihapus\n")
            
            # Read CSV and insert
            print(f"📥 Importing data...")
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                inserted = 0
                errors = 0
                duplicates = 0
                
                for i, row in enumerate(reader, 1):
                    try:
                        # Validate required fields
                        if not row.get('name'):
                            print(f"   ⚠️  Row {i}: Missing 'name', skipping...")
                            errors += 1
                            continue
                        
                        # Generate UUID if not provided
                        if not row.get('id'):
                            row['id'] = str(uuid.uuid4())
                        
                        # Check if name already exists
                        result = conn.execute(
                            text("SELECT id FROM foods WHERE name = :name"),
                            {"name": row['name']}
                        ).fetchone()
                        
                        if result:
                            print(f"   ⚠️  Row {i}: '{row['name']}' already exists, skipping...")
                            duplicates += 1
                            continue
                        
                        # Insert food
                        conn.execute(text("""
                            INSERT INTO foods (
                                id, name, name_aliases, cal, protein, carbs, fat, 
                                default_portion_g, source, is_indonesian
                            ) VALUES (
                                :id, :name, :name_aliases, :cal, :protein, :carbs, :fat,
                                :default_portion_g, :source, :is_indonesian
                            )
                        """), {
                            "id": row['id'],
                            "name": row['name'],
                            "name_aliases": row.get('name_aliases', ''),
                            "cal": float(row['cal']) if row.get('cal') else None,
                            "protein": float(row['protein']) if row.get('protein') else 0.0,
                            "carbs": float(row['carbs']) if row.get('carbs') else 0.0,
                            "fat": float(row['fat']) if row.get('fat') else 0.0,
                            "default_portion_g": float(row['default_portion_g']) if row.get('default_portion_g') else 100.0,
                            "source": row.get('source', 'unknown'),
                            "is_indonesian": row.get('is_indonesian', '').lower() == 'true',
                        })
                        
                        inserted += 1
                        
                        # Progress indicator
                        if i % 100 == 0:
                            print(f"   Processed {i}/{total_rows} rows...")
                        
                    except Exception as e:
                        print(f"   ❌ Row {i}: Error - {e}")
                        errors += 1
                        continue
                
                conn.commit()
            
            print(f"\n{'='*80}")
            print(f"✅ IMPORT COMPLETED")
            print(f"{'='*80}")
            print(f"   ✅ Inserted: {inserted:,} foods")
            print(f"   ⚠️  Duplicates: {duplicates:,}")
            print(f"   ❌ Errors: {errors:,}")
            print(f"   📊 Total in file: {total_rows:,}")
            print(f"{'='*80}\n")
            
            # Verify
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM foods"))
                count = result.scalar()
                print(f"📦 Total foods in database: {count:,}\n")
                
    except Exception as e:
        print(f"\n❌ Import failed: {e}\n")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_dataset.py <csv_file> [replace|append]")
        print("\nExample:")
        print("  python scripts/import_dataset.py dataset/foods_combined.csv")
        print("  python scripts/import_dataset.py dataset/foods_combined.csv append")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'replace'
    
    import_dataset(csv_file, mode)
