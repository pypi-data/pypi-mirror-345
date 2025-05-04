
import logging
import traceback
import relativePathImport


from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime

class storeErrorLogging():
    '''
    ## 🧩 SQL-Based Error & Print Logging for Flask

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
    '''
    
    def __init__(self, pathToDB = "../allData/errorLogging.db", includeStackForPrint = True, includeStackForError = True, saveEntireFileContentsAtStart=True, stackLimit = 20, debuggingLevelStored="DEBUG"):
        '''
        ### `__init__(self, pathToDB="../allData/errorLogging.db", includeStackForPrint=True, includeStackForError=True, saveEntireFileContentsAtStart=True, stackLimit=20, debuggingLevelStored="DEBUG")`

        Initializes a persistent logging system that:
        - Mimics `print()` while storing messages and traceback information into a database.
        - Captures print statements and logged errors with optional Python stack traces.
        - Records the contents of the primary application file at startup.
        - Integrates with the Python `logging` module (including Flask/Werkzeug) and stores errors and critical logs in a SQL database.
        - Automatically manages SQLAlchemy session lifecycles to prevent connection issues over long runs.

        #### **Parameters:**

        - **`pathToDB`** (`str`, default: `"../allData/errorLogging.db"`):  
        Path to the SQLite database file where logs will be stored. You can change this to a different path or database engine URI.

        - **`includeStackForPrint`** (`bool`, default: `True`):  
        Whether to save a traceback (function stack) for each `printt()` call. If `True`, the stack is recorded up to `stackLimit` frames.

        - **`includeStackForError`** (`bool`, default: `True`):  
        Whether to save a traceback for errors and logs handled by the `logging` module (e.g., `logger.error(...)`).

        - **`saveEntireFileContentsAtStart`** (`bool`, default: `True`):  
        If `True`, saves the contents of the main script file into the database at startup for traceability and auditability.

        - **`stackLimit`** (`int`, default: `20`):  
        Number of stack frames to include when generating tracebacks. This applies to both printed and logged errors.

        - **`debuggingLevelStored`** (`str`, default: `"DEBUG"`):  
        The minimum logging level that will be stored in the database. Must be one of:  
        `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`.

        ---

        #### **How It Works:**

        - At initialization:
        - Creates SQLAlchemy table schemas for logging print and error entries.
        - Sets up a scoped session maker for thread-safe DB interaction.
        - Records the contents of the main Python script.
        - Registers a custom `logging.Handler` to insert error logs directly into the database.
        - Redirects Flask and Werkzeug logs to the same database handler.
        - Auto-recycles the SQLAlchemy session every ~10 commits to reduce risk of stale DB connections.

        ---

        #### **Database Tables Created:**

        - `overall_run`: Stores the main file content and file path at the beginning of each run.
        - `log_entries`: Stores errors or logs with traceback, log level, and message.
        - `print_entries`: Stores custom print-style logs (via `printt()`) with optional stack trace.

        ---

        #### **Example Usage:**

        ```python
        from your_logger_module import YourLoggerClass

        # Initialize the logger
        logger = YourLoggerClass(
            pathToDB="logs/my_app_logs.db",
            includeStackForPrint=True,
            includeStackForError=True,
            saveEntireFileContentsAtStart=True,
            stackLimit=15,
            debuggingLevelStored="WARNING"
        )

        # Example logging
        logger.printt("Initialization complete.")

        import logging
        logging.warning("This warning will be saved in the database.")
        ```

        ### Error Levels

        | Level Name | Constant           | Description                                              |
        |------------|--------------------|----------------------------------------------------------|
        | `DEBUG`    | `logging.DEBUG`    | Detailed internal info (e.g., for developers).           |
        | `INFO`     | `logging.INFO`     | General operational messages.                            |
        | `WARNING`  | `logging.WARNING`  | Something unexpected happened, but not fatal.            |
        | `ERROR`    | `logging.ERROR`    | A serious problem that may affect behavior.              |
        | `CRITICAL` | `logging.CRITICAL` | A severe error that likely causes the application to crash. |

        '''
        '''
        pathToDB - path to database, by default it is "../allData/terms.db".
        includeStackForPrint - whether stack (functions leading to print statement) is saved. by default is True.
        includeStackForError - whether stack (functions leading to error) is saved. by default is True.
        saveEntireFileContentsAtStart - whether the entire file contents of the primary app file is saved or not.
        stackLimit - limit of items in stack - by default is 20.
        '''
        self.numCommitsToSession = 0
        self.stackLimit = stackLimit
        self.includeStackForPrint = includeStackForPrint
        self.includeStackForError = includeStackForError
        self.saveEntireFileContentsAtStart = saveEntireFileContentsAtStart

        def saveDebuggingLevel():
            # DEBUG	logging.DEBUG	Detailed internal info (e.g., for devs)
            # INFO	logging.INFO	General operational messages
            # WARNING	logging.WARNING	Something unexpected happened, not fatal
            # ERROR	logging.ERROR	A serious problem that may affect behavior
            # CRITICAL	logging.CRITICAL	A severe error that likely crashes stuff
            
            assert debuggingLevelStored in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

            if debuggingLevelStored == "DEBUG":
                self.debuggingLevel = logging.DEBUG
            elif debuggingLevelStored == "INFO":
                self.debuggingLevel = logging.INFO
            elif debuggingLevelStored == "WARNING":
                self.debuggingLevel = logging.WARNING
            elif debuggingLevelStored == "ERROR":
                self.debuggingLevel = logging.ERROR
            elif debuggingLevelStored == "CRITICAL":
                self.debuggingLevel = logging.CRITICAL
            else:
                raise Exception("this should never happen because of assert debuggingLevelStored in statement")
        saveDebuggingLevel()
        
            


        def creatingBasicDataStructure():
            self.Base = declarative_base()

            class OverallRun(self.Base):
                __tablename__ = 'overall_run'
                overallRun_id = Column(Integer, primary_key=True)
                overallFileContent = Column(Text) # longer
                filePath = Column(String)
                timestamp = Column(DateTime, default=datetime.utcnow)
            self.OverallRun = OverallRun

            class LogEntry(self.Base):
                __tablename__ = 'log_entries'
                logEntry_id = Column(Integer, primary_key=True)
                
                level = Column(String)
                traceBack = Column(Text)
                message = Column(Text)
                
                timestamp = Column(DateTime, default=datetime.utcnow)
                overallRun_id = Column( Integer, ForeignKey('overall_run.overallRun_id') )
            self.LogEntry = LogEntry

            class PrintEntry(self.Base):
                __tablename__ = 'print_entries'
                printEntry_id = Column(Integer, primary_key=True)

                traceBack = Column(Text)
                message = Column(Text)

                timestamp = Column(DateTime, default=datetime.utcnow)
                overallRun_id = Column( Integer, ForeignKey('overall_run.overallRun_id') )
            self.PrintEntry = PrintEntry
        creatingBasicDataStructure()

        def saveDatabase( pathToDB ):
            # Change this line to match your database
            # basedir = relativeToAbsolute("../allData/terms.db")
            # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + basedir #os.path.join(basedir, 'terms.db')
            basedir = relativePathImport.relativeToAbsolute( pathToDB )
            print("path to error logging db:", basedir)
            
            engine = create_engine('sqlite:///' + basedir) #logs.db')  # or use MySQL/PostgreSQL connection URI
            self.Base.metadata.create_all(engine)
            # self.Session = sessionmaker(bind=engine)
            
            # self.Session = scoped_session(sessionmaker(bind=engine))
            self.sessionMaker = scoped_session(sessionmaker(bind=engine))
            self.activeSession = self.sessionMaker()
        saveDatabase( pathToDB )

        def handleRecordingOverallRun(): #self):    
            currentPath = relativePathImport.getCurrentFilePath()
            
            if self.saveEntireFileContentsAtStart:
                with open(currentPath, "r") as f:
                    overallFileContent = f.read()
            else:
                overallFileContent = "not included"
            
            # session = s#elf.Session()
            # overallRun_entry = self.OverallRun(
            #     overallFileContent = overallFileContent,
            #     filePath = currentPath,
            # )
            

            # session.add( overallRun_entry )
            # session.commit()
            # self.overallRunID = overallRun_entry.overallRun_id
            # session.close()

            overallRun_entry = self.OverallRun(
                overallFileContent = overallFileContent,
                filePath = currentPath,
            )            

            try:
                self.activeSession.add( overallRun_entry )
                self.activeSession.commit()
            except Exception:
                self.activeSession.rollback()

            self.overallRunID = overallRun_entry.overallRun_id
            
        handleRecordingOverallRun()
        
        def setup_logging():
            def getDBHandler():
                class DBLogHandler(logging.Handler):
                    def emit(inner_self, record):
                        try:
                            # session = self.Session()
                            # s#tack_str = ''.join(traceback.format_stack(limit=self.stackLimit))
                            if self.includeStackForError:
                                stackk = self._getStack()
                            else:
                                stackk = "not included"
                            log_entry = self.LogEntry(
                                level=record.levelname,
                                traceBack = stackk,
                                message=inner_self.format(record),
                                overallRun_id = self.overallRunID,
                            )
                            # session.add(log_entry)
                            # session.commit()
                            # session.close()

                            self.numCommitsToSession += 1
                            if self.numCommitsToSession % 10 == 5:
                                self.activeSession.add(log_entry)
                                self.activeSession.commit()
                                self.activeSession.close()
                                self.activeSession = self.sessionMaker()
                            else:
                                try:
                                    
                                    self.activeSession.add(log_entry)
                                    self.activeSession.commit()
                                except Exception:
                                    self.activeSession.rollback()

                        except Exception as e:
                            # Avoid recursive logging here
                            print("HUGE PROBLEM: Failed to log error to DB:", e)
            
                db_handler = DBLogHandler()

                # Only allow ERROR and CRITICAL logs to be stored in the database
                db_handler.setLevel(logging.ERROR)

                # Define a log message format: timestamp - level - message
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

                # Apply the formatter to the database handler
                db_handler.setFormatter(formatter)
                return db_handler
            db_handler = getDBHandler()
                
            def handleConventionalLogging(db_handler):
                # Get the root logger object (shared across all modules)
                logger = logging.getLogger()

                # Set the overall logging level for this logger.
                # Only messages at INFO level and above will be processed.
                logger.setLevel(self.debuggingLevel) #logging.INFO)

                # --- Console Logging ---
                if False: # this would theoretically put stuff on the console, but that should already be there.
                    # Create a logging handler that outputs to the console (stdout)
                    console = logging.StreamHandler()

                    # Set the logging level for console output to INFO and above
                    console.setLevel(self.debuggingLevel) #logging.INFO)

                    # Attach the console handler to the logger so messages appear in terminal
                    logger.addHandler(console)

                # --- Database Logging ---

                # Create a custom handler that writes logs to the database
                
                # Attach the database handler to the logger so it can save error logs
                logger.addHandler(db_handler)
            handleConventionalLogging(db_handler)

            def handleFlaskLogging(db_handler):
                flask_logger = logging.getLogger("flask.app")
                flask_logger.setLevel(self.debuggingLevel) #INFO)
                flask_logger.addHandler(db_handler)

                werkzeug_logger = logging.getLogger("werkzeug")
                werkzeug_logger.setLevel(self.debuggingLevel) #.INFO)
                werkzeug_logger.addHandler(db_handler)
            handleFlaskLogging(db_handler)
        setup_logging()

    def _getStack(self):
        '''
        Internal helper method that retrieves a filtered stack trace leading up to the point of error or logging.

        **Returns:**  
        A formatted string representation of the current Python call stack, excluding any frames that originate from the `storeErrorLogging` module (to reduce noise).

        **Behavior:**
        - Uses `traceback.extract_stack()` to retrieve the current call stack.
        - Filters out stack frames related to internal logging modules.
        - Formats the remaining stack into a readable string with `traceback.format_list()`.

        **Example:**
        ```python
        stack_str = self._getStack()
        print(stack_str)

        '''
        '''internal function to get stack of requests leading to error'''
        stack = traceback.extract_stack(limit=self.stackLimit)
        stack = [frame for frame in stack if "storeErrorLogging" not in frame.filename]
        stack_str = ''.join(traceback.format_list(stack))
        return stack_str
    
    def printt(self, *args, flushIfPrinting=True, **kwargs):
        '''
        ### `printt(*args, flushIfPrinting=True, **kwargs)`

        Functions like a normal `print()` statement, but also logs the message to a database for later review.

        **Parameters:**
        - `*args`: Any number of positional arguments to print and log.
        - `flushIfPrinting` (`bool`, default `True`): When `True`, forces `print()` to flush output immediately to stdout. This is helpful in environments like Flask where output is often buffered.
        - `**kwargs`: Additional keyword arguments passed to the built-in `print()` function.

        **Behavior:**
        - Joins all arguments into a single string and ensures UTF-8 safe encoding.
        - Optionally includes a traceback stack (based on `self.includeStackForPrint`) to help trace where the `printt()` call was made.
        - Logs this message and stack to a database via SQLAlchemy.
        - Every 10 log entries, the current SQLAlchemy session is closed and reopened to avoid keeping a stale session open.

        **Example:**
        ```python
        logger.printt("Processing user input:", user_input)
        ```
        '''
        '''
        functions like a normal print statement.
        my observation is that print statements in flask often don't show unless you force it to flush to the system after each statement, so that is set to default true with this variable flushIfPrinting.
        '''
        messageStr = ' '.join(str(arg) for arg in args)
        messageStr = messageStr.encode("utf-8", errors="replace").decode("utf-8")

        if self.includeStackForPrint:
            stackk = self._getStack()
        else:
            stackk = "not included"
        
        # session = self.Session()
        print_entry = self.PrintEntry(
            traceBack=stackk,
            message=messageStr,
            overallRun_id=self.overallRunID,
        )

        # session.add(print_entry)
        # session.commit()
        # session.close()

        self.numCommitsToSession += 1
        if self.numCommitsToSession % 10 == 5:
            self.activeSession.add(print_entry)
            self.activeSession.commit()
            self.activeSession.close()
            self.activeSession = self.sessionMaker()
        else:
            self.activeSession.add(print_entry)
            self.activeSession.commit()

        try:
            if flushIfPrinting:
                kwargs.setdefault("flush", True)
            print(*args, **kwargs)
        except:
            pass
    #############################################
    #############################################
    #############################################
