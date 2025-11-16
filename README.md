FastAPI Forecast APIThis is a FastAPI application to manage clients, business units, and business verticals for a forecasting database.Project Structure.
├── .streamlit/
│   └── secrets.toml    # Your database credentials
├── fx_api.py           # The main FastAPI app, endpoints
├── crud.py             # Functions to Create, Read, Update, Delete data
├── schemas.py          # Pydantic models for data validation
├── database.py         # Database connection pool management
├── setup_database.py   # Script to initialize the database schema
├── streamlit_app.py    # The main Streamlit dashboard
├── pages/              # Directory for other Streamlit pages
│   ├── 1_Clients.py
│   ├── 2_Business_Structure.py
│   └── 3_Work_Types.py
└── README.md           # This file
How to Use1. Create Secrets FileCreate a file named .streamlit/secrets.toml in the same directory. Add your PostgreSQL credentials to it:[postgres]
host = "localhost"
port = "5432"
dbname = "your_db_name"
user = "your_username"
password = "your_password"
2. Install DependenciesYou'll need fastapi, uvicorn, the psycopg2 driver, pydantic, toml,requests, and streamlit.pip install fastapi "uvicorn[standard]" psycopg2-binary pydantic toml requests streamlit
3. Setup the DatabaseRun the setup script. This will connect to your database, drop any existing tables with the same names, create the new schema, and populate it with sample data.python setup_database.py
You should see output confirming the tables were created and data was inserted.4. Run the FastAPI Server (Terminal 1)In your first terminal, run the main application using uvicorn:uvicorn fx_api:app --reload
The --reload flag automatically re-loads the server when you make changes to the code.5. Run the Streamlit App (Terminal 2)In a second terminal, run the Streamlit application:streamlit run streamlit_app.py
Streamlit will open your browser and automatically detect the files in the pages/ directory to create a navigation menu.6. Access the API Docs (Optional)Once the server is running, open your browser and go to:https://www.google.com/search?q=http://127.0.0.1:8000/docsYou will see the interactive Swagger UI documentation. From here, you can test all the new API endpoints you just created!