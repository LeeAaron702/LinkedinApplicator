import time
import re
import json
import random
import logging
import csv
import os
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException

class EasyApplyLinkedin:
    def __init__(self, data, mode):
        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        self.driver_path = data['driver_path']
        self.job_counter = 0
        self.mode = mode
        
        self.driver = self.initialize_webdriver()
        
        # Initialize CSV file if it doesn't exist
        if not os.path.exists('applied_jobs.csv'):
            with open('applied_jobs.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Date & Time", "Company", "Job Title", "Job Description", "Job ID", "URL"])

    def initialize_webdriver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("user-data-dir=C:\\Users\\Lee\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
        options.add_experimental_option("detach", True)
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-insecure-localhost')
        service = Service(self.driver_path)
        return webdriver.Chrome(service=service, options=options)

    def current_time(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def job_search(self, keyword):
        self.driver.get("https://www.linkedin.com/jobs/")
        self.enter_text("//input[@aria-label='Search by title, skill, or company']", keyword)
        self.random_wait()
        self.enter_text("//input[@aria-label='City, state, or zip code']", self.location + Keys.RETURN)
        self.random_wait()

    def enter_text(self, xpath, text):
        field = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        field.clear()
        field.send_keys(text)
        self.random_wait()

    def filter_easy_apply(self):
        try:
            easy_apply_button_xpath = "//button[@aria-label='Easy Apply filter.']"
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, easy_apply_button_xpath))).click()
            self.random_wait()
        except TimeoutException:
            print(f"{self.current_time()} - Failed to click on Easy Apply filter: TimeoutException - Easy Apply filter not found.")
            return False
        except NoSuchElementException:
            print(f"{self.current_time()} - Failed to click on Easy Apply filter: NoSuchElementException - Easy Apply filter not found.")
            return False
        except ElementNotInteractableException:
            print(f"{self.current_time()} - Failed to click on Easy Apply filter: ElementNotInteractableException - Easy Apply filter not clickable.")
            return False
        except Exception as e:
            print(f"{self.current_time()} - Failed to click on Easy Apply filter: {str(e)}")
            return False
        return True

    def find_offers(self):
        try:
            total_results_text = self.get_text(".display-flex.t-12.t-black--light.t-normal")
            total_results_int = int(re.sub(r'[^\d]', '', total_results_text))
            print(f"{self.current_time()} - Total results: {total_results_int}")

            jobs_processed = 0
            page_number = 1
            while jobs_processed < total_results_int:
                jobs_processed += self.process_page(total_results_int)
                page_number += 1
                if jobs_processed < total_results_int:
                    try:
                        self.navigate_to_next_page(page_number)
                    except TimeoutException:
                        print(f"{self.current_time()} - TimeoutException: No more pages to navigate.")
                        break
                else:
                    break
        except TimeoutException:
            print(f"{self.current_time()} - No job results found for this keyword.")
            return

    def get_text(self, selector):
        return WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector))).text

    def get_elements(self, selector):
        return WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))

    def hover_and_apply(self, result):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", result)
            hover = ActionChains(self.driver).move_to_element(result)
            hover.perform()
            # print(f"{self.current_time()} - Hovered over a job result")

            if result.is_displayed() and result.is_enabled():
                company = self.get_company()
                job_description = self.get_job_description()
                # job_description_preview = job_description[:50] if job_description else "No description available"
                try:
                    title = result.find_element(By.TAG_NAME, "strong")
                    
                    self.job_counter += 1
                    print(f"{self.current_time()} - #{self.job_counter}: Company: {company} ---- Job Title: {title.text}")
                    self.submit_apply(result, company, title.text, job_description)
                except NoSuchElementException:
                    print(f"{self.current_time()} - Job title element not found.")
                    self.random_wait()
                except Exception as e:
                    print(f"{self.current_time()} - Failed to process job title: {e}")
                    self.random_wait()
            else:
                print(f"{self.current_time()} - Job result is not visible or interactable: {result}")
        except ElementNotInteractableException as e:
            print(f"{self.current_time()} - Job result is not interactable: {e}")
        except Exception as e:
            print(f"{self.current_time()} - Error interacting with job result: {e}")

    
    def get_company(self):
        try:
            # Try to find the company name in the job details section
            try:
                # First attempt: using the specific div class
                company_element = self.driver.find_element(By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__company-name a")
            except NoSuchElementException:
                print(f"{self.current_time()} - Company element with .job-details-jobs-unified-top-card__company-name not found, trying alternative method.")

                # Second attempt: using the span within the div
                try:
                    company_element = self.driver.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__subtitle .job-card-container__primary-description")
                except NoSuchElementException:
                    print(f"{self.current_time()} - Company element with .job-card-container__primary-description not found, trying final method.")
                    
                    # Third attempt: alternative div with company name
                    company_element = self.driver.find_element(By.CSS_SELECTOR, ".display-flex.align-items-center.flex-1 a.app-aware-link")
            
            if company_element:
                company = company_element.text.strip()
                return company
            print(f"{self.current_time()} - Company element not found.")
            return None
        except NoSuchElementException:
            print(f"{self.current_time()} - Company element not found.")
            return None
        except Exception as e:
            print(f"{self.current_time()} - Failed to process company: {e}")
            return None
        
    def get_job_description(self):
        try:
            # Try to find the job description element using the specific class
            description_element = self.driver.find_element(By.CSS_SELECTOR, ".jobs-description-content__text")
            if description_element:
                job_description = description_element.text.strip()
                return job_description
            print(f"{self.current_time()} - Job description element not found.")
            return None
        except NoSuchElementException:
            print(f"{self.current_time()} - Job description element not found.")
            self.random_wait()
            return None
        except Exception as e:
            print(f"{self.current_time()} - Failed to process job description: {e}")
            self.random_wait()
            return None

    def process_page(self, total_results_int):
        job_index = 0
        processed_count = 0  # Variable to keep track of processed jobs
        while job_index < total_results_int:  # Assuming there are 24 jobs per page
            try:
                job_listings = self.get_elements("a.job-card-container__link.job-card-list__title.job-card-list__title--link")
                if job_index >= len(job_listings):
                    print(f"{self.current_time()} - Processed {job_index} job listings on this page.")
                    break

                job_listing = job_listings[job_index]
                self.hover_and_apply(job_listing)
                job_index += 1
                processed_count += 1  # Increment the processed count
            except Exception as e:
                print(f"{self.current_time()} - Error processing job listing #{job_index + 1}: {e}")
                self.random_wait()
                job_index += 1
        
        return processed_count

    def navigate_to_next_page(self, page_number):
        current_url = self.driver.current_url
        if "start=" in current_url:
            next_page_url = re.sub(r'start=\d+', f'start={(page_number - 1) * 25}', current_url)
        else:
            next_page_url = current_url + f"&start={(page_number - 1) * 25}"
        print(f"{self.current_time()} - Page Number: {page_number}")
        self.driver.get(next_page_url)
        self.random_wait()

    def submit_apply(self, job_add, company, job_title, job_description):
        # print(f"{self.current_time()} - You are applying to the position of: {job_add.text}")
        job_add.click()
        self.random_wait()

        try:
            easy_apply_button_xpath = "//button[contains(@class, 'jobs-apply-button') and contains(span, 'Easy Apply')]"
            easy_apply_button = WebDriverWait(self.driver, self.random_wait_time()).until(EC.element_to_be_clickable((By.XPATH, easy_apply_button_xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView();", easy_apply_button)
            easy_apply_button.click()
            
            # Get the current URL
            current_url = self.driver.current_url
            job_id = self.extract_job_id(current_url)
            
            self.handle_submission(company, job_title, job_description, job_id, current_url)
        except (NoSuchElementException, TimeoutException):
            print(f"{self.current_time()} - ❌ Easy Apply button not found, skipping job...")
            self.random_wait()
        except Exception as e:
            print(f"{self.current_time()} - Error clicking Easy Apply button: {e}")
            self.random_wait()

    def extract_job_id(self, url):
        match = re.search(r'currentJobId=(\d+)', url)
        if match:
            return match.group(1)
        return None

    def handle_submission(self, company, job_title, job_description, job_id, url):
        max_attempts = 6 if self.mode == 'human' else 10  # Max attempts adjusted based on mode
        click_count = 0
        while click_count < max_attempts:
            try:
                # Check if the submit button is present
                submit_button_xpath = "//button[@aria-label='Submit application']"
                submit_button = WebDriverWait(self.driver, self.random_wait_time()).until(
                    EC.presence_of_element_located((By.XPATH, submit_button_xpath))
                )
                if submit_button.is_displayed() and submit_button.is_enabled():
                    print(f"{self.current_time()} - Submit button found.")
                    submit_button.click()
                    print(f"{self.current_time()} - 🔥🔥🔥 Application submitted.")
                    self.random_wait()
                    
                    # Log application details to CSV
                    self.log_application(company, job_title, job_description, job_id, url)
                    
                    # Try to click 'Done' button if available
                    done_button_xpath = "//button[contains(@class, 'artdeco-button') and contains(@class, 'artdeco-button--primary') and contains(text(), 'Done')]"
                    try:
                        done_button = WebDriverWait(self.driver, self.random_wait_time()).until(
                            EC.element_to_be_clickable((By.XPATH, done_button_xpath))
                        )
                        done_button.click()
                        print(f"{self.current_time()} - Closed the confirmation modal with 'Done' button.")
                    except TimeoutException:
                        print(f"{self.current_time()} - 'Done' button not found, closing modal manually.")
                        self.close_modal()
                    break
                else:
                    self.click_next_button()
            except TimeoutException:
                self.click_next_button()
            except ElementNotInteractableException as e:
                print(f"{self.current_time()} - Submit button not interactable: {e}")
                self.close_modal()
                break
            except NoSuchElementException as e:
                print(f"{self.current_time()} - Submit button not found: {e}")
                self.close_modal()
                break
            except Exception as e:
                print(f"{self.current_time()} - An error occurred during submission: {e}")
                self.close_modal()
                break
            click_count += 1
        
        if click_count >= max_attempts:
            print(f"{self.current_time()} - Reached maximum attempts to click next/review buttons, closing modal.")
            self.close_modal()

    def click_next_button(self):
        # Click the Next or Review button
        try:
            next_button_xpath = "//button[@aria-label='Continue to next step' and contains(@class, 'artdeco-button--primary')]"
            review_button_xpath = "//button[@aria-label='Review your application' and contains(@class, 'artdeco-button--primary')]"
            next_buttons = self.driver.find_elements(By.XPATH, next_button_xpath)
            review_buttons = self.driver.find_elements(By.XPATH, review_button_xpath)
            
            if next_buttons:
                next_button = next_buttons[0]
                next_button.click()
                print(f"{self.current_time()} - Next button clicked")
            elif review_buttons:
                review_button = review_buttons[0]
                review_button.click()
                print(f"{self.current_time()} - Review button clicked")
            else:
                print(f"{self.current_time()} - Next or Review button not found, attempting to close modal.")
                self.close_modal()
            self.random_wait()
        except Exception as e:
            print(f"{self.current_time()} - Error clicking Next or Review button: {e}")
            self.close_modal()

    def close_modal(self):
        try:
            dismiss_button_xpath = "//button[@aria-label='Dismiss' and contains(@class, 'artdeco-modal__dismiss')]"
            dismiss_button = WebDriverWait(self.driver, self.random_wait_time()).until(
                EC.element_to_be_clickable((By.XPATH, dismiss_button_xpath))
            )
            dismiss_button.click()
            print(f"{self.current_time()} - Dismiss button clicked")
            self.random_wait()

            discard_button_xpath = "//button[@data-control-name='discard_application_confirm_btn' and contains(@class, 'artdeco-modal__confirm-dialog-btn')]"
            discard_button = WebDriverWait(self.driver, self.random_wait_time()).until(
                EC.element_to_be_clickable((By.XPATH, discard_button_xpath))
            )
            discard_button.click()
            print(f"{self.current_time()} - Discard button clicked")
            self.random_wait()
        except TimeoutException:
            print(f"{self.current_time()} - Timed out waiting for modal buttons")
        except Exception as e:
            print(f"{self.current_time()} - An error occurred while trying to close the modal: {e}")

    def random_wait(self):
        time.sleep(random.uniform(1, 4))

    def random_wait_time(self):
        return 15 if self.mode == 'human' else random.uniform(1, 5)

    def log_application(self, company, job_title, job_description, job_id, url):
        with open('applied_jobs.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([self.current_time(), company, job_title, job_description, job_id, url])

    def apply(self):
        past_time_seconds = 86400 # Variable for past time, currently set to past day

        for keyword in self.keywords:
            print(f"{self.current_time()} - 🟩🟩🟩 Starting search for keyword: {keyword}")
            self.job_search(keyword)
            time.sleep(2)

            if not self.filter_easy_apply():
                print(f"{self.current_time()} - 🟥🟥🟥🟥🟥🟥 Skipping keyword '{keyword}' due to missing Easy Apply filter.")
                continue

            time.sleep(2)

            # most recent 
            entry_and_associate_recent_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={self.location}&f_AL=true&f_E=2%2C3&f_WT=2&geoId=103644278&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&sortBy=DD"
            self.driver.get(entry_and_associate_recent_url)
            time.sleep(2)

            # Add past time filter to the URL
            past_time_recent_url = f"{entry_and_associate_recent_url}&f_TPR=r{past_time_seconds}"
            self.driver.get(past_time_recent_url)
            time.sleep(2)

            self.find_offers()
            print(f"{self.current_time()} - 🟥🟥🟥Completed search for keyword: {keyword}")
            print(f"{self.current_time()} - Waiting for 2 minutes before next search...")
            time.sleep(120)  # Wait for 2 minutes

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Apply to jobs on LinkedIn.')
    parser.add_argument('mode', choices=['autonomous', 'human'], help='Mode to run the script in: autonomous or human')
    args = parser.parse_args()

    with open('config.json') as config_file:
        data = json.load(config_file)

    bot = EasyApplyLinkedin(data, args.mode)
    bot.apply()
