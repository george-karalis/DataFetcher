from unittest import mock

import pytest
from movingpicturesfetcher.tomato_accessor import (
    get_pictures_data_generator,
    get_pictures_score,
)
from selenium.webdriver.common.by import By


class TestGetPictureDateGenerator:
    """
    ## Tests `get_pictures_data_generator` function.
    """

    @mock.patch("movingpicturesfetcher.tomato_accessor.tile_has_video")
    @mock.patch("movingpicturesfetcher.tomato_accessor.tile_get_url")
    @mock.patch(
        "movingpicturesfetcher.tomato_accessor.webdriver.remote.webelement.WebElement"
    )
    @mock.patch("movingpicturesfetcher.tomato_accessor.webdriver.Chrome")
    def test_get_pictures_data_generator(
        self, mock_driver, mock_tile, mock_get_url, mock_has_video
    ):
        mock_tiles = mock_driver.find_elements.return_value = [mock_tile]
        mock_tile.text.split.return_value = [
            "WATCH THE TRAILER FOR THE FALL GUY",
            "81%",
            "86%",
            "The Fall Guy",
            "Streaming May 21, 2024",
        ]
        mock_has_video.return_value = True
        mock_get_url.return_value = "https://www.rottentomatoes.com/m/the_fall_guy_2024"
        expected_pic_data = ["81%", "86%", "The Fall Guy", "Streaming May 21, 2024"]
        expected_mpic_url = "https://www.rottentomatoes.com/m/the_fall_guy_2024"

        pic_data_gen = get_pictures_data_generator(mock_driver)
        result_pic_data, result_mpic_url = next(pic_data_gen)

        mock_tile.text.split.assert_called_once_with("\n")
        mock_has_video.assert_called_once_with(mock_tile)
        mock_get_url.assert_called_once_with(mock_tile)
        assert set(expected_pic_data) == set(result_pic_data)
        assert expected_mpic_url == result_mpic_url
