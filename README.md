# NLP Toolkit Application

This project is an NLP (Natural Language Processing) toolkit built with **pywebview**, **React**, and **TypeScript**. The application allows users to create, configure, and run NLP pipelines with various processing steps.

## Folder Structure

```plaintext
nlp-toolkit-app/
├── src/
│   ├── assets/               # Static assets for the application (icons, images, etc.)
│   ├── backend/              # Backend Python code
│   │   ├── operations/         # Individual NLP operation modules (e.g., tokenization, stemming)
│   │   ├── run/                # Logic related to pipeline execution
│   │   ├── storage/            # Backend storage handling (may include caching or configurations)
│   │   ├── tests/              # Backend test suites
│   │   └── transferObjects/    # Data Transfer Objects and backend API
│   │   ├── Api.py            # Python API exposed to the frontend via pywebview
│   │   ├── generaltypes.py   # General type definitions shared within backend
│   │   ├── parameterTypes.py # Parameter definitions for operations
│   │   ├── register.py       # Logic to register operations/pipelines and link configs to their operation code.
│   │   └── utils.py          # Backend utility functions
│   ├── frontend/              # Frontend React/TypeScript application
│   │   ├── components/          # Reusable UI components
│   │   ├── screens/             # High-level screens (LandingPage, PipelineConfigScreen, etc.)
│   │   ├── styles/              # SCSS files for styling
│   │   ├── types/               # TypeScript type definitions (e.g. Pipeline, Step)
│   │   └── utils/               # Frontend utilities (e.g., API interaction)
└── storage/                   # Top-level storage, may contain pipeline JSON files or persistent data
    ├── inputs/                 # Stored user inputs (CSV, TXT, typed-in text)
    ├── pipelines/              # Definition Files for Pipelines (which steps, which configuration).
    ├── runs/                   # Stores single runs with unique ids and outputs. 
    └── steps/                  # Definition Files for Steps/Operations. Will be linked to a python operation class in register.py.
```

## Key Files
- src/backend/transferObjects/Api.py: Contains Python API functions (e.g., save_pipeline, load_pipeline), exposed to the frontend via pywebview.
- src/frontend/screens/: Contains main screens for the application:
  - LandingPage: Entry point for users.
  - PipelineConfigScreen: Configure and visualize your NLP pipelines.
  - ResultScreen: Display and analyze pipeline execution results.
- src/frontend/types/: TypeScript type definitions for ensuring consistent data handling throughout the application.
- src/frontend/utils/: Frontend utility functions, for example:
  - pipelineApi.ts (or similar) to load, save, and list pipelines via the backend API.
- main.py (if present at the root): Initializes the pywebview window and links the Api class to the frontend, enabling the frontend to call backend functions directly.

## Extendable design

The general design idea is to make (nlp) operations easily implementable in a way that the app renders it in a user-friendly GUI.
There are multiple ways you may extend this app:

- **Add Operations**:
  - This is the general use case. Add a new StepOperation Python class in backend/operations/ and a .json configuration in storage/steps and link them in backend/register.py
  - Start with the configuration:
    - Define Operation meta-data (name, id, description etc.)
    - First, you want to define which static parameters (configurable before run, i.e. settings) the user should specify and the input method (slider, text_field, list, ... (may also be extended in register.py))
    - Then define a input-output definition. This will say which inputs you expect in the payload and which outputs you will generate.
    - If an input is of a certain type (e.g. "tensor") you may define the type and its behavious in register.py
  - Then define the actual operation python code:
    - Operations receive a frontend notifier (for logs and status reports) and a payload object. All the data of previous steps may be loaded from the payload. The most important data object is payload.data
    - payload.data is a pandas dataframe representing the csv data the user provided and that has been modifier thus far in the pipeline
    - after your operation finished add a visualization object to the payload and output according status reports
  - For more information have a look on the operations that have already been implemented. You may also use ParallelizableTextOperation instead of StepOperation if your operation only need text as input.
      
- **Add new Visualization methods**
  - After a step has successfully run it's result is shown via a Visualization object that is mapped to a frontend React component
  - You may either define some custom HTML in the backend and use HTMLVisualization or define a new Visualization method
  - If you choose to do so, add both a new Visualization sub-class in the backend and link it to a new Visualization React component in the frontend
  
- **Add Data Fields and Data Pickers**
  - You may define your own data types and the parsing therof in register.py
  - You may also define custom data pickers. For this register a data picker in register.py and map it to an according frontend picker class in DynamicPicker.tsx


## Getting Started
### Install Dependencies:
Run pip install -r requirements.txt for Python dependencies and npm install for frontend dependencies.

### Run the Application:
Then, start the frontend with npm run start. The application should open with the React UI connected to the backend.

### Building the Frontend:
When ready to bundle for production, run npm run build to generate optimized frontend assets.
