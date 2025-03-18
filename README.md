# ATEEZ-Backup-Dancer

## Backup Automation System
## Overview
This project is a fully automated backup system that allows you to configure and execute various backup jobs, including file synchronization, snapshot creation, and reporting. The system logs job execution details, generates reports in HTML format, and optionally sends summary emails.

## Features
- **Automated Backups**: Supports file synchronization using `rsync` and snapshot creation with 7-Zip.
- **Job Scheduling**: Define and execute multiple backup jobs with customizable configurations.
- **Logging System**: Logs can be printed to the terminal, written to a file, or both.
- **HTML Reports**: Generates an overview of executed jobs with job details.
- **Email Notifications**: Optionally send job reports via email.
- **Database Storage**: Uses SQLite to store job execution history.

## Setup Instructions
### 1. Initialize the Database
Before running the system for the first time, initialize the SQLite database by executing:
```bash
python InitDB.py
```
This will create the necessary database structure for job logging.

### 2. Deploy HTML Documents
Move all files from the `HTMLDocuments` folder to the target directory where the generated HTML report will be stored. This path is specified in the standard report job configuration.

### 3. Configure Logging Settings
Adjust the logging settings in `Config.ini` under the `[LOGGING]` section. You can enable or disable terminal output, file logging, and debugging features as needed.

### 4. Configure Backup Jobs
Navigate to the `Jobs` folder and configure the `.job` files:
- Each job file corresponds to a specific backup type.
- To create a new job, duplicate an existing `.job` file, modify the settings inside, and rename it.
- The job filenames must follow this naming convention:
  ```
  00-jobname.job
  ```
    - The **two-digit prefix** determines the execution order.
    - The **job name** can be freely chosen.

### 5. Run the System
Once the configurations are complete, start the main script:
```bash
python main.py
```
This will execute all configured jobs in the specified order.

## Notes
- Ensure all required dependencies are installed before running the system.
- The system is designed to be modular, allowing additional job types to be added easily.
- Job execution details will be stored in the SQLite database and can be accessed via the generated HTML reports.