# Language Learning Roleplay Chatbot Application

This is a Roleplay Chatbot application built using a React front-end and a FastAPI back-end. The chatbot is designed to engage in roleplay scenarios and assist users in completing a set of predefined tasks related to the selected scenario. The application makes use of the OpenAI API to generate scenario content and provide real-time chat interactions.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
  - [Setting Up the API Server](#setting-up-the-api-server)
  - [Setting Up the Frontend Client](#setting-up-the-frontend-client)
- [Environment Variables](#environment-variables)
- [Application Structure](#application-structure)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

## Prerequisites
To run this project, ensure you have the following software installed on your local machine:
- Python 3.8+
- Node.js (version 14+)
- npm (Node Package Manager)
- OpenAI API Key

## Installation

### 1. Clone the Repository
Clone the repository to your local machine:

```bash
git clone https://github.com/franua/language-learning-role-play-chat-bot
cd language-learning-role-play-chat-bot
```

### 2. Set Up the Backend (FastAPI Server)
Navigate to the `api/` folder and set up the Python environment.

#### Using Conda
```bash
conda env create -f conda_env.yml
conda activate language-learning-role-play-chat-bot
```

#### Venv and Pip (not tested!)
1. Install virtualenv (if not installed):
```bash
pip install virtualenv
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

4. Install the necessary dependencies:
```bash
pip install -r requirements.txt
```

### 3. Set Up the Frontend (React Application)
Navigate to the `site/` folder and install the Node.js dependencies:

```bash
cd site
npm install
```

## Running the Application

### Setting Up the API Server
1. Go to the `api/` folder if not already there
2. Copy `.env.dist` file into the `.env`
3. Replace `your_openai_api_key` with your actual OpenAI API key. Ensure you have the appropriate access to the OpenAI models.
    ```bash
    OPENAI_API_KEY=your_openai_api_key
    OPENAI_MODEL=gpt-4
    ```

4. Start the FastAPI server:
   ```bash
   uvicorn server:app --reload
   ```

   By default, the server will run on `http://127.0.0.1:8000/`.

### Setting Up the Frontend Client
1. Navigate to the `site/` folder if not already there.
2. Copy `.env.dist` file into the `.env`
3. Update the `API_URL` environment variable or keep the default value `http://127.0.0.1:8000/`.
4. Start the React development server:
   ```bash
   npm start
   ```

   The frontend should now be running on `http://localhost:3000/`.

## Application Structure

### Backend
Located in the `api/` folder. The most important files are:
- **server.py**: Main FastAPI server file handling the scenario and chat endpoints.
- **data.py**: Pydantic Models, Templates for prompts and text parsing helper functions.
- **conda_env.yaml**: Environment configuration for `conda`.
- **requirements.txt**: Python libraries required for the backend server.

### Frontend
Located in the `site/` folder. The most important files are:
- **App.js**: Main React component responsible for rendering the chat UI.
- **App.css**: Styles for the chat application.

## Usage
1. Open the frontend in your browser at `http://localhost:3000/`.
2. The application will call API for the generated scenario and tasks and display them:
    - the scenario on the left panel
    - the tasks on the right panel
3. Use the chat box in the middle to interact with the AI based on the scenario.
4. Tasks accomplished during the Chat interaction will be marked as done by check boxes.

## Troubleshooting
### CORS Issues
If you encounter a CORS error, ensure that the `allow_origins` parameter in the `api/server.py` is set to match the URL where your frontend is running (e.g., `"http://localhost:3000"`).

### OpenAI API Errors
If the backend fails to generate responses, ensure that:
1. Your OpenAI API key is correctly set in the `.env` file.
2. The selected model (`OPENAI_MODEL`) is accessible with your API key.

### Port Conflicts
Make sure that no other applications are running on the same ports (`8000` for backend and `3000` for frontend).
