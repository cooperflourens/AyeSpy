# AyeSpy Setup and Testing Instructions

## Quick Start Guide

This guide will help you set up and test the AyeSpy congressional transparency platform step by step.

## Prerequisites

- **Python 3.8+** (Python 3.12 recommended)
- **Conda** or **Miniconda** installed
- **PostgreSQL** server (local or remote)
- **Milvus** vector database (optional for basic testing)
- **8GB+ RAM** (for AI models)

## Phase 1: Environment Setup

### Step 1: Create Conda Environment

```bash
# Navigate to the AyeSpy directory
cd /path/to/AyeSpy

# Create conda environment from the provided file
conda env create -f environment.yml

# Activate the environment
conda activate SEEK
```

### Step 2: Install Additional Dependencies

```bash
# Install any missing Python packages
pip install flask python-dotenv rich sqlalchemy psycopg2-binary

# Verify installation
python -c "import flask, sqlalchemy, transformers, torch; print('All dependencies installed!')"
```

### Step 3: Verify GPU Support (Optional)

```bash
# Check if PyTorch can use GPU (optional, CPU works fine)
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## Phase 2: Database Configuration

### Step 1: PostgreSQL Setup

**Option A: Local PostgreSQL Installation**
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# Or on macOS with Homebrew
brew install postgresql

# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS
```

**Option B: Docker PostgreSQL (Recommended for testing)**
```bash
# Run PostgreSQL in Docker
docker run --name ayespy-postgres \
  -e POSTGRES_DB=seek \
  -e POSTGRES_USER=seek_user \
  -e POSTGRES_PASSWORD=secret \
  -p 5432:5432 \
  -d postgres:13

# Verify connection
docker exec -it ayespy-postgres psql -U seek_user -d seek -c "SELECT version();"
```

### Step 2: Create Database and User

```sql
-- Connect to PostgreSQL as superuser
sudo -u postgres psql

-- Create database and user
CREATE DATABASE seek;
CREATE USER seek_user WITH PASSWORD 'secret';
GRANT ALL PRIVILEGES ON DATABASE seek TO seek_user;
ALTER USER seek_user CREATEDB;

-- Exit PostgreSQL
\q
```

### Step 3: Milvus Setup (Optional)

**Option A: Docker Milvus (Easiest)**
```bash
# Download Milvus docker compose
wget https://github.com/milvus-io/milvus/releases/download/v2.3.0/milvus-standalone-docker-compose.yml -O docker-compose.yml

# Start Milvus
docker-compose up -d

# Verify Milvus is running
curl http://localhost:19530/health
```

**Option B: Skip Milvus for Initial Testing**
- The system can work with PostgreSQL only for basic functionality
- Semantic search features will be limited without Milvus

## Phase 3: Environment Variables

### Step 1: Create Environment File

```bash
# Create .env file in the project root
touch .env
```

### Step 2: Configure Environment Variables

```env
# Database Configuration
DATABASE_URL=postgresql://seek_user:secret@localhost:5432/seek
POSTGRES_DB_NAME=seek
POSTGRES_USER=seek_user
POSTGRES_PASSWORD=secret
POSTGRES_HOST=localhost

# Milvus Configuration (optional)
MILVUS_HOST=localhost
MILVUS_PORT=19530

# API Keys (optional for initial testing)
CONGRESS_API_KEY=your_congress_api_key_here
GOVINFO_API_KEY=your_govinfo_api_key_here

# AI Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
SIMILARITY_THRESHOLD=0.3

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

## Phase 4: Initialize Database Schema

### Step 1: Test Database Connection

```bash
# Test PostgreSQL connection
python -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://seek_user:secret@localhost:5432/seek')
    print('✅ PostgreSQL connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ PostgreSQL connection failed: {e}')
"
```

### Step 2: Initialize Database Tables

```bash
# Run database migrations/setup
python -c "
from database.migrations import initialize_database
success, message = initialize_database()
print('✅ Database initialized!' if success else f'❌ Database setup failed: {message}')
"
```

## Phase 5: Load Test Data

### Step 1: Prepare Sample Data

```bash
# The system already includes sample data files:
# - congressional_hearings_test2.csv (sample hearing transcripts)
# - data/legislators-current.csv (representative information)
# - data/committee_data.csv (committee information)

