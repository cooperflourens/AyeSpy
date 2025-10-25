#!/usr/bin/env python3
"""
Simple test script to verify AyeSpy system functionality.
"""

import os
import sys
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db_manager
from database.migrations import initialize_database, check_database_health
from services.embedding_service import EmbeddingService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_database():
    """Test database functionality."""
    print("🔍 Testing database...")
    
    try:
        # Initialize database
        success, message = initialize_database()
        if success:
            print("✅ Database initialized successfully")
        else:
            print(f"❌ Database initialization failed: {message}")
            return False
        
        # Check database health
        is_healthy, message = check_database_health()
        if is_healthy:
            print("✅ Database health check passed")
        else:
            print(f"❌ Database health check failed: {message}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_embedding_service():
    """Test embedding service functionality."""
    print("🔍 Testing embedding service...")
    
    try:
        # Initialize embedding service
        embedding_service = EmbeddingService()
        
        # Test basic functionality
        test_text = "This is a test of the embedding service."
        embedding = embedding_service.generate_embedding(test_text)
        
        if embedding is not None and len(embedding) > 0:
            print("✅ Embedding service working")
            
            # Test model info
            model_info = embedding_service.get_model_info()
            print(f"   Model: {model_info.get('model_name', 'Unknown')}")
            print(f"   Dimension: {model_info.get('embedding_dimension', 'Unknown')}")
            
            return True
        else:
            print("❌ Embedding generation failed")
            return False
        
    except Exception as e:
        print(f"❌ Embedding service test failed: {e}")
        return False


def test_basic_search():
    """Test basic search functionality."""
    print("🔍 Testing basic search...")
    
    try:
        from services.search_service import SearchService
        from services.embedding_service import EmbeddingService
        
        embedding_service = EmbeddingService()
        search_service = SearchService(embedding_service, get_db_manager())
        
        # Test search statistics
        stats = search_service.get_search_statistics()
        print(f"✅ Search service initialized")
        print(f"   Total segments: {stats.get('total_transcript_segments', 0)}")
        print(f"   Embedding coverage: {stats.get('embedding_coverage', '0%')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic search test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting AyeSpy system tests...")
    print("=" * 50)
    
    tests = [
        ("Database", test_database),
        ("Embedding Service", test_embedding_service),
        ("Basic Search", test_basic_search),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test passed")
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 