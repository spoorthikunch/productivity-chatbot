# 🧠 Personal Productivity Coach

A RAG-based chatbot that analyses your daily productivity 
logs and gives personalised suggestions to improve your habits.

## 🎯 What it does
- Log your daily screen time, sleep, exercise and mood
- Ask questions about your habits in natural language
- Get personalised suggestions based on YOUR actual data

## 🛠️ Tech Stack
- LangChain — RAG pipeline orchestration
- ChromaDB — Vector database for storing embeddings
- HuggingFace — Sentence embeddings (all-MiniLM-L6-v2)
- TinyLlama — Local LLM for generating answers
- Streamlit — Web application interface
- Python — Core language

## 🏗️ Architecture
```
User fills daily log form
        ↓
Saved to logs.txt
        ↓
RecursiveCharacterTextSplitter (chunk_size=300, overlap=50)
        ↓
HuggingFace Embeddings → ChromaDB vector store
        ↓
User asks question → similarity search → top 3 chunks retrieved
        ↓
ChatPromptTemplate → TinyLlama → personalised answer
```

## 🚀 How to run

### 1. Clone the repo
```bash
git clone https://github.com/spoorthikunch/productivity-chatbot.git
cd productivity-chatbot
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
streamlit run app.py
```

## 📱 How to use
1. Go to **Log Today** tab
2. Fill in your daily habits — screen time, apps, sleep, mood
3. Click Save
4. Go to **Chat** tab
5. Ask anything about your habits!

## 💡 Example questions
- "Which apps am I spending too much time on?"
- "How does my sleep affect my productivity?"
- "What was my best day and why?"
- "What should I do to improve my productivity?"

## 🔮 Future improvements
- Add OpenAI GPT for better answer quality
- Weekly summary report
- Habit streak tracking
- Export data as CSV

## 👩‍💻 Author
Spoorthi G Kunch
[LinkedIn](https://linkedin.com/in/spoorthikunch) | 
[GitHub](https://github.com/spoorthikunch)