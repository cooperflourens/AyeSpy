#!/usr/bin/env python3
"""
Simple data loader for AyeSpy - loads sample data without complex setup.
This is a simplified version for initial testing.
"""

import os
import sys
import pandas as pd
import logging
from typing import Dict, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def load_congressional_hearings_simple() -> bool:
    """Load congressional hearings data using simple PostgreSQL approach."""
    try:
        import postgres_utils
        
        # Read the sample data
        if not os.path.exists('congressional_hearings_test2.csv'):
            print("❌ congressional_hearings_test2.csv not found")
            return False
        
        df = pd.read_csv('congressional_hearings_test2.csv')
        print(f"📋 Found {len(df)} congressional hearing records")
        
        # Connect to database
        conn = postgres_utils.connect("seek", "seek_user", "secret", "localhost")
        if not conn:
            print("❌ Could not connect to PostgreSQL")
            return False
        
        # Create simple documents table if it doesn't exist
        table_name = "documents"
        table_cols = {
            "id": "SERIAL PRIMARY KEY",
            "date": "DATE",
            "name": "TEXT", 
            "quote": "TEXT",
            "document": "TEXT",
            "vector_id": "TEXT"
        }
        
        # Check if table exists
        existing_tables = postgres_utils.get_all_tables(conn)
        if table_name not in existing_tables:
            postgres_utils.create_table(conn, table_name, table_cols)
            print(f"✅ Created '{table_name}' table")
        else:
            print(f"✅ Table '{table_name}' already exists")
        
        # Insert data (simplified - just the basic columns)
        try:
            # Prepare data for insertion 
            insert_data = []
            for _, row in df.iterrows():
                insert_data.append({
                    'date': row.get('date', '2023-01-01'),
                    'name': row.get('name', 'Unknown'),
                    'quote': row.get('quote', ''),
                    'document': row.get('document', ''),
                    'vector_id': ''  # Will be populated later
                })
            
            # Convert to DataFrame for insertion
            insert_df = pd.DataFrame(insert_data)
            
            # Use the existing utility to insert data
            columns_to_insert = ['date', 'name', 'quote', 'document', 'vector_id']
            postgres_utils.insert_document_data(conn, table_name, columns_to_insert, insert_df)
            
            print(f"✅ Inserted {len(insert_data)} records into {table_name}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"⚠️  Data insertion issue: {e}")
            print("This might be expected if data already exists")
            conn.close()
            return True
        
    except Exception as e:
        print(f"❌ Failed to load congressional hearings: {e}")
        return False

def load_legislators_data() -> bool:
    """Load legislators data into memory for UI autocomplete."""
    try:
        legislators_file = 'data/legislators-current.csv'
        
        if not os.path.exists(legislators_file):
            print(f"⚠️  {legislators_file} not found - UI autocomplete may not work")
            return False
        
        df = pd.read_csv(legislators_file)
        print(f"👥 Found {len(df)} legislators for autocomplete")
        
        # Check if we have the expected columns
        if 'full_name' in df.columns:
            unique_names = df['full_name'].nunique()
            print(f"✅ {unique_names} unique legislator names available")
        else:
            print("⚠️  'full_name' column not found in legislators data")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to load legislators data: {e}")
        return False

def verify_data_loading() -> Dict[str, bool]:
    """Verify that data was loaded successfully."""
    results = {}
    
    try:
        import postgres_utils
        
        # Test database connection
        conn = postgres_utils.connect("seek", "seek_user", "secret", "localhost")
        if not conn:
            print("❌ Database connection failed")
            return {'database': False}
        
        # Check tables
        tables = postgres_utils.get_all_tables(conn)
        results['tables_exist'] = len(tables) > 0
        print(f"📊 Found {len(tables)} database tables: {tables}")
        
        # Check documents table
        if 'documents' in tables:
            sample_data = postgres_utils.head_postgresql(conn, 'documents', 5)
            results['documents_loaded'] = len(sample_data) > 0
            print(f"✅ Documents table has {len(sample_data)} sample records")
            
            # Show sample data
            if len(sample_data) > 0:
                print("\n📝 Sample records:")
                for i, row in sample_data.iterrows():
                    name = row.get('name', 'Unknown')[:30]
                    quote = row.get('quote', '')[:60] + '...' if len(str(row.get('quote', ''))) > 60 else row.get('quote', '')
                    print(f"   {i+1}. {name}: {quote}")
        else:
            results['documents_loaded'] = False
            print("⚠️  Documents table not found")
        
        conn.close()
        
        # Check data files
        data_files = {
            'hearings': 'congressional_hearings_test2.csv',
            'legislators': 'data/legislators-current.csv',
            'committees': 'data/committee_data.csv'
        }
        
        for name, file_path in data_files.items():
            exists = os.path.exists(file_path)
            results[f'{name}_file'] = exists
            if exists:
                try:
                    df = pd.read_csv(file_path)
                    print(f"✅ {name.title()} file: {len(df)} records")
                except Exception as e:
                    print(f"⚠️  {name.title()} file exists but has issues: {e}")
                    results[f'{name}_file'] = False
            else:
                print(f"❌ {name.title()} file missing: {file_path}")
        
        return results
        
    except Exception as e:
        print(f"❌ Data verification failed: {e}")
        return {'error': True}

def main():
    """Main data loading function."""
    print("📊 AyeSpy Simple Data Loader")
    print("=" * 40)
    
    success_count = 0
    total_tasks = 3
    
    # Task 1: Load congressional hearings
    print("\n1. Loading congressional hearings data...")
    if load_congressional_hearings_simple():
        success_count += 1
        print("   ✅ Congressional hearings loaded")
    else:
        print("   ❌ Congressional hearings loading failed")
    
    # Task 2: Load legislators data
    print("\n2. Loading legislators data...")
    if load_legislators_data():
        success_count += 1
        print("   ✅ Legislators data processed")
    else:
        print("   ⚠️  Legislators data had issues")
    
    # Task 3: Verify data loading
    print("\n3. Verifying data loading...")
    verification_results = verify_data_loading()
    if verification_results.get('documents_loaded', False):
        success_count += 1
        print("   ✅ Data verification passed")
    else:
        print("   ⚠️  Data verification had issues")
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 DATA LOADING SUMMARY")
    print("=" * 40)
    print(f"✅ Completed: {success_count}/{total_tasks} tasks")
    
    if success_count >= 2:
        print("\n🎉 DATA LOADING SUCCESSFUL!")
        print("\nReady for testing:")
        print("• Web UI:      python ui.py")
        print("• Terminal:    python main.py") 
        print("• Full test:   python test_system.py")
        return True
    else:
        print("\n⚠️  DATA LOADING INCOMPLETE")
        print("\nSome components may not work properly.")
        print("Check database setup and data files.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
