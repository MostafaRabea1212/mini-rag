# mini-rag

This is a minimal implementation of the RAG model for question
answering.

## Requirements

- Python 3.12.10 or Later or lastet 
-  Visual Studio Code
- Jupyter Extension for Visual Studio Code

### 1. Install Python

Download and install Python 3.12.10 or later from the official Python website.

During the installation, make sure to enable:

- Add Python to PATH

After installation, open a terminal and verify the installation:

```powershell
python --version
```

You should see:

```text
Python 3.12.10
```

---
### 2. Install Visual Studio Code

Download and install Visual Studio Code.

After installation, open VS Code and open the project folder:

```text
mini-rag
```

You can open the project using:

```text
File → Open Folder
```

---

### 3. Create a Virtual Environment

This project uses Python's built-in `venv` module instead of Conda.

Open the VS Code terminal:

```text
Terminal → New Terminal
```

Make sure you are inside the project directory:

```text
F:\mini-rag-app
```

Create the virtual environment:

```powershell
python -m venv .mini-rag-app
```

This creates an isolated Python environment for the project:

```text
mini-rag/
└── .mini-rag-app/
```

---

### 4. Activate the Virtual Environment

On Windows PowerShell, run:

```powershell
.\.mini-rag-app\Scripts\Activate.ps1
```

After activation, you should see:

```text
(.mini-rag-app)
```

at the beginning of the terminal:

```text
(.mini-rag-app) PS F:\mini-rag-app>
```

This means that the virtual environment is active.

Verify the Python version:

```powershell
python --version
```

It should show:

```text
Python 3.12.10
```

---

### 5. Upgrade pip

With the virtual environment activated, upgrade `pip`:

```powershell
python -m pip install --upgrade pip
```

---

### 6. Install Jupyter Support

Install `ipykernel` inside the virtual environment:

```powershell
pip install ipykernel
```

`ipykernel` allows the virtual environment to be used as a Jupyter kernel.

---

### 7. Register the Environment as a Jupyter Kernel

Register the environment with Jupyter:

```powershell
python -m ipykernel install --user --name mini-rag-app --display-name "Python 3.12.10 (mini-rag-app)"
```

You should see a message similar to:

```text
Installed kernelspec mini-rag-app in ...
```

This makes the `mini-rag-app` environment available as a Jupyter kernel.

---

### 8. Install the Jupyter Extension in VS Code

Open the Extensions panel in VS Code and install:

```text
Jupyter
```

from Microsoft.

The Jupyter extension allows you to create and run `.ipynb` notebooks directly inside VS Code.

---

### 9. Select the Project Kernel

Open a Jupyter Notebook (`.ipynb`) in VS Code.

Click:

```text
Select Kernel
```

and select:

```text
Python 3.12.10 (mini-rag-app)
```

The notebook will now run using the project's virtual environment.

You can verify this by running:

```python
import sys

print(sys.version)
print(sys.executable)
```

The Python executable should point to:

```text
.mini-rag-app\Scripts\python.exe
```

At this point, the project environment is ready.

### (Optional) Setup you command line interface for better readability

```powershell
function prompt { "[$env:VIRTUAL_ENV_PROMPT] $((Get-Location).Path)`n> " }
```
## installation

### Install the required pachages

```powershell
pip install -r requirements.txt
```
### Setup the environment variables

```PowerShell
Copy-Item .env.example .env
```

Set your environment variables in the `.env` file. Like `OPENAI_API_KEY` value.
## Run the FastApi server
```PowerShell
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```
## POSTMAN Collection

Download the POSTMAN collection from [/assets/mini-rag-app.postman_collection.json](/assets/mini-rag-app.postman_collection.json)
