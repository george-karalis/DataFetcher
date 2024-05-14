from movingpicturesdb.schemas import CreateMovingPicture
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from movingpicturesfetcher.elements import (
    ATTRIBUTES,
    TAG_NAMES,
)
from movingpicturesfetcher.settings import OPTIONS, SERVICE
from movingpicturesfetcher.urls import (
    COMING_SOON,
    MOVIES_AT_HOME,
    MOVIES_IN_CINEMAS,
    TV_SERIES,
)
from movingpicturesfetcher.utils import (
    clean_date,
    clean_score,
    tile_get_url,
    tile_has_video,
)

URLS = [MOVIES_IN_CINEMAS, MOVIES_AT_HOME, COMING_SOON, TV_SERIES]


def get_pictures_data(driver: webdriver.Chrome):
    tiles = driver.find_elements(
        By.XPATH, f"//{TAG_NAMES["tile"]}[@{ATTRIBUTES["video_bool"]}[last()-29:]"
    )[-30:]
    for tile in tiles:
        picture_data = tile.text.split("\n")
        if tile_has_video(tile):
            picture_data = picture_data[1:]
        mpic_url = tile_get_url(tile)
        yield picture_data, mpic_url


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
    pictures_data = get_pictures_data(driver)
    for mpic_data, mpic_url in pictures_data:
        critics_score, audience_score, title, date = mpic_data
        picture_object = CreateMovingPicture(
            title=title,
            released_date=clean_date(date),
            rot_critics_score=clean_score(critics_score),
            rot_audience_score=clean_score(audience_score),
            url=mpic_url,
        )
        yield picture_object


def main():
    driver = webdriver.Chrome(service=SERVICE, options=OPTIONS)
    for page_url in URLS:
        driver.get(page_url)
        yield moving_picture(driver)


if __name__ == "__main__":
    main()
