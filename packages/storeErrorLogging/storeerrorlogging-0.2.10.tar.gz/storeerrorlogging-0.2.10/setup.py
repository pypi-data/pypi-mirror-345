
from setuptools import setup, find_packages
with open("README.md", "r") as fh: 
    long_description = fh.read() 

setup(
    name='storeErrorLogging',
    version='0.2.10',
    author='Brigham Turner',
    author_email='brighamturner@narratebay.com',
    description='''# 🧩 SQL-Based Error & Print Logging for Flask

This module enhances error tracking in Flask by logging both **Flask errors** and **standard Python errors** directly into an **SQLite database**, in addition to the terminal.

It also introduces a `printt()` function that logs printed messages to the database. This is useful because:

- Conventional `print()` statements often fail in background processes unless `.flush()` is called.
- However, calling `.flush()` can raise exceptions if the terminal is closed.
- `printt()` handles this cleanly and persistently logs messages.

### 🎯 Key Features

- ✅ Logs **Flask errors**, **standard exceptions**, and **custom print statements** to a database.
- 🧵 Includes full **stack trace** (if enabled) for debugging context.
- 🧠 Optionally saves the full content of the main `app.py` file and its path at each startup.
- 🎚 Customizable error **log level threshold** (e.g., only log `ERROR` and above).
- 🧰 Fully compatible with **Flask's logger**, **Werkzeug**, and the base `logging` module.

---

## 🗃️ Database Structure

The logging system uses three tables:

### 📄 `overall_run`

| Column             | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `overallRun_id`    | Unique ID for each execution of the app.                                    |
| `overallFileContent` | *(Optional)* Full contents of the main app file.                          |
| `filePath`         | Full file path to the app.                                                   |
| `timestamp`        | Time the app started.                                                        |

---

### 🐞 `log_entries`

| Column           | Description                                                           |
|------------------|-----------------------------------------------------------------------|
| `logEntry_id`    | Unique ID for each error log.                                         |
| `level`          | Error level (e.g., `ERROR`, `WARNING`).                               |
| `traceBack`      | *(Optional)* Stack trace leading to the error.                        |
| `message`        | Error message content.                                                |
| `timestamp`      | When the error occurred.                                              |
| `overallRun_id`  | Foreign key linking to the `overall_run` entry.                      |

---

### 🖨️ `print_entries`

| Column           | Description                                                            |
|------------------|------------------------------------------------------------------------|
| `printEntry_id`  | Unique ID for each printed message.                                     |
| `traceBack`      | *(Optional)* Stack trace leading to the print statement.               |
| `message`        | The printed content.                                                    |
| `timestamp`      | When the message was printed.                                           |
| `overallRun_id`  | Foreign key linking to the `overall_run` entry.                        |
''',
    long_description=long_description, 
    long_description_content_type="text/markdown", 

    url="https://github.com/brighamturner12/storeErrorLogging.git",
    project_urls={"Documentation": "https://github.com/brighamturner12/storeErrorLogging/blob/main/readme.md","Source Code": "https://github.com/brighamturner12/storeErrorLogging/blob/main/simpleDescription.md",},

    packages=find_packages(),
    install_requires=["sqlalchemy","sqlalchemy","sqlalchemy","relativePathImport"], 
    license="MIT",
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)