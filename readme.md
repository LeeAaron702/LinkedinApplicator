# EasyApplyLinkedin Bot

The EasyApplyLinkedin Bot is a Python script designed to automate the process of applying for jobs on LinkedIn. By leveraging Selenium, the bot can interact with LinkedIn's web interface to search for jobs, apply filters, and automatically submit applications to jobs that match specified criteria. This bot is particularly useful for job seekers who want to maximize their applications without manually going through each job listing.

## Features

- Automated Job Search: Searches for jobs based on specified keywords and location.
- Easy Apply Filter: Filters job results to only show positions that support LinkedIn's "Easy Apply" feature.
- Automated Job Application: Automatically applies to jobs and logs application details.
- Two Modes of Operation:
  - Autonomous Mode: Operates with shorter wait times and fewer attempts for faster execution.
  - Human Mode: Operates with longer wait times, allowing human intervention during the application process.

## Requirements

- Python 3.6+
- Google Chrome
- ChromeDriver
- Selenium
- LinkedIn account

## Setup

### Install Dependencies

Ensure you have the required Python packages installed. Use pip to install Selenium:

``` pip install selenium ```

## ChromeDriver
ChromeDriver is necessary for Selenium to interact with the Chrome browser. Follow these steps to install ChromeDriver:

- Download ChromeDriver: Go to the ChromeDriver download page and download the version that matches your installed version of Google Chrome.
- Place ChromeDriver in a Known Directory: After downloading, extract the chromedriver executable and place it in a directory you can easily reference, such as C:\path\to\chromedriver.

## User Data Directory
To keep you logged in to LinkedIn and to avoid re-entering your credentials every time the script runs, configure Chrome to use a specific user data directory:

Find the User Data Directory:

- On Windows, the default user data directory is typically located at: C:\Users\<YourUsername>\AppData\Local\Google\Chrome\User Data\Default.
- On macOS, it is: /Users/<YourUsername>/Library/Application Support/Google/Chrome/Default.
- On Linux, it is: /home/<YourUsername>/.config/google-chrome/Default.
Update the Script:

Modify the initialize_webdriver method in the script to use your user data directory:

```
options.add_argument("user-data-dir=C:\\Users\\<YourUsername>\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
```

## Configuration File
Create a config.json file in the same directory as the script. This file should contain your LinkedIn login details and job search preferences:


```
{
  "email": "your_email@example.com",
  "password": "your_password",
  "keywords": ["Software Engineer", "Data Scientist"],
  "location": "San Francisco, CA",
  "driver_path": "C:/path/to/chromedriver"
}
```

## Running the Script
The script can be run in two different modes: autonomous and human.

### Autonomous Mode
In this mode, the script will run with shorter wait times and fewer attempts for clicking the next/review buttons, optimizing for speed.


```
python easy_apply_linkedin.py autonomous
```

### Human Mode
In this mode, the script will run with longer wait times, allowing human intervention during the application process. This is useful if a human is present to fill in any required fields manually.

```
python easy_apply_linkedin.py human
```
## Script Details
### Initialization
The script begins by setting up the Chrome WebDriver and preparing a CSV file to log application details. The initialization process involves:

- WebDriver Setup: Configures the Chrome WebDriver with options such as specifying the user data directory, handling SSL errors, and keeping the browser window open after the script finishes.
- CSV Initialization: Checks if an applied_jobs.csv file exists; if not, creates it and writes the header row.
### Job Search
The bot navigates to LinkedIn's job search page and enters the specified keywords and location to search for jobs. The process involves:

- Navigating to LinkedIn Jobs: The bot opens the LinkedIn Jobs page.
- Entering Search Keywords: The bot enters the specified keywords into the search field.
- Entering Location: The bot enters the specified location into the location field and initiates the search.
### Easy Apply Filter
The bot applies the "Easy Apply" filter to narrow down job results to those that support the quick application process. This is done by:

- Locating and Clicking the Easy Apply Filter: The bot waits until the Easy Apply filter button is clickable and then clicks it.

### Processing Job Listings
The bot iterates through the job listings, hovering over each job to trigger details, and then attempts to apply using the Easy Apply button. The steps include:

- Hovering Over Job Listings: The bot scrolls to and hovers over each job listing to reveal additional details.
- Extracting Job Information: The bot extracts the job title, company name, job location, and job description.
- Submitting Applications: The bot clicks the Easy Apply button and follows through the application process.


### Handling Submissions
Depending on the mode (autonomous or human), the bot handles the submission process differently:

