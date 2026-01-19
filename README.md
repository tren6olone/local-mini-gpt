# Local Mini GPT 🧠

A modern, local chat interface built with **Streamlit** and **Ollama**. It features dynamic model switching and a specialized UI for visualizing the "thinking process" of reasoning models like DeepSeek-R1.

## Prerequisites

Before running the application, ensure you have the following:

- **Python 3.10+** installed.
- **[Ollama](https://ollama.com/)** installed and running in the background.
- At least one model pulled (DeepSeek-R1 is recommended for the full experience):

```bash
ollama pull deepseek-r1
```

## Installation

1. **Clone the repository:**

   ```bash
   git clone <your-repository-url>
   cd <repository-name>
   ```

2. **Create a virtual environment (Recommended):**

   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment:**

   - **Windows:**
     ```powershell
     .venv\Scripts\activate
     ```
   - **Mac/Linux:**
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Ensure the **Ollama** app is running in the background.
2. Run the Streamlit app:

   ```bash
   streamlit run app.py
   ```

3. Open your browser to the URL shown (usually `http://localhost:8501`).
4. Select a model from the sidebar and start chatting!

## Features

- **🔍 Auto-Detection:** Automatically finds and lists all models installed in your local Ollama instance.
- **💭 Thinking UI:** Special handling for reasoning models (like DeepSeek-R1) to show/hide their internal thought process.
- **💾 Persistent Chat:** Maintains conversation history within the active session.
- **🎨 Modern Design:** Clean interface with sidebar controls and responsive layout.
