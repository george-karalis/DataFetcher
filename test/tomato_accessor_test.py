from datetime import date
from unittest import mock

import pytest
from movingpicturesdb.schemas import CreateMovingPicture
from movingpicturesfetcher.tomato_accessor import (
    get_pictures_data_generator,
    moving_picture_generator,
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


# @mock.patch("movingpicturesfetcher.tomato_accessor.webdriver.Chrome")


class TestMovingPictureGenerator:
    """
    ## Tests `moving_picture_generator` function.
    """

    @mock.patch("movingpicturesfetcher.tomato_accessor.get_pictures_data_generator")
    @mock.patch(
        "movingpicturesfetcher.tomato_accessor.webdriver.remote.webelement.WebElement"
    )
    def test_moving_picture_generator(self, mock_driver, mock_pic_data_gen):
        mock_pic_data_gen.return_value = (
            (
                ["81%", "86%", "The Fall Guy", "Streaming May 21, 2024"],
                "https://www.rottentomatoes.com/m/the_fall_guy_2024",
            ),
        )
        expected_result = CreateMovingPicture(
            title="The Fall Guy",
            released_date=date(2024, 5, 21),
            rot_critics_score=81,
            rot_audience_score=86,
            url="https://www.rottentomatoes.com/m/the_fall_guy_2024",
        )

        pic_obj_gen = moving_picture_generator(mock_driver)
        result = next(pic_obj_gen)

        mock_pic_data_gen.assert_called_once_with(mock_driver)
        assert expected_result == result
