# 🏛️ AyeSpy - Start Here!

## 🚀 Quick Start Instructions

**Get AyeSpy running in 10 minutes with these simple steps:**

### Step 1: Setup Environment (2 minutes)

**🪟 Windows Users - If you get "ResolvePackageNotFound" error:**
```bash
# Use the Windows-specific setup script
python setup-windows.py
```

**🐧 Linux/Mac Users or if Windows script doesn't work:**
```bash
# Navigate to the AyeSpy directory
cd /path/to/AyeSpy

# Try the original environment file
conda env create -f environment.yml
conda activate SEEK

# If that fails, try the simplified version
conda env create -f environment-windows.yml
conda activate SEEK

# Install additional dependencies
pip install -r requirements.txt
```

**Manual Setup (if conda environments fail):**
```bash
# Create basic environment
conda create -n SEEK python=3.12
conda activate SEEK

# Install core packages
pip install flask pandas numpy requests rich transformers torch sqlalchemy psycopg2-binary python-dotenv beautifulsoup4 sentence-transformers
```

### Step 2: Setup Database (3 minutes)

**Option A: Docker PostgreSQL (Easiest)**
```bash
# Start PostgreSQL in Docker
docker run --name ayespy-postgres \
  -e POSTGRES_DB=seek \
  -e POSTGRES_USER=seek_user \
  -e POSTGRES_PASSWORD=secret \
  -p 5432:5432 \
  -d postgres:13
```

**Option B: Local PostgreSQL**
```bash
# If you have PostgreSQL installed locally
sudo -u postgres createdb seek
sudo -u postgres createuser seek_user
```

### Step 3: Initialize System (2 minutes)

```bash
# Run system tests
python test_system.py

# Initialize database and load sample data
python init_database.py
python simple_data_loader.py
```

### Step 4: Start AyeSpy! (1 minute)

**Option A: Web Interface**
```bash
python ui.py
# Then open: http://localhost:5000
```

**Option B: Terminal Application**
```bash
python main.py
# Interactive terminal interface
```

**Option C: Interactive Menu**
```bash
python quick_start.py
# Guided setup and testing
```

---

## 🌟 What You'll See

### Web Interface (ui.py)
- **Beautiful Interface**: Capitol building background with professional design
- **Smart Search**: Politician autocomplete dropdown with real congressional data
- **Advanced Filters**: Search by issue, time range, and more
- **Responsive Design**: Works on desktop and mobile

### Terminal Application (main.py)
- **Rich CLI**: Colorful, interactive terminal interface
- **Multiple Modules**:
  - 🔍 Semantic transcript search
  - 📋 Bill tracking and lifecycle
  - 🗳️ Voting history analysis
  - 📊 Recent congressional updates
  - 🔄 Data synchronization
  - ⚙️ System health monitoring

---

## 🧪 Testing Your Setup

### Quick Health Check
```bash
# Test all components at once
python test_system.py
```

Should show:
- ✅ Core packages: PASS
- ✅ Project structure: PASS  
- ✅ Data files: PASS
- ✅ PostgreSQL: PASS
- ✅ Flask app: PASS
- ✅ AI models: PASS

### Test Individual Components

**Database Test:**
```bash
python -c "
import postgres_utils
conn = postgres_utils.connect('seek', 'seek_user', 'secret', 'localhost')
print('✅ Database OK' if conn else '❌ Database Error')
"
```

**Web UI Test:**
```bash
# Start web server
python ui.py

# In another terminal, test the endpoint
curl http://localhost:5000
```

**Data Test:**
```bash
python -c "
import pandas as pd
df = pd.read_csv('congressional_hearings_test2.csv')
print(f'✅ Sample data: {len(df)} congressional hearing records')
"
```

---

## 🎯 Sample Searches to Try

### Web Interface Searches
1. **Politician**: "Alexandria Ocasio-Cortez" or "Ted Cruz"  
2. **Issue**: "climate change" or "healthcare reform"
3. **Time Range**: "Past month" with current topics

### Terminal App Searches
1. **Defense Topics**: "military spending", "national security"
2. **Healthcare**: "medicare", "healthcare costs"
3. **Technology**: "artificial intelligence", "cybersecurity"
4. **Environment**: "renewable energy", "climate policy"

### Expected Results
- **Speaker identification**: Real congressional representatives
- **Contextual quotes**: Actual hearing transcripts
- **Metadata**: Committee names, hearing dates, similarity scores
- **Rich formatting**: Colored output, tables, progress bars

