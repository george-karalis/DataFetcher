from datetime import date, datetime

from movingpicturesdb.schemas import CreateMovingPicture
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from tomato_scrapper.settings import OPTIONS, SERVICE
from tomato_scrapper.urls import (
    COMING_SOON,
    MOVIES_AT_HOME,
    MOVIES_IN_CINEMAS,
    TV_SERIES,
)

URLS = [MOVIES_IN_CINEMAS, MOVIES_AT_HOME, COMING_SOON, TV_SERIES]


def _has_video(picture: WebElement) -> bool:
    tile = picture.find_element(By.TAG_NAME, "tile-dynamic")
    is_video = tile.get_attribute("isvideo")
    has_video = True if is_video == "true" else False
    return has_video


def get_pictures_data(driver: webdriver.Chrome):
    picture_tiles = driver.find_elements(By.CLASS_NAME, "js-tile-link")
    for picture_tile in picture_tiles:
        picture_data = picture_tile.text.split("\n")
        if _has_video(picture_tile):
            picture_data = picture_data[1:]

        critics_score, audience_score, title, date = picture_data
        url = picture_tile.get_attribute("href")

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
        picture_data = get_pictures_data(driver)


if __name__ == "__main__":
    main()
