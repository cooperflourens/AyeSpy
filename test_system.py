#!/usr/bin/env python3
"""
AyeSpy System Test Script
Tests all major components to ensure proper setup.
"""

import sys
import os
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports() -> Dict[str, bool]:
    """Test that all required packages can be imported."""
    results = {}
    
    # Core packages
    test_packages = [
        ('flask', 'Flask web framework'),
        ('sqlalchemy', 'Database ORM'),
        ('psycopg2', 'PostgreSQL connector'),
        ('torch', 'PyTorch for AI models'),
        ('transformers', 'Hugging Face transformers'),
        ('pandas', 'Data manipulation'),
        ('rich', 'Terminal UI'),
        ('requests', 'HTTP client'),
        ('numpy', 'Numerical computing')
    ]
    
    for package, description in test_packages:
        try:
            __import__(package)
            print(f"✅ {package:<15} - {description}")
            results[package] = True
        except ImportError as e:
            print(f"❌ {package:<15} - {description} (Error: {e})")
            results[package] = False
    
    return results

def test_optional_imports() -> Dict[str, bool]:
    """Test optional packages."""
    results = {}
    
    optional_packages = [
        ('pymilvus', 'Milvus vector database'),
        ('sentence_transformers', 'Sentence embeddings'),
        ('dotenv', 'Environment variables')
    ]
    
    print("\nOptional packages:")
    for package, description in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package:<20} - {description}")
            results[package] = True
        except ImportError:
            print(f"⚠️  {package:<20} - {description} (Optional)")
            results[package] = False
    
    return results

def test_database_connection() -> bool:
    """Test PostgreSQL database connection."""
    try:
        import psycopg2
        
        # Try to connect with default settings
        conn_strings = [
            "postgresql://seek_user:secret@localhost:5432/seek",
            "postgresql://postgres:postgres@localhost:5432/postgres",
            "postgresql://localhost:5432/postgres"
        ]
        
        for conn_string in conn_strings:
            try:
                conn = psycopg2.connect(conn_string)
                print(f"✅ PostgreSQL connection successful: {conn_string}")
                conn.close()
                return True
            except psycopg2.OperationalError:
                continue
        
        print("❌ PostgreSQL connection failed - check database setup")
        return False
        
    except ImportError:
        print("❌ psycopg2 not available - cannot test database")
        return False

def test_milvus_connection() -> bool:
    """Test Milvus vector database connection."""
    try:
        from pymilvus import connections, utility
        
        connections.connect("default", host="localhost", port="19530")
        
        # Test basic functionality
        collections = utility.list_collections()
        print(f"✅ Milvus connection successful - {len(collections)} collections found")
        return True
        
    except Exception as e:
        print(f"⚠️  Milvus connection failed (optional): {e}")
        return False

def test_ai_models() -> bool:
    """Test AI model loading."""
    try:
        import torch
        from transformers import BertTokenizer, BertModel
        
        print("🧠 Testing AI models...")
        
        # Check PyTorch
        if torch.cuda.is_available():
            print(f"✅ PyTorch with CUDA support - {torch.cuda.get_device_name()}")
        else:
            print("✅ PyTorch (CPU only)")
        
        # Test BERT model loading (this might take time on first run)
        try:
            tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            model = BertModel.from_pretrained('bert-base-uncased')
            print("✅ BERT model loaded successfully")
            
            # Quick inference test
            inputs = tokenizer("Hello, this is a test", return_tensors='pt')
            with torch.no_grad():
                outputs = model(**inputs)
            
            embedding_size = outputs.last_hidden_state.shape[-1]
            print(f"✅ BERT inference test passed - embedding size: {embedding_size}")
            return True
            
        except Exception as e:
            print(f"❌ BERT model test failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ AI model test failed - missing imports: {e}")
        return False

def test_data_files() -> Dict[str, bool]:
    """Test that required data files exist."""
    results = {}
    
    data_files = [
        'congressional_hearings_test2.csv',
        'data/legislators-current.csv',
        'data/committee_data.csv',
        'environment.yml'
    ]
    
    print("\nData files:")
    for file_path in data_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path:<35} ({file_size:,} bytes)")
            results[file_path] = True
        else:
            print(f"❌ {file_path:<35} (Missing)")
            results[file_path] = False
    
    return results

def test_project_structure() -> Dict[str, bool]:
    """Test that project structure is correct."""
    results = {}
    
    required_dirs = [
        'database',
        'services', 
        'api',
        'data',
        'gpo_data_scraper',
        'static'
    ]
    
    required_files = [
        'ui.py',
        'main.py',
        'run.py',
        'embedding_utils.py',
        'postgres_utils.py'
    ]
    
    print("\nProject structure:")
    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            print(f"✅ {dir_name}/ directory exists")
            results[dir_name] = True
        else:
            print(f"❌ {dir_name}/ directory missing")
            results[dir_name] = False
    
    for file_name in required_files:
        if os.path.isfile(file_name):
            print(f"✅ {file_name} file exists")
            results[file_name] = True
        else:
            print(f"❌ {file_name} file missing")
            results[file_name] = False
    
    return results

def test_flask_app() -> bool:
    """Test that Flask app can be imported."""
    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())
        
        # Try to import the Flask app
        from ui import app
        print("✅ Flask application imports successfully")
        
        # Test basic app configuration
        if app.config.get('DEBUG') is not None:
            print("✅ Flask app configuration loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def main():
    """Run all system tests."""
    print("🏛️  AyeSpy Congressional Transparency Platform")
    print("=" * 50)
    print("System Test Script")
    print("=" * 50)
    
    # Test imports
    print("\nCore package imports:")
    import_results = test_imports()
    optional_results = test_optional_imports()
    
    # Test project structure
    structure_results = test_project_structure()
    
    # Test data files
    data_results = test_data_files()
    
    # Test database connections
    print("\nDatabase connections:")
    db_result = test_database_connection()
    milvus_result = test_milvus_connection()
    
    # Test Flask app
    print("\nFlask application:")
    flask_result = test_flask_app()
    
    # Test AI models (this might take time)
    print("\nAI models:")
    ai_result = test_ai_models()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    core_packages_ok = all(import_results.values())
    structure_ok = all(structure_results.values())
    data_files_ok = all(data_results.values())
    
    print(f"✅ Core packages:     {'PASS' if core_packages_ok else 'FAIL'}")
    print(f"✅ Project structure: {'PASS' if structure_ok else 'FAIL'}")
    print(f"✅ Data files:        {'PASS' if data_files_ok else 'FAIL'}")
    print(f"✅ PostgreSQL:        {'PASS' if db_result else 'FAIL'}")
    print(f"⚠️  Milvus (optional): {'PASS' if milvus_result else 'FAIL (Optional)'}")
    print(f"✅ Flask app:         {'PASS' if flask_result else 'FAIL'}")
    print(f"✅ AI models:         {'PASS' if ai_result else 'FAIL'}")
    
    # Overall assessment
    critical_tests = [core_packages_ok, structure_ok, flask_result]
    if all(critical_tests):
        print("\n🎉 SYSTEM READY FOR TESTING!")
        print("\nNext steps:")
        print("1. Start the web UI:      python ui.py")
        print("2. Start terminal app:    python main.py")
        print("3. Load test data:        python delete_and_load_documents.py")
        return True
    else:
        print("\n❌ SYSTEM NOT READY")
        print("\nPlease fix the issues above before proceeding.")
        print("See SETUP_INSTRUCTIONS.md for detailed setup steps.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)