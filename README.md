# NLP Toolkit Application

This project is an NLP (Natural Language Processing) toolkit built with **pywebview**, **React**, and **TypeScript**. The application allows users to create, configure, and run NLP pipelines with various processing steps.

## Folder Structure

```plaintext
nlp-toolkit-app/
├── src/
│   ├── assets/                # Static assets for the application
│   ├── backend/               # Backend 
│   │   ├── storage/             # Static memory
│   │   │   └── pipelines/       # JSON files for each pipeline
│   │   └── Api.py               # Python API exposed to the frontend via pywebview
│   ├── frontend/              # Frontend 
│   │   ├── components/          # Reusable React components
│   │   └── screens/             # Screen components (LandingPage, PipelineConfigScreen, etc.)
│   ├── types/                 # TypeScript type definitions for the application
│   ├── utils/                 # 
│   │   └── pipelineApi.ts     # Functions to interact with the backend API
│   └── styles/                # SCSS files for global and component styles
├── index.html                 # The root html element
├── index.jsx                  # Mounts App to the root element
├── index.py                   # Starts pywebview (Main)
```
## Key Files
backend/Api.py: Contains the Python API functions (e.g., save_pipeline, load_pipeline) that the frontend calls through pywebview.
frontend/screens/: Holds main screens of the app, including LandingPage, PipelineConfigScreen, and ResultScreen.
types/: Contains TypeScript type definitions, including Pipeline and Step, to enforce consistent data handling.
utils/pipelineApi.ts: Functions for interacting with the backend API (loading, saving, listing pipelines).
main.py: Initializes the pywebview window and links the Api class to the frontend.
Running the Application
Install dependencies:

