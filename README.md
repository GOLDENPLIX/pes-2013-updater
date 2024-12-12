# 🎮 PES 2013 Updater Bot

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Football Data API Key

### Installation
```bash
# Clone the repository
git clone https://github.com/GOLDENPLIX/pes-2013-updater.git

# Navigate to project directory
cd pes-2013-updater

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration
1. Obtain a Football Data API Key from [football-data.org](https://www.football-data.org/)
2. Create a `.env` file in the project root
3. Add your API key:
```
FOOTBALL_DATA_API_KEY=your_api_key_here
COMPETITIONS=PL,PD,BL1,SA,FL1
LOG_LEVEL=INFO
```

### Usage
```bash
# Run the updater
python pes_updater.py --update-transfers --download-assets

# Customize update options
python pes_updater.py --leagues PL,PD --update-database
```

## 🧪 Testing
```bash
# Run all tests
pytest

# Generate coverage report
pytest --cov=. --cov-report=html
```

## 🤝 Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🙌 Acknowledgments
- PESMaster Community
- Football-Data.org API
- Open Source Contributors

---

**Happy Gaming! ⚽🎮**
