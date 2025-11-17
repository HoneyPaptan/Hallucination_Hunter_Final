# 🧪 Hallucination Hunter

An AI-powered fact-checking tool that verifies claims and images using Google Gemini and real-time web search. It detects hallucinations, false information, and provides evidence-based verification.

## 🌟 Features

### Text Verification
- **Real-time fact-checking**: Verify any text claim against web evidence
- **Hallucination scoring**: Get a 0.0-1.0 score indicating accuracy
- **Detailed analysis**: See what's true, what's false, and why
- **Source citations**: View web sources used for verification

### Image Analysis
- **Image description**: AI describes what it sees in uploaded images
- **Claim verification**: Check if statements about images are true
- **Visual hallucination detection**: Identify false claims about images
- **Web cross-reference**: Search for additional context about image content

## 🛠️ How It Works

1. **User Input**: Enter a text claim or upload an image
2. **Web Search**: System searches Tavily for relevant evidence (up to 5 sources)
3. **AI Verification**: Gemini 2.0 analyzes the claim against evidence
4. **Scoring**: Assigns hallucination score based on accuracy
5. **Report**: Shows supported facts, false claims, and contradictions

## 📊 Hallucination Scoring

- **0.0 - 0.3**: ✅ Low risk - Claim is accurate
- **0.3 - 0.6**: ⚠️ Moderate risk - Some inaccuracies
- **0.6 - 1.0**: ❌ High risk - Claim is largely false

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key
- Tavily API key

### Clone and Install

```bash
# Clone the repository
git clone <your-repo-url>
cd hallucination_hunter

# Install dependencies
pip install streamlit google-genai tavily-python python-dotenv
```

### Environment Setup

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

**Where to get API keys:**
- **Gemini API Key**: Get it from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Tavily API Key**: Sign up at [Tavily.com](https://tavily.com/)

### Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 💡 Usage Examples

### Text Verification
```
Input: "Barack Obama was born in Kenya"
Result: Hallucination Score 0.9 (FALSE - He was born in Hawaii)
```

### Image Analysis
```
Upload: Photo of Eiffel Tower
Claim: "This shows the Eiffel Tower in London"
Result: FALSE - The Eiffel Tower is in Paris, France
```

## 🔧 Tech Stack

- **Streamlit**: Web interface
- **Google Gemini 2.0**: AI model for analysis and verification
- **Tavily**: Web search API for real-time evidence
- **Python**: Backend logic

## 📝 Project Structure

```
hallucination_hunter/
├── app.py              # Main application file
├── .env                # API keys (create this)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## ⚙️ Requirements

Create a `requirements.txt` file:

```txt
streamlit
google-genai
tavily-python
python-dotenv
```

Then install with:
```bash
pip install -r requirements.txt
```