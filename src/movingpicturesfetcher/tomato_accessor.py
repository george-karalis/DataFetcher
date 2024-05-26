import time
from typing import Iterator

import deprecation
from movingpicturesdb.schemas import CreateMovingPicture
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
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
)

# TV_SERIES,
from movingpicturesfetcher.utils import (
    clean_date,
    clean_score,
    tile_get_url,
    tile_has_video,
    turn_page,
)

URLS = [MOVIES_IN_CINEMAS, MOVIES_AT_HOME, COMING_SOON]  # , TV_SERIES]


def get_pictures_data_generator(driver: webdriver.Chrome) -> Iterator:
    """
    ## Scans the last 30 moving pictures tiles.

    Parameters
    ----------
    driver
        The webdriver with the html code.

    Yields
    ------
        * picture data in a tuple as str in the following order:
          (critics_score, audience_score, title)
        * moving picture rotten tomatoes url (mpic_url)
    """
    tiles = driver.find_elements(
        By.XPATH, f"//{TAG_NAMES["tile"]}[@{ATTRIBUTES["video_bool"]}]"
    )[-30:]
    for tile in tiles:
        picture_data = tile.text.split("\n")
        if tile_has_video(tile):
            picture_data = picture_data[1:]
        mpic_url = tile_get_url(tile)
        yield picture_data, mpic_url


@deprecation.deprecated(
    deprecated_in="0.1",
    removed_in="1.0",
    details="Use the `get_pictures_data_generator` function instead",
)
def get_pictures_score(picture: WebElement) -> tuple[str | None, str | None]:
    """
    ## Retrieve Audience and Critics Score

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


def moving_picture_generator(driver: webdriver.Chrome) -> Iterator:
    """
    ## Uses the picture tile to create a single CreateMovingPicture object.

    Parameters
    ----------
    driver
        Web driver to be passed in the scrapping data pipeline, which will return
        the necessary picture data to create the Moving Picture object.

    Yields
    ------
        Picture object.
    """
    pictures_data = get_pictures_data_generator(driver)
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


def parse_page(driver: webdriver.Chrome, page_url: str) -> None:
    driver.get(page_url)
    page_counter = 0  # FIXME: Scan all the pages instead of the first 20
    while page_counter <= 20:
        # FIXME: Call post API and add CreateMovingPicture object to the DB
        movie_list = list(moving_picture_generator(driver))
        print(
            f"Page: {page_counter}\n---\n"
            f"First Movie:\n{movie_list[0].title}\n---\n"
            f"Last Movie: \n{movie_list[-1].title}"
        )
        try:
            time.sleep(0.4)  # FIXME: To be removed
            turn_page(driver)
        except ElementNotInteractableException:
            # Reached the end of pages
            return
        page_counter += 1


def main():
    driver = webdriver.Chrome(service=SERVICE, options=OPTIONS)
    for page_url in URLS:
        print(f"{'*'*19}\nParsing {page_url}\n{'*'*19}")
        parse_page(driver, page_url)
    driver.quit()


if __name__ == "__main__":
    main()
