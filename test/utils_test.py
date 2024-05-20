from datetime import date
from unittest import mock

import pytest
from movingpicturesfetcher.utils import (
    clean_date,
    clean_score,
    tile_get_url,
    tile_has_video,
    turn_page,
)
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By


class TestTitleHasVideo:
    """
    ## Tests the `tile_has_video` function.
    """

    @mock.patch("movingpicturesfetcher.utils.webdriver.remote.webelement.WebElement")
    @pytest.mark.parametrize(
        ("is_video, expected"),
        [
            pytest.param("true", True, id="Moving Picture Tile With Video"),
            pytest.param("false", False, id="Moving Picture Tile Without Video"),
        ],
    )
    def test_tile_has_video(self, mock_WebElement, is_video, expected):
        mock_tile = mock_WebElement
        mock_tile.get_attribute.return_value = is_video

        has_video = tile_has_video(mock_tile)

        mock_tile.get_attribute.assert_called_once_with("isvideo")
        assert has_video == expected


class TestTileGetUrl:
    """
    ## Tests the `tile_get_url` function.
    """

    @mock.patch("movingpicturesfetcher.utils.webdriver.remote.webelement.WebElement")
    def test_tile_get_url_from_parent(self, webElement):
        """
        ## Testing passing a tile such as this one:
        ```
        <a class="js-tile-link"
            href="https://www.rottentomatoes.com/m/blood_sweat_and_cheer">
            <tile-dynamic isvideo="false"></tile-dynamic>
        </a>
        ```
        """
        from selenium.common.exceptions import NoSuchElementException
        from selenium.webdriver.common.by import By

        mock_a_tag = mock.MagicMock()
        mock_tile = webElement
        mock_tile.find_element.side_effect = [
            NoSuchElementException,
            mock_a_tag,
        ]
        mock_a_tag.get_attribute.return_value = (
            "https://www.rottentomatoes.com/m/blood_sweat_and_cheer"
        )

        tile_url = tile_get_url(mock_tile)

        mock_tile.find_element.assert_any_call(By.TAG_NAME, "a")
        mock_tile.find_element.assert_any_call(By.XPATH, "./ancestor::a")
        assert tile_url == "https://www.rottentomatoes.com/m/blood_sweat_and_cheer"

    @mock.patch("movingpicturesfetcher.utils.webdriver.remote.webelement.WebElement")
    def test_tile_get_url_from_child(self, webElement):
        """
        ## Testing passing a tile such as this one:
        ```
        <div class="js-tile-link"">
            <tile-dynamic isvideo="false">
                <a href="https://www.rottentomatoes.com/m/blood_sweat_and_cheer"></a>
            </tile-dynamic>
        </div>
        ```

        """
        mock_a_tag = mock.MagicMock()
        mock_tile = webElement
        mock_tile.find_element.side_effect = [
            NoSuchElementException,
            mock_a_tag,
        ]
        mock_a_tag.get_attribute.return_value = (
            "https://www.rottentomatoes.com/m/blood_sweat_and_cheer"
        )

        tile_url = tile_get_url(mock_tile)

        mock_tile.find_element.assert_any_call(By.TAG_NAME, "a")
        mock_tile.find_element.assert_any_call(By.XPATH, "./ancestor::a")
        assert tile_url == "https://www.rottentomatoes.com/m/blood_sweat_and_cheer"


class TestCleanDate:
    """
    ## Tests the `clean_date` function.
    """

    @pytest.mark.parametrize(
        ("date_str, date_format, expected"),
        [
            pytest.param("Streaming May 21, 2024", "%b %d %Y", date(2024, 5, 21)),
            pytest.param("Opens Apr 8 2021", "%b %d %Y", date(2021, 4, 8)),
            pytest.param("Re-releasing Sep 12 1995", "%b %d %Y", date(1995, 9, 12)),
        ],
    )
    def test_clean_date(self, date_str, date_format, expected):
        result = clean_date(date_str=date_str, date_format=date_format)

        assert expected == result


class TestCleanScore:
    """
    ## Tests the `clean_score` function.
    """

    @pytest.mark.parametrize(
        ("score_str, expected"),
        [
            pytest.param("60%", 60),
            pytest.param("--", None),
        ],
    )
    def test_clean_score(self, score_str, expected):
        result = clean_score(score=score_str)

        assert expected == result


class TestTurnPage:
    """
    ## Test the `turn_page` function.
    """

    @mock.patch("movingpicturesfetcher.utils.webdriver.Chrome")
    def test_turn_page_without_cookies_dialog(self, mock_driver):
        mock_reject_cookies_button = mock.MagicMock()
        mock_next_page_button = mock.MagicMock()

        mock_driver.find_element.side_effect = [
            mock_reject_cookies_button,
            mock_next_page_button,
        ]
        mock_reject_cookies_button.click.side_effect = ElementClickInterceptedException
        mock_next_page_button.click.return_value = None

        turn_page(mock_driver)

        mock_driver.find_element.assert_any_call(By.ID, "onetrust-reject-all-handler")
        mock_driver.find_element.assert_any_call(
            By.XPATH, "//button[@data-discoverygridsmanager='btnLoadMore']"
        )
        mock_reject_cookies_button.click.assert_called_once()
        mock_next_page_button.click.assert_called_once()
        mock_next_page_button.click.assert_called_once()

    @mock.patch("movingpicturesfetcher.utils.webdriver.Chrome")
    def test_turn_page_with_cookies_dialog(self, mock_driver):
        mock_next_page_button = mock.MagicMock()
        mock_reject_cookies = mock.MagicMock()
        mock_driver.find_element.side_effect = [
            mock_reject_cookies,
            mock_next_page_button,
        ]
        mock_next_page_button.click.return_value = None
        turn_page(mock_driver)

        mock_driver.find_element.assert_any_call(
            By.XPATH, "//button[@data-discoverygridsmanager='btnLoadMore']"
        )
        mock_driver.find_element.assert_any_call(By.ID, "onetrust-reject-all-handler")
        mock_next_page_button.click.assert_any_call()
        mock_reject_cookies.click.assert_called_once()
        mock_next_page_button.click.assert_any_call()
