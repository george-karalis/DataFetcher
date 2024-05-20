from datetime import date, datetime

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from movingpicturesfetcher.elements import (
    ATTRIBUTES,
    IDS,
)


def tile_has_video(tile: WebElement) -> bool:
    """
    ## Finds if the Tile has a playable media.

    Parameters
    ----------
    tile
         The div containing the picture.

    Returns
    -------
        is the picture a video or not
    """
    is_video = tile.get_attribute(ATTRIBUTES["video_bool"])
    has_video = True if is_video == "true" else False
    return has_video


def tile_get_url(tile: WebElement) -> str | None:
    """
    ## Gets Moving Picture url using Tile.

    The URL can be part of an <a> tag inside the tile
    or be part of the ancestor <a> tag of the tile.

    Parameters
    ----------
    tile
        The tile with the moving picture's data

    Returns
    -------
        The tomato url of the moving picture
    """
    try:
        a_tag = tile.find_element(By.TAG_NAME, "a")
    except NoSuchElementException:
        a_tag = tile.find_element(By.XPATH, "./ancestor::a")
    mpic_url = a_tag.get_attribute("href")

    if mpic_url is None:
        # TODO: Add Rich Console
        print(f"No URL was found for tile: {tile}")

    return mpic_url


# TODO: Add clean date for TV_SERIES URL
def clean_date(date_str: str, date_format: str = "%b %d %Y") -> date:
    """
    ## Clean Date to Populate DB Field.

    ##The Scrapped date field from the Rotten Tomatoes website is not in an ideal
    format;
    date_str = 'Streaming May 10, 2024'u
    This function converts the above string to a datetime.date object

    Parameters
    ----------
    date_str
        Date from rotten tomatoes tile text
    date_format, optional
        datetime.date object to populate the DB., by default '%B %d %Y'

    Returns
    -------
        The date in a datetime.date format.
    """
    date_str = date_str.replace(",", "")
    date_list = date_str.split()[1:]
    date_str = " ".join(date_list)
    date = datetime.strptime(date_str, date_format).date()

    return date


def clean_score(score: str) -> int | None:
    """
    ## Converts scrap score text to int.

    Parameters
    ----------
    score
        Score as scrapped from the web

    Returns
    -------
        If the score data exist returns it as int,
        otherwise returns `None`
    """
    if score == "--":
        return None
    score = score.strip("%")
    return int(score)


def turn_page(driver: webdriver.Chrome) -> None:
    """
    ## Action: Goes to next page.

    Click the button to load next page.

    Initially the button is not clickable, as there is the cookies dialog layer
    on top of it. In that case it scans for the cookies reject button and clicks
    it, prior of going to the next page.

    Parameters
    ----------
    driver
        The webdriver with the page.
    """
    reject_cookies = driver.find_element(By.ID, IDS["reject_cookies"])

    try:
        reject_cookies.click()
    except ElementClickInterceptedException:
        print("There is no cookies dialog")
    finally:
        next_page_button = driver.find_element(
            By.XPATH, f"//button[@{ATTRIBUTES["next_page"]}]"
        )
        next_page_button.click()
