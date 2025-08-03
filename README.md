# 🏛️ Sovereign Fund Portfolio Manager

*AI-Powered Investment Analysis & Optimization Platform*

## 📋 Project Overview

The Sovereign Fund Portfolio Manager is a comprehensive portfolio management system designed to analyze, monitor, and optimize sovereign wealth fund investments. Built with modern web technologies and AI capabilities, it provides institutional-grade portfolio analytics through an intuitive dashboard interface.

This project implements portfolio management principles from the **CFA Institute Investment Series**, specifically following guidelines from:
- CFA Level 1 2025 - Volume 09 - Portfolio Management
- CFA Institute Portfolio Management (Investment Series)

The system processes multi-sheet Excel portfolio data and provides AI-powered insights, recommendations, and interactive analysis capabilities.

## 🏗️ Project Architecture

### Backend-Frontend Separation

The project follows a clean separation of concerns with distinct backend and frontend layers:

```
portfolio-manager/
├── backend/                    # Core business logic and 
│   ├── __init__.py
│   ├── ai_engine.py           # Google Gemini AI integration
│   ├── data_processor.py      # Excel data processing and 
│   └── vector_store.py        # FAISS vector store for 
│
├── frontend/                   # User interface and 
│   ├── __init__.py
│   ├── app.py                 # Main Streamlit application
│   ├── components.py          # UI components and 
│   └── utils.py               # Frontend utilities and 
│
├── docker-compose.yml         # Docker orchestration
├── Dockerfile                 # Container definition
├── requirements.txt           # Python dependencies
├── .env                       # Environment configuration
└── SovereignFund_Portfolio.xlsx  # Sample portfolio data
```

### Backend Components

#### 1. **AI Engine** (`ai_engine.py`)
- **Google Gemini Integration**: Uses Gemini 1.5 Flash for portfolio analysis
- **Portfolio Analysis**: Comprehensive risk assessment and performance evaluation
- **Investment Recommendations**: AI-generated optimization suggestions
- **Interactive Chat**: Natural language queries about portfolio data
- **Vector Context**: Leverages vector store for contextual responses

#### 2. **Data Processor** (`data_processor.py`)
- **Excel Processing**: Handles multi-sheet portfolio files
- **Metrics Calculation**: Computes performance, risk, and allocation metrics
- **Data Validation**: Ensures data integrity and completeness
- **Time Series Analysis**: Processes historical performance data

#### 3. **Vector Store** (`vector_store.py`)
- **FAISS Integration**: CPU-optimized vector similarity search
- **Portfolio Embeddings**: Creates numerical representations of portfolio states
- **Context Retrieval**: Finds similar historical periods for analysis
- **Metadata Management**: Stores and retrieves portfolio metadata

### Frontend Components

#### 1. **Main Application** (`app.py`)
- **Streamlit Framework**: Web-based dashboard interface
- **File Upload**: Excel portfolio data ingestion
- **Session Management**: Maintains application state
- **Tab Navigation**: Organized dashboard sections
- **API Integration**: Connects to backend services

#### 2. **UI Components** (`components.py`)
- **Interactive Charts**: Plotly-based visualizations
- **Performance Dashboards**: Real-time portfolio metrics
- **Holdings Analysis**: Asset allocation and sector breakdowns
- **Risk Visualizations**: VaR, beta, and risk metric displays
- **Chat Interface**: AI-powered portfolio Q&A

#### 3. **Utilities** (`utils.py`)
- **Data Formatting**: Currency, percentage, and number formatting
- **Custom Styling**: CSS styling for enhanced UI
- **Validation Logic**: Data completeness checks
- **Alert Generation**: Portfolio warning and notification system

## 🚀 Features

### 📊 Portfolio Analytics
- **Performance Metrics**: Returns, volatility, Sharpe ratio, maximum drawdown
- **Risk Assessment**: VaR, CVaR, beta, tracking error, concentration risk
- **Benchmark Comparison**: Portfolio vs. benchmark performance analysis
- **Historical Analysis**: Time series performance visualization

### 🎯 Holdings Management
- **Asset Allocation**: Sector, geographic, and ESG breakdowns
- **Top Holdings**: Detailed analysis of largest positions
- **Concentration Metrics**: Risk concentration and diversification analysis
- **ESG Integration**: Environmental, Social, Governance rating analysis

### 🤖 AI-Powered Insights
- **Portfolio Analysis**: Comprehensive AI-driven portfolio evaluation
- **Investment Recommendations**: Actionable optimization suggestions
- **Interactive Chat**: Natural language portfolio queries
- **Context-Aware Responses**: Leverages historical data for insights

### 📈 Visualization
- **Interactive Charts**: Dynamic Plotly visualizations
- **Real-time Updates**: Live data refresh capabilities
- **Multi-dimensional Analysis**: Performance, risk, and allocation views
- **Export Capabilities**: Report generation and data export

