# Student Financial Persona Predictor & Analysis Pipeline

This repository contains the machine learning pipeline and interactive offline web dashboard for predicting financial literacy and detecting financial behavior patterns among graduating students at Palawan State University.

## Setup & Installation

Follow these steps to clone the project, navigate to the correct directory, set up the isolated `venv` virtual environment, and install all dependencies.

### 1. Prepare Directory and Clone
Open your terminal, navigate to the folder where you want to store the project, and clone the repository:

```bash
# Navigate to your preferred workspace (e.g., your Documents or Projects folder)
cd path/to/your/workspace

# Clone the repository
git clone <GITHUB_REPOSITORY_URL>

# Enter the newly created project directory
cd <REPOSITORY_FOLDER_NAME>
```

### 2. Create the Virtual Environment
Ensure you are inside the project root folder (where `requirements.txt` is located). Run this command to create the isolated environment:

```bash
python -m venv tmvenv
```

### 3. Activate the Virtual Environment
You must activate the virtual environment every time you open a new terminal for this project.

**For Windows:**
```bash
tmvenv\Scripts\activate
```

**For macOS/Linux:**
```bash
source tmvenv/bin/activate
```

### 4. Install Dependencies
Once activated (you will see `(tmvenv)` at the beginning of your terminal prompt), install the required packages:

```bash
pip install -r requirements.txt
```

---

## 📊 Running the Analytics Pipeline

To explore the data engineering, clustering, and Random Forest modeling notebooks, launch Jupyter from the root directory:

```bash
jupyter notebook
```
*Note: Check your terminal output for the local URL (usually `http://localhost:8888/?token=...`) and open it in your browser.*

### ⚠️ Critical Developer Protocol: Committing Notebooks
Jupyter Notebooks store images and output data directly in their code files, which causes massive repository bloat. **Before running `git add` or committing any changes to a notebook, you MUST:**
1. Open the notebook in your browser.
2. Click **Kernel** -> **Restart & Clear Output**.
3. Save the notebook (`Ctrl + S`).
4. You may now safely commit the file.

---

## 🖥️ Running the Interactive Kiosk (Streamlit UI)

To launch the offline prediction dashboard (which automatically handles local SQLite database storage for institutional tracking), run this command from the project root:

```bash
streamlit run app.py
```