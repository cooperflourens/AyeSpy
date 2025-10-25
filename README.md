# AyeSpy - Congressional Transparency Platform

AyeSpy is a comprehensive congressional transparency platform that provides semantic search of congressional transcripts, bill tracking, and voting history analysis. Built with modern Python technologies and designed for scalability.

## 🏗️ Architecture Overview

### Core Components

1. **Database Layer**: SQLite with SQLAlchemy ORM, designed for millions of records
2. **API Integration**: Congress.gov and GovInfo APIs for live congressional data
3. **AI Services**: Sentence Transformers for semantic search and transcript analysis
4. **Terminal Application**: Rich CLI interface for all functionality
5. **Scalable Backend**: Ready for web application deployment

### Data Models

- **Representatives**: Congressional members with party affiliation and district info
- **Committees**: Congressional committees and subcommittees
- **Bills**: Legislation with complete lifecycle tracking
- **Hearings**: Committee hearings with metadata
- **Transcripts**: Searchable segments with vector embeddings
- **Votes**: Representative voting records and patterns

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- 4GB+ RAM (for AI models)
- Internet connection for API access

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AyeSpy
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Get API keys** (optional for testing)
   - [Congress.gov API](https://api.congress.gov/)
   - [GovInfo API](https://www.govinfo.gov/developers)

### First Run

1. **Test the system**
   ```bash
   python test_system.py
   ```

2. **Run the main application**
   ```bash
   python main.py
   ```

## 🔍 Core Features

### 1. Transcript Search
- **Semantic Search**: Find quotes by concept, not just keywords
- **Advanced Filtering**: By representative, committee, date range
- **Context-Aware Results**: Full hearing and committee information
- **Speaker Identification**: Automatic speaker detection and attribution

### 2. Bill Tracking
- **Complete Lifecycle**: Track bills from introduction through final passage
- **Status Monitoring**: Every status change with timestamps
- **Sponsor Information**: Full representative details and party affiliation
- **Timeline Visualization**: Visual representation of bill progress

### 3. Voting History
- **Representative Records**: Complete voting history for each member
- **Bill Analysis**: How each representative voted on specific legislation
- **Party Patterns**: Analyze voting patterns by political party
- **Trend Analysis**: Historical voting behavior over time

## 🛠️ Technical Implementation

### Database Design
- **SQLite**: Lightweight, file-based database for development
- **Optimized Indexes**: Performance tuning for millions of records
- **Relationship Mapping**: Proper foreign keys and joins
- **Data Integrity**: Constraints and validation

### AI-Powered Search
- **Sentence Transformers**: State-of-the-art text embeddings
- **Cosine Similarity**: Fast similarity calculations
- **Batch Processing**: Efficient handling of large datasets
- **Fallback Mechanisms**: Graceful degradation if AI services fail

### API Integration
- **Rate Limiting**: Respectful API usage with automatic backoff
- **Error Handling**: Robust error handling and retry logic
- **Data Synchronization**: Automatic updates from congressional sources
- **Caching**: Intelligent caching to reduce API calls

## 📊 Data Sources

### Congress.gov API
- Bills and resolutions
- Representative information
- Voting records
- Committee data

### GovInfo API
- Congressional hearing transcripts
- Document metadata
- Hearing schedules
- Committee information

## 🔧 Configuration

### Environment Variables
```bash
# API Keys
CONGRESS_API_KEY=your_congress_api_key
GOVINFO_API_KEY=your_govinfo_api_key

# Database
DATABASE_URL=sqlite:///ayespy.db

# AI Settings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
SIMILARITY_THRESHOLD=0.3

# Update Intervals
BILL_UPDATE_INTERVAL_MINUTES=30
TRANSCRIPT_UPDATE_INTERVAL_HOURS=24
```

### Performance Tuning
- **Embedding Model**: Choose based on speed vs. accuracy trade-offs
- **Similarity Threshold**: Adjust for precision vs. recall
- **Batch Sizes**: Optimize for your hardware capabilities
- **Database Indexes**: Automatic optimization for common queries

## 📈 Usage Examples

### Search Transcripts
```python
from services.search_service import SearchService

# Find quotes about climate change
results = search_service.search_transcripts(
    query="climate change renewable energy",
    representative="Alexandria Ocasio-Cortez",
    committee="Energy and Commerce",
    max_results=20
)

for result in results:
    print(f"{result['speaker_name']}: {result['text'][:100]}...")
    print(f"Similarity: {result['similarity']:.3f}")
```

### Track Bills
```python
from services.bill_tracking_service import BillTrackingService

# Get bill lifecycle
lifecycle = bill_service.get_bill_lifecycle("HR1234")
for status in lifecycle['statuses']:
    print(f"{status['date']}: {status['status']}")
```

### Get Voting Records
```python
# Representative voting analysis
voting_service = VotingService(db_manager)
record = voting_service.get_representative_voting_record("AOC")
print(f"Votes: {record['total_votes']}")
print(f"Party Line: {record['party_line_percentage']:.1f}%")
```

## 🚀 Deployment

### Development
```bash
python main.py
```

### Production
```bash
# Set production environment
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@host/db

# Run with production server
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 🔮 Future Enhancements

### Advanced AI Features
- **Topic Modeling**: Automatic topic extraction from transcripts
- **Sentiment Analysis**: Emotional tone analysis of statements
- **Entity Recognition**: Automatic identification of people, places, organizations
- **Summarization**: AI-generated summaries of long transcripts

### Enhanced Search
- **Multi-Modal Search**: Include video and audio analysis
- **Federated Search**: Search across multiple data sources
- **Real-Time Updates**: Live transcript processing and indexing
- **Advanced Analytics**: Trend detection and predictive modeling

### Web Interface
- **React Frontend**: Modern, responsive web application
- **Real-Time Updates**: WebSocket integration for live data
- **Interactive Visualizations**: Charts and graphs for data exploration
- **User Accounts**: Personalized searches and saved queries

## 🧪 Testing

### Run Tests
```bash
# Basic system test
python test_system.py

# Database tests
python -m pytest tests/test_database.py

# Service tests
python -m pytest tests/test_services.py
```

### Test Coverage
- Database operations
- API integrations
- Search functionality
- Bill tracking
- Voting analysis

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run linting
black .
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

- **Documentation**: [Project Wiki](link-to-wiki)
- **Issues**: [GitHub Issues](link-to-issues)
- **Discussions**: [GitHub Discussions](link-to-discussions)
- **Email**: support@ayespy.org

## 🙏 Acknowledgments

- **Congress.gov**: For providing comprehensive legislative data
- **GovInfo**: For access to government documents and transcripts
- **Hugging Face**: For the sentence transformer models
- **SQLAlchemy**: For robust database operations
- **Rich**: For beautiful terminal interfaces

---

**Built with ❤️ for transparent democracy and accessible congressional information.**

*"The best way to predict the future is to create it." - Peter Drucker*