- Autonomous Mode: Uses shorter wait times and fewer attempts before discarding an application.
- Human Mode: Uses longer wait times and more attempts, allowing a human to intervene and complete any necessary forms.

### Next/Review Button Handling
The script intelligently handles the Next and Review buttons during the application process:

- Next Button: The bot clicks the "Next" button to proceed to the next step of the application. This is particularly useful for multi-step application forms.
- Review Button: The bot clicks the "Review" button to review the application before submitting. This step ensures that all required fields are filled correctly.

In Autonomous Mode, the script has shorter wait times between clicks and fewer total attempts (e.g., 5 attempts). This mode prioritizes speed and automation.

In Human Mode, the script has longer wait times (static 15 seconds) and more total attempts (e.g., 10 attempts). This mode allows a human user to fill in required fields between automated steps, providing flexibility for more complex application forms.

### Logging Applications
The bot logs the details of each application, including the company name, job title, job description, job ID, and the URL of the job posting, into a CSV file.

### Error Handling
The script includes comprehensive error handling to manage various scenarios, such as elements not being found or clickable, timeouts, and other exceptions. If no job results are found for a given keyword, the script will skip to the next keyword.

### Log Output
During execution, the script will print log messages to the console, detailing its actions and any errors encountered. These logs include timestamps and messages indicating the current operation or error.

Example log output:

```
2024-06-12 16:51:21 - Starting search for keyword: Software Engineer
2024-06-12 16:51:21 - Total results: 150
2024-06-12 16:51:26 - Processed 24 job listings on this page.
2024-06-12 16:51:33 - Next button clicked
2024-06-12 16:51:36 - Submit button found.
2024-06-12 16:51:36 - 🔥🔥🔥 Application submitted.
2024-06-12 16:51:38 - Closed the confirmation modal with 'Done' button.
```

### Next/Review Button Behavior
The script handles the Next and Review buttons based on the mode of operation:

- Autonomous Mode:
    - Shorter wait times between clicks.
    - Fewer total attempts (e.g., 5 attempts) before discarding the application.
Example:

```
2024-06-12 17:09:23 - Next button clicked
2024-06-12 17:09:27 - Next button clicked
2024-06-12 17:09:34 - Next button clicked
2024-06-12 17:09:40 - Next button clicked
2024-06-12 17:09:47 - Next button clicked
```
- Human Mode:
    - Longer wait times (static 15 seconds) between clicks.
    - More total attempts (e.g., 10 attempts), allowing human intervention.
Example:

```
2024-06-12 17:11:16 - Next button clicked
2024-06-12 17:11:23 - Next button clicked
2024-06-12 17:11:30 - Review button clicked
2024-06-12 17:11:39 - Review button clicked
2024-06-12 17:11:44 - Review button clicked
2024-06-12 17:11:53 - Review button clicked
```

## Installation and Running Guide
### Install Python
Ensure Python 3.6 or higher is installed on your machine. 
https://www.python.org/downloads/

### Install Selenium
Install Selenium using pip:

```
pip install selenium
```
### Download ChromeDriver
Download the ChromeDriver that matches your version of Google Chrome.
https://getwebdriver.com/chromedriver#stable
Extract the chromedriver executable and place it in the driver directory in the project folder



### Configure User Data Directory
Locate your Chrome user data directory and update the initialize_webdriver method in the script to use this directory. This keeps you logged in to LinkedIn.

### Create Configuration File
Create a config.json file with your LinkedIn login details and job search preferences:

```
{
  "email": "your_email@example.com",
  "password": "your_password",
  "keywords": ["Software Engineer", "Data Scientist"],
  "location": "San Francisco, CA",
  "driver_path": "C:/path/to/chromedriver"
}
```

## Run the Script
### For autonomous mode:


```
python easy_apply_linkedin.py autonomous
```

### For human mode:


```
python easy_apply_linkedin.py human
```

### Contributions
Contributions are welcome! Feel free to open an issue or submit a pull request on GitHub.

### License
This project is licensed under the MIT License. See the LICENSE file for details.

## Disclaimer

Using automation tools to apply for jobs on LinkedIn may violate LinkedIn's terms of service. This script is intended for educational purposes only. By using this bot, you acknowledge that:

- The use of this script is at your own risk.
- I, the creator of this script, am not responsible for any actions taken by LinkedIn against your account, including but not limited to suspension or banning of your account.
- It is your responsibility to understand and comply with LinkedIn's terms of service.

Please use this tool responsibly and consider the potential consequences before running the script on your LinkedIn account.
