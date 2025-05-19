# RoadTrippy (Google ADK Project)

This project is built using the Google Agent Development Kit (ADK).
Currently, it can provide the current weather for a specified city.

## Project Structure

```
weather_agent/
├── __init__.py         # Makes the directory a Python package
├── agent.py            # Defines the main ADK agent and its tools
└── weather_service.py  # Handles communication with the OpenWeatherMap API
.env                    # Stores API keys (not in git)
README.md               # This file
```

## Setup

1.  **Prerequisites:**
    *   Python 3.9+ (preferably managed with a virtual environment tool like `venv` or `conda`).
    *   Google Agent Development Kit (`google-adk`). If not installed, refer to the [official ADK documentation](https://developers.google.com/agent-platform/adk/docs/overview) for installation instructions.

2.  **Clone the Repository:**
    ```bash
    # git clone <repository-url>
    # cd <repository-name>
    ```

3.  **Create and Activate a Virtual Environment:**
    It's highly recommended to use a virtual environment. If you used `adk new` to create the project, a virtual environment (e.g., `.adk1` or `.venv`) might have been set up for you.
    If not, you can create one:
    ```bash
    python3 -m venv .venv  # Or your preferred environment name
    source .venv/bin/activate # On macOS/Linux
    # .venv\Scripts\activate    # On Windows
    ```

4.  **Install Dependencies:**
    The primary dependencies are `google-adk` and `requests` for API calls, and `python-dotenv` for managing environment variables.
    
    ```bash
    pip install -r requirements.txt
    ```
    Otherwise, install them manually if needed (though `adk` usually handles its own dependencies):
    ```bash
    pip install requests python-dotenv
    ```

5.  **API Key Configuration:**
    This project requires an API key from OpenWeatherMap to fetch weather data.
    *   Go to [OpenWeatherMap](https://openweathermap.org/api) and sign up for a free API key if you don't have one.
    *   Create a file named `.env` in the root directory of the project.
    *   Add your API key to the `.env` file like this:
        ```env
        OPENWEATHERMAP_API_KEY=your_actual_openweathermap_api_key
        ```
        Replace `your_actual_openweathermap_api_key` with the key you obtained.
        The `.env` file is used by `python-dotenv` to load the API key into the environment when the agent runs. Ensure `.env` is listed in your `.gitignore` file to prevent committing your API key.

## Running the Agent

Once the setup is complete and the API key is configured:

1.  Navigate to the project's root directory.
2.  Ensure your virtual environment is activated.
3.  Run the agent using the ADK CLI:
    ```adk run```

This will start the agent, and you can interact with it through the ADK interface (usually a local web server or command-line chat).

## Example prompt
```How is the weather in London?```