## 🔧 Installation & Setup

### Prerequisites
- Python 3.12+
- Docker (optional)
- Google Gemini API Key

### Code Setup

1. **Clone the repository**
```bash
git clone https://github.com/PratikshaChavan-09/Sovereign-Portfolio-AI.git
cd Sovereign-Portfolio-AI
```

## 🏃‍♂️ Running the Application

### Option 1: Docker (Recommended)

**Start with Docker Compose:**
```bash
# Build and run the application
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

**Manual Docker Build:**
```bash
# Build the image
docker build -t portfolio-manager .

# Run the container
docker run -p 8501:8501 --env-file .env portfolio-manager
```

The application will be available at: `http://localhost:8501`

### Option 2: Local Development

**Install dependencies:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

**To run the app:**
```bash
# Run the application
streamlit run frontend/app.py --server.port=8501
```

## 📊 Portfolio Data Format

The system expects a multi-sheet Excel file with the following structure based on **CFA Institute Portfolio Management** standards:

### Required Sheets:

1. **Portfolio_Overview**
   - Fund metadata, AUM, target returns, risk levels
   - Inception date, benchmark information

2. **Holdings_Detail**
   - Individual asset holdings with weights and values
   - Sector classification, ESG ratings, geographic allocation

3. **Historical_Performance**
   - Time series performance data
   - Returns, volatility, Sharpe ratios over time

4. **Benchmarks**
   - Benchmark performance data for comparison
   - Market indices and peer group data

5. **Risk_Metrics**
   - VaR, CVaR, beta calculations
   - Risk attribution and concentration metrics

6. **Cash_Flows**
   - Transaction history and cash flow data
   - Subscription and redemption records

7. **Market_Data**
   - External market indicators
   - Economic and market environment data

### Sample Data

Use the provided `SovereignFund_Portfolio.xlsx` file as a template. This file contains sample data structured according to CFA Institute guidelines for portfolio management and analysis.

## 💡 Usage Guide

### 1. **Upload Portfolio Data**
- Navigate to the sidebar
- Upload your Excel portfolio file
- Wait for data processing and validation

### 2. **Explore Dashboard**
- **Dashboard Tab**: Overview metrics and key performance indicators
- **Performance Tab**: Detailed performance and risk analysis
- **Holdings Tab**: Asset allocation and holdings breakdown
- **AI Recommendations Tab**: AI-generated insights and suggestions

### 3. **Interactive Analysis**
- Use the chat interface for natural language queries
- Ask questions like:
  - "What are the key risks in my portfolio?"
  - "How is my portfolio performing vs benchmark?"
  - "Which sectors should I consider reducing?"
  - "Explain my portfolio in detail with specific numbers"

### 4. **AI-Powered Insights**
- Review AI-generated portfolio analysis
- Examine investment recommendations with priority levels
- Implement suggested optimizations



## 🛠️ Technical Stack

- **Backend**: Python 3.12, Pandas, NumPy, FAISS
- **AI/ML**: Google Generative AI (Gemini 1.5 Flash)
- **Frontend**: Streamlit, Plotly
- **Data Processing**: OpenPyXL, Pandas
- **Deployment**: Docker, Docker Compose
- **Vector Storage**: FAISS (CPU optimized)

## 📚 Dependencies

```txt
# Core Data Processing
pandas==2.2.2
numpy==1.26.4
openpyxl==3.1.5

# Streamlit Frontend
streamlit==1.38.0
plotly==5.24.1

# AI/ML Dependencies
google-generativeai==0.8.4
faiss-cpu==1.9.0

# Utilities
python-dotenv==1.0.1
```

## 🔍 How It Works

### 1. **Data Ingestion**
- Upload Excel file through Streamlit interface
- Data processor validates and cleans the multi-sheet data
- Metrics calculation and portfolio summary generation

### 2. **AI Analysis**
- Portfolio data converted to vector embeddings
- Gemini AI analyzes portfolio health and performance
- Context-aware recommendations generated

### 3. **Interactive Dashboard**
- Real-time visualization of portfolio metrics
- Dynamic charts and tables for data exploration
- Responsive UI with custom styling

### 4. **Chat Interface**
- Natural language processing for portfolio queries
- Vector store provides relevant context
- AI generates specific, data-driven responses

## 🎯 Based on CFA Institute Standards

This project implements portfolio management concepts from:

- **CFA Level 1 2025 - Volume 09 - Portfolio Management**
  - Risk and return concepts
  - Portfolio construction principles
  - Asset allocation strategies

- **CFA Institute Portfolio Management (Investment Series)**
  - Modern portfolio theory implementation
  - Risk measurement and management
  - Performance evaluation standards


