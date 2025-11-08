# alphastream

A scalable, cloud-native data pipeline for ingesting, processing, and serving real-time financial market data.

## Overview

This project aims to do the following:

- Ingest real-time market data form financial APIs
- Process and transform streaming data
- Store data efficiently for analytics
- Serve data via REST API
- Visualize insights through interactive dashboard

## Architecture (Work in progress)

```
┌─────────────────┐
│  Market Data    │
│      API        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Ingestion     │
│    Service      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Kafka/      │
│    Kinesis      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Processing    │
│    Service      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────┐
│   PostgreSQL    │────▶│   FastAPI   │
│   TimescaleDB   │     └──────┬──────┘
└─────────────────┘            │
                               ▼
                        ┌─────────────┐
                        │  Dashboard  │
                        └─────────────┘
```

## Tech Stack

**Infrastructure & Cloud:**
- AWS (S3, EC2/ECS, RDS) or GCP (Cloud Storage, Compute Engine, Cloud SQL)
- Terraform for Infrastructure as Code
- Docker for containerization

**Data Pipeline:**
- Python 3.11+
- Apache Kafka / AWS Kinesis for streaming
- Apache Airflow for orchestration
- PostgreSQL / TimescaleDB for time-series data

**Application Layer:**
- FastAPI for REST API
- Streamlit for dashboard
- pytest for testing

**Data Source:**
- Alpha Vantage / Polygon.io / Yahoo Finance API

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- AWS/GCP account (free tier)
- API key from [Alpha Vantage](https://www.alphavantage.co/) (free)

### Local Setup
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/market-data-pipeline.git
cd market-data-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Running Locally
```bash
# Start infrastructure (Kafka, PostgreSQL)
docker-compose up -d

# Run ingestion service
python src/ingestion/main.py

# Run API server
uvicorn src.api.main:app --reload

# Run dashboard
streamlit run src/dashboard/app.py
```

## Features

### Phase 1: MVP (Current)
- [ ] Real-time data ingestion from market API
- [ ] Kafka/Kinesis streaming pipeline
- [ ] PostgreSQL/TimescaleDB storage
- [ ] Basic data transformations

### Phase 2: Core Features
- [ ] FastAPI REST endpoints
- [ ] Airflow orchestration
- [ ] Analytics queries (volatility, moving averages)
- [ ] Interactive dashboard

### Phase 3: Production Ready
- [ ] Comprehensive test suite
- [ ] Monitoring & alerting
- [ ] CI/CD pipeline
- [ ] Cloud deployment
- [ ] Performance optimization

## Performance Metrics

## Design Decisions

### Why Kafka over SQS?

### Why TimescaleDB?

## Testing
```bash
pytest tests/
```

## Future Improvements
- Real-time anomaly detection
- Multi-source data ingestion
- Machine learning for price prediction
- Advanced risk metrics

## Author
Me
- Email: sebastian.adm0@gmail.com

Built for fun

## License
MIT License