from datetime import date, datetime

from movingpicturesdb.schemas import CreateMovingPicture
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException, ElementClickInterceptedException,)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from movingpicturesfetcher.elements import (
    ATTRIBUTES,
    CLASS_NAMES,
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

    Args:
        picture (WebElement): The div containing the picture.

    Returns:
        bool: is the picture a video or not
    """
    is_video = tile.get_attribute(ATTRIBUTES["video_bool"])
    has_video = True if is_video == "true" else False
    return has_video


def get_pictures_data(driver: webdriver.Chrome):
    tiles = driver.find_element(
        By.XPATH,
        f"//{TAG_NAMES["tile"]}[@{ATTRIBUTES["video_bool"]}]"
    )
    for tile in tiles:
        picture_data = tile.text.split("\n")
        if _has_video(tile):
            picture_data = picture_data[1:]

        critics_score, audience_score, title, date = picture_data
        url = tile.get_attribute("href")

        content = {
            "title": title,
            "critics_score": clean_score(critics_score),
            "audience_score": clean_score(audience_score),
            "date": date,
            "url": url,
        }
        yield content


def clean_score(score: str) -> str:
    if score == "--":
        return ""
    score = score.strip("%")
    return score


def clean_date(date_str: str) -> date:
    """Clean Date to Populate DB Field."""
    pass


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


def main():
    driver = webdriver.Chrome(service=SERVICE, options=OPTIONS)
    for url in URLS:
        driver.get(url)
        try:
            reject_cookies = driver.find_element(By.ID, "onetrust-reject-all-handler")
            reject_cookies.click()
        except NoSuchElementException as exc:

        picture_data = get_pictures_data(driver)


if __name__ == "__main__":
    main()