# Verify data files exist
ls -la congressional_hearings_test2.csv data/legislators-current.csv data/committee_data.csv
```

### Step 2: Load Basic Data

```bash
# Load sample congressional hearing data
python delete_and_load_documents.py
```

## Phase 6: Start the Web UI

### Step 1: Test the Flask Application

```bash
# Start the web interface
python ui.py
```

### Step 2: Access the Interface

1. **Open your web browser**
2. **Navigate to**: http://localhost:5000
3. **You should see**: "AyeSpy" interface with:
   - Capitol building background
   - Search form with politician dropdown
   - Issue search field
   - Time range selector

### Step 3: Test Basic Functionality

1. **Politician Search**: Try typing a name in the search field
2. **Issue Search**: Enter a topic like "healthcare" or "defense"
3. **Time Range**: Select different time ranges
4. **Submit**: Click the submit button to test form handling

## Phase 7: Start the Terminal Application

### Step 1: Launch Terminal Interface

```bash
# Run the main terminal application
python main.py

# Or use the simple runner
python run.py
```

### Step 2: Explore Terminal Features

The terminal application provides:

1. **🔍 Search Transcripts**: Semantic search of congressional transcripts
2. **📋 Track Bills**: Bill tracking and lifecycle monitoring
3. **🗳️ View Voting History**: Representative voting records
4. **📊 View Recent Updates**: Latest congressional activity
5. **🔄 Sync Data**: Data synchronization from APIs
6. **⚙️ System Status**: Health monitoring and diagnostics

### Step 3: Test System Status

1. **Select option 6** (System Status) from the main menu
2. **Verify** that all components show as healthy:
   - ✅ Database: Healthy
   - ✅ Congress.gov API: Connected (if API keys configured)
   - ✅ GovInfo API: Connected (if API keys configured)
   - ✅ Embedding Service: Loaded

## Troubleshooting

### Common Issues

**Issue**: Database connection failed
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list postgresql     # macOS

# Check if database exists
psql -U seek_user -d seek -c "SELECT 1;"
```

**Issue**: Conda environment creation failed
```bash
# Update conda
conda update conda

# Try creating with explicit Python version
conda create -n SEEK python=3.12
conda activate SEEK
pip install -r requirements.txt  # if requirements.txt exists
```

**Issue**: Import errors
```bash
# Reinstall problematic packages
pip install --force-reinstall transformers torch sqlalchemy

# Verify Python path
python -c "import sys; print(sys.path)"
```

**Issue**: Port already in use
```bash
# Find process using port 5000
lsof -i :5000
# Kill process if needed
kill -9 <PID>

# Or run Flask on different port
FLASK_RUN_PORT=5001 python ui.py
```

### Performance Tips

1. **GPU Acceleration**: If available, PyTorch will automatically use GPU for faster embeddings
2. **Database Indexing**: The system includes optimized indexes for search performance
3. **Batch Processing**: Large data imports are processed in batches for efficiency

## Next Steps

Once the system is running:

1. **Test Search**: Try different search queries in both web and terminal interfaces
2. **Explore Data**: Browse the congressional hearing transcripts and representative data
3. **Add API Keys**: Configure Congress.gov and GovInfo API keys for live data
4. **Customize**: Modify search parameters, add new data sources, or enhance the UI

## Getting Help

- **Check Logs**: Look at `ayespy.log` for detailed error information
- **Database Issues**: Verify connection strings and permissions
- **Missing Data**: Ensure sample data files are in the correct locations
- **Performance**: Monitor system resources during AI model loading

## Success Indicators

✅ **Environment Setup Complete**: Conda environment activated with all dependencies
✅ **Database Connected**: PostgreSQL connection successful
✅ **Web UI Running**: Flask application accessible at http://localhost:5000
✅ **Terminal App Working**: Rich CLI interface with all menu options
✅ **Search Functional**: Can search congressional transcripts and get results
✅ **Data Loaded**: Sample congressional hearing data available for testing

The system is now ready for testing and development!
