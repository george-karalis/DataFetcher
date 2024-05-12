from datetime import datetime

from movingpicturesdb.schemas import CreateMovingPicture
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from movingpicturesfetcher.elements import (
    ATTRIBUTES,
    CLASS_NAMES,
    IDS,
    TAG_NAMES,
)
from movingpicturesfetcher.settings import OPTIONS, SERVICE
from movingpicturesfetcher.urls import (
    COMING_SOON,
    MOVIES_AT_HOME,
    MOVIES_IN_CINEMAS,
    TV_SERIES,
)

URLS = [MOVIES_IN_CINEMAS, MOVIES_AT_HOME, COMING_SOON, TV_SERIES]


def _has_video(tile: WebElement) -> bool:
    """Finds if the Tile has a playable media.
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


def get_pictures_data(driver: webdriver.Chrome):
    tiles = driver.find_elements(
        By.XPATH, f"//{TAG_NAMES["tile"]}[@{ATTRIBUTES["video_bool"]}]"
    )
    for tile in tiles:
        picture_data = tile.text.split("\n")
        if _has_video(tile):
            picture_data = picture_data[1:]

        a_tag = tile.find_element(By.TAG_NAME, "a")
        mpic_url = a_tag.get_attribute("href")

        yield picture_data, mpic_url


def clean_score(score: str) -> int | None:
    if score == "--":
        return None
    score = score.strip("%")
    return int(score)


def clean_date(date_str: str, date_format: str = "%B %d %Y") -> datetime.date:
    """Clean Date to Populate DB Field.

    The Scrapped date field from the Rotten Tomatoes website is not in an ideal
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


def get_pictures_score(picture: WebElement) -> tuple[str | None, str | None]:
    """
    Retrieve Audience and Critics Score

    Parameters
    ----------
    picture
        The movie/series web element.

    Returns
    -------
        Tuple with the movie/series scores as such:
        (critics_score, audience_score)
    """
    scores = picture.find_element(By.TAG_NAME, "score-pairs-deprecated")
    critics_score = scores.get_attribute("criticsscore")
    audience_score = scores.get_attribute("audiencescore")

    return critics_score, audience_score


def turn_page(driver: webdriver.Chrome) -> None:
    next_page_button = driver.find_element(
        By.XPATH, f"//button[@{ATTRIBUTES["next_page"]}]"
    )
    try:
        next_page_button.click()
    except ElementClickInterceptedException:
        reject_cookies = driver.find_element(By.ID, IDS["reject_cookies"])
        reject_cookies.click()
    finally:
        next_page_button.click()


def moving_picture(driver: webdriver.Chrome):
    """Uses the picture tile to create a single CreateMovingPicture object.

    Parameters
    ----------
    driver
        Web driver to be passed in the scrapping data pipeline, which will return
        the necessary picture data to create the Moving Picture object.

    Yields
    ------
        Picture object.
    """
    try:
        picture_data, mpic_url = next(get_pictures_data(driver))
    except StopIteration:
        turn_page(driver)
    finally:
        moving_picture(driver)
    critics_score, audience_score, title, date = picture_data
    picture_object = CreateMovingPicture(
        title=title,
        released_date=clean_date(date),
        rot_critics_score=clean_score(critics_score),
        rot_audience_score=clean_score(audience_score),
        url=mpic_url,
    )
    yield picture_object


# def moving_pictures_parser(driver: webdriver.Chrome):


def main():
    driver = webdriver.Chrome(service=SERVICE, options=OPTIONS)
    for page_url in URLS:
        driver.get(page_url)
        yield moving_picture(driver)


if __name__ == "__main__":
    main()
