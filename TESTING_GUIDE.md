# AyeSpy Testing Guide

## Quick Start - Get Running in 5 Minutes

### Option 1: Automated Quick Start

```bash
# 1. Activate the environment
conda activate SEEK

# 2. Run the quick start script
python quick_start.py
```

The quick start script will guide you through:
- System tests
- Database initialization  
- Starting the web UI or terminal app

### Option 2: Manual Step-by-Step

```bash
# 1. Test the system
python test_system.py

# 2. Initialize database
python init_database.py

# 3. Start the web UI
python ui.py
```

## Web UI Testing

### Starting the Web Interface

```bash
# Start the Flask application
python ui.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Testing the Web Interface

1. **Open Browser**: Navigate to http://localhost:5000

2. **Visual Check**: You should see:
   - Capitol building background image
   - "AyeSpy" title with logo
   - Search form with:
     - Politician name dropdown (autocomplete)
     - Issue search field  
     - Time range selector
     - Submit button

3. **Test Politician Search**:
   - Start typing in the politician name field
   - Should see autocomplete suggestions from legislators data
   - Try names like "Biden", "Pelosi", "McConnell"

4. **Test Issue Search**:
   - Enter topics like:
     - "healthcare"
     - "defense spending" 
     - "climate change"
     - "immigration"

5. **Test Time Filters**:
   - Select different time ranges:
     - Past 24 hours
     - Past week
     - Past month
     - Past year
     - All time

6. **Test Form Submission**:
   - Fill out the form and click Submit
   - Note: Backend processing may not be fully implemented yet

### Expected Behavior

✅ **Working Features**:
- Page loads with proper styling
- Politician dropdown shows names from legislators data
- Form accepts input in all fields
- Time range selector works
- Form submission processes (may show blank results)

⚠️ **Limited Features** (depending on database setup):
- Search results may be empty without processed embeddings
- Some politician names may not have associated data

## Terminal Application Testing

### Starting the Terminal App

```bash
# Start the Rich terminal interface
python main.py
```

### Main Menu Testing

You should see a colorful menu with options:
```
🏛️  AyeSpy - Congressional Transparency Platform
============================================

MAIN MENU
========================================

1. 🔍 Search Transcripts
2. 📋 Track Bills  
3. 🗳️  View Voting History
4. 📊 View Recent Updates
5. 🔄 Sync Data
6. ⚙️  System Status
7. ❓ Help
8. 🚪 Exit
```

### Test Each Menu Option

#### 1. 🔍 Search Transcripts
- Enter a search query like "national security"
- Try filtering by representative name
- Test different result limits (10, 20, 50)
- Check similarity scores in results

#### 2. 📋 Track Bills
- Try searching for bills by keyword
- Test bill lifecycle viewing
- Check bill status tracking

#### 3. 🗳️ Voting History  
- Search for representative voting records
- View bill vote results
- Analyze party voting patterns

#### 4. 📊 View Recent Updates
- Check for recent congressional activity
- View new bills, hearings, votes

#### 5. 🔄 Sync Data
- Test data synchronization (if API keys configured)
- Monitor sync progress and results

#### 6. ⚙️ System Status
**This is most important for testing!**
- Check database connectivity
- Verify API connections
- Confirm AI service status
- View embedding model information

#### 7. ❓ Help
- Review help documentation
- Check feature descriptions

### Expected Terminal Behavior

✅ **Should Work**:
- Rich colorful interface displays properly
- Menu navigation works
- System status shows component health
- Help system provides information

⚠️ **May Have Limited Data**:
- Search results depend on database content
- Bill tracking requires API data
- Voting history needs congressional vote data

## System Status Validation

### Database Health Check

```bash
# Test database connection
python -c "
import postgres_utils
conn = postgres_utils.connect('seek', 'seek_user', 'secret', 'localhost')
print('✅ Database connected!' if conn else '❌ Database connection failed')
"
```

### AI Model Check

```bash
# Test AI model loading
python -c "
from transformers import BertTokenizer, BertModel
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
print('✅ AI models loaded successfully!')
"
```

### Data File Check

```bash
# Verify data files
ls -la congressional_hearings_test2.csv data/legislators-current.csv
```

## Sample Test Queries

### Web UI Test Queries
- **Politicians**: "Alexandria Ocasio-Cortez", "Ted Cruz", "Nancy Pelosi"
- **Issues**: "Climate change", "Healthcare reform", "National defense"
- **Time Ranges**: Try all available options

### Terminal Search Test Queries
- **Defense**: "military spending", "national security", "defense budget"
- **Healthcare**: "medicare", "healthcare reform", "medical costs"
- **Economy**: "inflation", "jobs", "economic growth"
- **Environment**: "climate change", "renewable energy", "environmental protection"

## Troubleshooting Common Issues

### Port Already in Use
```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process or use different port
FLASK_RUN_PORT=5001 python ui.py
```

### Database Connection Issues
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list postgresql     # macOS

# Test manual connection
psql -h localhost -U seek_user -d seek
```

### Import Errors
```bash
# Reinstall dependencies
pip install --force-reinstall flask sqlalchemy transformers

# Check Python path
python -c "import sys; print(sys.path)"
```

### Memory Issues
```bash
# Monitor memory usage during AI model loading
free -h  # Linux
top      # macOS/Linux

# Use CPU-only if GPU memory insufficient
export CUDA_VISIBLE_DEVICES=""
```

## Success Criteria

### ✅ Web UI Success
- [ ] Page loads at http://localhost:5000
- [ ] Form elements are functional
- [ ] Politician dropdown shows names
- [ ] Form submission works (even if results are empty)
- [ ] No JavaScript errors in browser console

### ✅ Terminal App Success  
- [ ] Rich interface displays properly
- [ ] All menu options are accessible
- [ ] System status shows component health
- [ ] No Python import errors
- [ ] Graceful error handling

### ✅ Database Success
- [ ] PostgreSQL connection established
- [ ] Tables created successfully
- [ ] Sample data files accessible
- [ ] No connection timeout errors

### ✅ AI Models Success
- [ ] BERT models load without errors
- [ ] Embedding generation works
- [ ] Model inference completes
- [ ] Memory usage is reasonable

## Next Steps After Testing

Once basic testing is complete:

1. **Load Real Data**: Use the API sync features to get current congressional data
2. **Configure APIs**: Add Congress.gov and GovInfo API keys for live data
3. **Performance Tuning**: Optimize database queries and AI model usage
4. **Custom Features**: Add new search filters, visualization, or data sources

## Getting Help

If you encounter issues:

1. **Check Logs**: Look for detailed error messages in terminal output
2. **System Test**: Run `python test_system.py` to identify problems
3. **Setup Guide**: Review `SETUP_INSTRUCTIONS.md` for detailed setup
4. **Component Test**: Test individual components (database, AI models, etc.)

The AyeSpy system is designed to be robust, but congressional data and AI models can be complex. Start with basic functionality and gradually add features as the system stabilizes.
