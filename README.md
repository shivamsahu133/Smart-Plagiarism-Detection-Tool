📖 Smart Plagiarism Detection Tool

Built a code plagiarism detector using AST, tokenization, and SequenceMatcher for Type 1 to 4 clone detection.  • Implemented function-level comparison with side-by-side code view to highlight similar logic across files.  • Added loop normalization and function name heuristics to enhance semantic similarity detection.  •
 
It provides a simple UI for uploading text, runs preprocessing (tokenization, stopword removal, TF-IDF, cosine similarity, etc.), and generates a plagiarism percentage report.

✨ Features

✅ User-Friendly UI – Clean and interactive interface powered by Streamlit.
✅ Text Preprocessing – Tokenization, stopwords removal, normalization.
✅ Similarity Detection – Uses TF-IDF vectorization + Cosine Similarity to compare text.
✅ Multiple Input Options – Paste text directly or upload documents.
✅ Visual Insights – Displays similarity percentage in easy-to-understand format.
✅ Lightweight & Fast – Runs directly in your browser, no complex setup required.

🛠️ Tech Stack

Frontend / UI: Streamlit

Programming Language: Python

NLP & ML:

scikit-learn → TF-IDF Vectorization, Cosine Similarity

NLTK / Tokenizer utils → text preprocessing

Other Libraries: Pandas, NumPy, Matplotlib

📂 Project Structure
Smart-Plagiarism-Detection-Tool/
│
├── app.py                     # Main Streamlit app
├── requirements.txt           # Dependencies
├── plagiarism/
│   ├── preprocess.py          # Text cleaning & preprocessing
│   ├── similarity.py          # Similarity calculation logic
│   ├── token_utils.py         # Tokenization utilities
│
├── .streamlit/
│   └── config.toml            # UI theme settings (default light mode)
│
└── README.md                  # Project documentation

🚀 Live Demo

👉 Smart Plagiarism Detection Tool (Streamlit App)

⚡ Installation & Setup
1. Clone the Repository
git clone https://github.com/shivamsahu133/Smart-Plagiarism-Detection-Tool.git
cd Smart-Plagiarism-Detection-Tool

2. Create Virtual Environment (Optional but Recommended)
python -m venv venv
source venv/bin/activate   # for Linux/Mac
venv\Scripts\activate      # for Windows

3. Install Dependencies
pip install -r requirements.txt

4. Run the App
streamlit run app.py

📊 How It Works

Input Text → User pastes or uploads text.

Preprocessing → Text is cleaned, tokenized, and converted to TF-IDF vectors.

Similarity Calculation → Cosine similarity between texts is computed.

Plagiarism Score → Percentage similarity is displayed in an interactive report.

📸 Screenshots

(Add screenshots of your app UI here once deployed — Streamlit input form + similarity output chart.)

🔮 Future Improvements

Support for PDF/DOCX file uploads.

Advanced NLP techniques (Word2Vec, BERT embeddings) for semantic similarity.

Plagiarism detection against online databases.

Multi-language support.

🤝 Contributing

Contributions are welcome! 🎉

Fork the repo

Create a new branch (feature-new)

Commit changes and open a Pull Request

📜 License

This project is licensed under the MIT License – you are free to use, modify, and distribute it with attribution.

👨‍💻 Author

Shivam Kumar Sahu

GitHub: shivamsahu133

LinkedIn: (add your profile link here)
