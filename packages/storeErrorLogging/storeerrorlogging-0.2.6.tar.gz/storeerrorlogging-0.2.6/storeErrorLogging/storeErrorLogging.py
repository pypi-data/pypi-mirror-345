
import logging
import traceback
import relativePathImport


from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime

class storeErrorLogging():
    '''
    This module makes flask error reporting and normal error reporting get reported inside an sql database. It also provides a printt function that also saves statements to the database. The database has this structure:
    
    table overall_run:
        overallRun_id - id associated with each time you run app.
        overallFileContent - optional; records entire file contents of main file for app.
        filePath - records full path to app file.
        timestamp - time stamp of when you started app.

    table log_entries:
        logEntry_id - id associated with a log entry.
        level - error level
        traceBack - optional; functions leading to call
        message - error message
        timestamp - time of error
        overallRun_id - links to overall_run table

    table print_entries:
        printEntry_id - id associated with print statement
        traceBack - optional; functions leading to call
        message - text printed
        timestamp - time of print statement
        overallRun_id - links to overall_run table
    
    error levels:
        Level Name	Constant	What it Means
        DEBUG - Detailed internal info (e.g., for devs)
        INFO - General operational messages
        WARNING - Something unexpected happened, not fatal
        ERROR - A serious problem that may affect behavior
        CRITICAL - A severe error that likely crashes stuff
    '''
    def _getStack(self):
        '''internal function to get stack of requests leading to error'''
        stack = traceback.extract_stack(limit=self.stackLimit)
        stack = [frame for frame in stack if "storeErrorLogging" not in frame.filename]
        stack_str = ''.join(traceback.format_list(stack))
        return stack_str
    
    def __init__(self, pathToDB = "../allData/errorLogging.db", includeStackForPrint = True, includeStackForError = True, saveEntireFileContentsAtStart=True, stackLimit = 20, debuggingLevelStored="DEBUG"):
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
            
            engine = create_engine('sqlite:///' + basedir) #logs.db')  # or use MySQL/PostgreSQL connection URI
            self.Base.metadata.create_all(engine)
            # self.Session = sessionmaker(bind=engine)
            
            # self.Session = scoped_session(sessionmaker(bind=engine))
            self.sessionMaker = scoped_session(sessionmaker(bind=engine))
            self.activeSession = self.sessionMaker()
        saveDatabase( pathToDB )

        def handleRecordingOverallRun(self):    
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

        
    
    def printt(self, *args, flushIfPrinting=True, **kwargs):
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
