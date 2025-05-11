# 🧳 Travel Assistant

**Travel Assistant** is a smart travel planning assistant that integrates data from multiple sources to suggest personalized trips, destinations, hotels, restaurants, and travel videos tailored to user preferences.

## 🧠 Key Features

- ✈️ Flight and hotel recommendations based on user preferences  
- 🎥 YouTube travel video integration for a richer experience  
- 📍 Smart destination suggestions via DuckDuckGo search  
- 📝 Automated travel summary generated from user input  
- 🗺️ Local insights and travel tips via conversational assistant

## 🛠️ Technical Stack

- **Frontend**: Streamlit  
- **Backend**: Flask  
- **Language Models**: Gemini 1.5  
- **Search**: DuckDuckGo API  
- **Web Data (Realtime, Datasets, Scraping)**: Playwright  
- **Browser Automation**: `browser_use` (`Agent`, `Browser`, `BrowserConfig`)  
- **YouTube Transcript Loader**: `YouTubeTranscriptApi`  

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file with necessary API keys and configurations:

```bash
cp sample.env .env
```

### 3. Initialize the Application

Start the backend server:

```bash
cd src/backend/config
python app.py
```

### 4. Run the Frontend

In a new terminal, start the frontend:

```bash
cd ../../frontend/frontend
streamlit run frontend.py
```

## 📌 Usage

### 📝 Enter Travel Details
Use natural language to describe your travel plan (flights & hotels).  
**Example**: "I want to travel to Bangkok from New York from July 1st to July 10th."

### ✈️ View Results
- Check flight options and pricing  
- Browse hotel recommendations based on your preferences  

### 🗺️ Get Local Insights
- Chat with the Research Assistant to discover local attractions  
- Learn about local customs, culture, and travel tips  

### 🎥 YouTube Review Search
- Enter a topic, location, or activity to search for related YouTube reviews  
- The system returns summarized video content and allows follow-up conversation

---