---

## 🛠️ Troubleshooting

### Common Issues & Solutions

**Issue: "ImportError" or missing packages**
```bash
# Reinstall dependencies
conda activate SEEK
pip install --force-reinstall -r requirements.txt
```

**Issue: "Database connection failed"**
```bash
# Check if PostgreSQL is running
docker ps  # if using Docker
sudo systemctl status postgresql  # if local install

# Restart if needed
docker start ayespy-postgres
```

**Issue: "Port 5000 already in use"**
```bash
# Use different port
FLASK_RUN_PORT=5001 python ui.py
```

**Issue: "AI models downloading slowly"**
```bash
# First run downloads BERT models (~500MB)
# This is normal and only happens once
# Subsequent runs will be much faster
```

**Issue: "No search results"**
```bash
# Reload sample data
python simple_data_loader.py

# Verify data exists
python -c "
import postgres_utils
conn = postgres_utils.connect('seek', 'seek_user', 'secret', 'localhost')
data = postgres_utils.head_postgresql(conn, 'documents', 5)
print(f'Records in database: {len(data)}')
"
```

---

## 📊 System Requirements

### Minimum Requirements
- **Python**: 3.8+
- **RAM**: 4GB (8GB+ recommended for AI models)
- **Storage**: 2GB free space
- **Database**: PostgreSQL 12+

### Recommended Setup
- **Python**: 3.12
- **RAM**: 16GB
- **GPU**: CUDA-compatible (optional, speeds up AI processing)
- **Database**: PostgreSQL 15 + Milvus 2.3 (for advanced vector search)

---

## 🌐 What's Included

### Real Congressional Data
- **118th Congress Hearings**: Actual transcripts from 2023-2024
- **Strategic Forces Committee**: Defense and military hearings
- **Representative Database**: 500+ current legislators
- **Committee Structure**: House and Senate committees

### AI-Powered Features
- **Semantic Search**: Find concepts, not just keywords
- **BERT Embeddings**: State-of-the-art text understanding
- **Similarity Scoring**: Relevance-ranked results
- **Speaker Identification**: Automatic attribution

### Advanced Capabilities
- **Bill Tracking**: Complete legislative lifecycle
- **Voting Analysis**: Representative voting patterns
- **Real-time Sync**: Live congressional data updates
- **Rich Terminal UI**: Beautiful command-line interface

---

## 🎉 Success Indicators

You know AyeSpy is working correctly when:

### Web Interface ✅
- [ ] Page loads at http://localhost:5000 with Capitol background
- [ ] Politician dropdown shows real names (try typing "Biden")
- [ ] Form submission works without errors
- [ ] No JavaScript console errors

### Terminal Interface ✅  
- [ ] Rich colorful menu appears
- [ ] System Status (option 6) shows all components healthy
- [ ] Search Transcripts finds real congressional quotes
- [ ] Help system provides detailed information

### Database ✅
- [ ] PostgreSQL connects successfully
- [ ] Sample data loads (100+ hearing records)
- [ ] Legislator names appear in autocomplete
- [ ] No connection timeout errors

### AI Models ✅
- [ ] BERT models download and load successfully
- [ ] Embedding generation works
- [ ] Search similarity scores make sense
- [ ] No out-of-memory errors

---

## 🚀 Next Steps

Once basic testing works:

1. **Add API Keys**: Get live congressional data
   - Congress.gov API key
   - GovInfo API key

2. **Advanced Setup**: 
   - Configure Milvus for vector search
   - Set up automated data updates
   - Optimize database indexes

3. **Customization**:
   - Add new search filters
   - Customize the web interface
   - Add data visualizations

4. **Production Deployment**:
   - Configure environment variables
   - Set up reverse proxy
   - Enable SSL/HTTPS

---

## 📞 Getting Help

If you encounter issues:

1. **Run Diagnostics**: `python test_system.py`
2. **Check Logs**: Look for error messages in terminal
3. **Review Files**: 
   - `SETUP_INSTRUCTIONS.md` - Detailed setup
   - `TESTING_GUIDE.md` - Comprehensive testing
   - `ayespy.log` - Application logs

4. **Component Testing**:
   - Database: `python init_database.py`
   - Data: `python simple_data_loader.py`
   - System: `python test_system.py`

---

**🏛️ Welcome to AyeSpy - Making Congressional Information Accessible!**

*"Democracy works best when citizens have access to the information they need to hold their representatives accountable."*
