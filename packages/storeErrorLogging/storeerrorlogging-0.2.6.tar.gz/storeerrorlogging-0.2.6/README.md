
This module makes flask error reporting and normal error reporting get reported inside an sql database. It also provides a printt function that also saves statements to the database.  
**Database Structure:**  
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

**__init__(self, pathToDB = "../allData/errorLogging.db", includeStackForPrint = True, includeStackForError = True, saveEntireFileContentsAtStart=True, stackLimit = 20):**  
    pathToDB - path to database, by default it is "../allData/errorLogging.db".  
    includeStackForPrint - whether stack (functions leading to print statement) is saved. by default is True.  
    includeStackForError - whether stack (functions leading to error) is saved. by default is True.  
    saveEntireFileContentsAtStart - whether the entire file contents of the primary app file is saved or not.  
    stackLimit - limit of items in stack - by default is 20.  

**printt(self, args, flushIfPrinting=True, kwargs):**  
    functions like a normal print statement.  
    my observation is that print statements in flask often don't show unless you force it to flush to the system after each statement, so that is set to default true with this variable flushIfPrinting.   
