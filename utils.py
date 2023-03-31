#!/usr/bin/env python3
"""Utility functions for the Google Careers Scraper."""
import json
from typing import List, Optional
from loguru import logger
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Disable logging for this module
logger.disable(__name__)

BASE_URL = "https://careers.google.com"
QUERY_URL = "/jobs/results/?q="

def get_page(url: str, driver: webdriver.Chrome) -> Optional[str]:
    """Get the HTML of the page.

    Args:
        url (str): The URL of the page.
        driver (webdriver.Chrome): The Selenium driver.

    Returns:
        Optional[str]: The HTML of the page.
    """

    logger.info("Getting page: {}", url)
    try:
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "gc-card__content"))
            )
        except Exception as error: # pylint: disable=broad-except
            logger.error("Error waiting for page: {}", error)
            return None
        return driver.page_source
    except Exception as error: # pylint: disable=broad-except
        logger.error("Error getting page: {}", error)
        return None

def get_job_links(page: str) -> List[str]:
    """Get the job links from the page.

    Args:
        page (str): The HTML of the page.

    Returns:
        List[str]: The job links.
    """

    logger.info("Getting job links")
    soup = BeautifulSoup(page, "html.parser")
    links = soup.find_all("a", class_="gc-card")
    return [{"name": link["aria-label"], "link": BASE_URL+link["href"]} for link in links]

def check_for_changes(links: List[str]) -> None:
    """Check for changes in the job listings.

    Args:
        links (List[str]): The job links.

    Returns:
        None: No return value.
    """

    logger.info("Checking for changes")
    with open("data/links.json", "r", encoding="utf-8") as file:
        old_links = json.load(file)

    # Check for new links
    changes = []
    for link in links:
        if link not in old_links:
            logger.info("New job posted: {}", link)
            changes.append({"link": link, "action": "added"})

    # Check for removed links
    for link in old_links:
        if link not in links:
            logger.info("Job posting removed: {}", link)
            changes.append({"link": link, "action": "removed"})
    return changes

def scrape(query: str, driver: webdriver.Chrome) -> Optional[List[str]]:
    """Scrape the Google Careers site for job listings.

    Args:
        query (str): The query to search for.
        driver (webdriver.Chrome): The Selenium driver.

    Returns:
        Optional[List[str]]: The job links.
    """

    # Get the page
    page = get_page(BASE_URL+QUERY_URL+query, driver)
    if page:
        # Get the job links
        links = get_job_links(page)
        logger.info("Found {} job links", len(links))
        for link in links:
            pretty = json.dumps(link, indent=4)
            logger.info("Found job link: {}", pretty)

        # Check for changes
        changes = check_for_changes(links)
    else:
        logger.error("No page found")

    # Close the driver
    driver.close()

    # Return links and changes
    return links, changes

def generate_changes_str(changes: List[str]) -> str:
    """Generate the changes string.

    Args:
        changes (List[str]): The changes.

    Returns:
        str: The changes string.
    """

    changes_str = ""
    for change in changes:
        name = change["link"]["name"]
        link = change["link"]["link"]
        # Strip the query from the link
        link = link.split("?")[0]
        changes_str += f"\n- {name}:\n" + \
                        f"  {link}\n"
    return changes_str

def generate_report(changes: List[str]) -> str:
    """Generate a report of the changes.

    Args:
        changes (List[str]): The changes.

    Returns:
        str: The report.
    """

    changes_str = "Changes found:\n"

    added = [change for change in changes if change["action"] == "added"]
    removed = [change for change in changes if change["action"] == "removed"]

    if added:
        changes_str += "\nAdded jobs:"
        changes_str += generate_changes_str(added)

    if removed:
        changes_str += "\nRemoved jobs:"
        changes_str += generate_changes_str(removed)

    return changes_str

if __name__ == "__main__":
    logger.error("This script is not meant to be run directly")
