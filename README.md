# Job Application Tracker

A Python-based desktop application to manage and track job applications. This tool allows you to:
- Add, update, and delete job applications.
- Visualize application statuses using a pie chart with a legend.
- Search applications by company, position, or status.
- Track rejection details, including interview and coding challenge stages.

## Features

- **Add Applications**: Track job applications by company, position, status, and date applied.
- **Update/Delete Applications**: Modify or remove existing entries.
- **Rejection Tracking**: Record details on interviews or coding challenges for rejected applications.
- **Search Functionality**: Search for applications by company name, position, or status.
- **Pie Chart Visualization**: View a pie chart that categorizes the current status of all applications.
- **Data Persistence**: Application data is stored in an SQLite database.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.6+**
- **pip** (Python's package installer)

## Installation

1. **Clone the repository** or download the source code.
    ```bash
    git clone https://github.com/your-username/job-application-tracker.git
    cd job-application-tracker
    ```

2. **Create a virtual environment** (optional, but recommended).
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3. **Install the required dependencies**.
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the application**.
    ```bash
    python application_tracker.py
    ```

## Usage

1. **Add Application**: Enter the company name, position, status, and date applied. For rejected applications, additional fields for rejection details will appear.
2. **Search**: Use the search field to filter applications by company, position, or status.
3. **Visualization**: Click the "Visualize Data" button to see a pie chart of your application statuses.
4. **Data Persistence**: All application data is stored in an `applications.db` SQLite database.

## Requirements

- **Python 3.6+**
- **Tkinter** (included with standard Python installation)
- **Matplotlib** (for pie chart visualization)
- **SQLite3** (for database storage)

## License

This project is licensed under the MIT License.
