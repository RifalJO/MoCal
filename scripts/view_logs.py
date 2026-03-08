"""
Quick script to view latest log details from database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from app.database import settings

DATABASE_URL = (
    f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

def view_latest_logs(limit=5):
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT 
                id,
                raw_input,
                total_kcal,
                log_detail,
                logged_at
            FROM food_logs
            ORDER BY logged_at DESC
            LIMIT {limit}
        """))
        
        rows = result.fetchall()
        
        print(f"\n{'='*80}")
        print(f"📋 LATEST {limit} LOG ENTRIES")
        print(f"{'='*80}\n")
        
        for i, row in enumerate(rows, 1):
            print(f"--- Log #{i} ---")
            print(f"ID:          {row.id}")
            print(f"Input:       {row.raw_input}")
            print(f"Calories:    {row.total_kcal} kcal")
            print(f"Time:        {row.logged_at}")
            
            if row.log_detail:
                print(f"\n📄 Log Details:")
                parsing = row.log_detail.get('parsing', {})
                summary = row.log_detail.get('summary', {})
                
                print(f"   - Items parsed:     {parsing.get('parsed_items_count', 'N/A')}")
                print(f"   - Parse time:       {parsing.get('parse_time_ms', 'N/A')}ms")
                print(f"   - Total time:       {summary.get('total_time_ms', 'N/A')}ms")
                print(f"   - Items matched:    {summary.get('total_items_matched', 'N/A')}")
                print(f"   - Unknown items:    {summary.get('unknown_items', 'N/A')}")
                
                # Show LLM response preview
                llm_response = parsing.get('llm_raw_response', '')
                if llm_response:
                    preview = llm_response[:200].replace('\n', ' ')
                    print(f"\n   🤖 LLM Output Preview:")
                    print(f"      {preview}...")
            else:
                print(f"   ⚠️  No log_detail available")
            
            print(f"\n")
        
        print(f"{'='*80}\n")

if __name__ == "__main__":
    view_latest_logs()
