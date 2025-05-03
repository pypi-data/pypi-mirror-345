from dataclasses import asdict
from typing import List, Tuple

import numpy as np
import numpy.typing as npt
from cratonapi import datacontainers
from cratonapi.dataconnector import DataConnector
from cratonapi.datacontainers import TransformMatrix


class Cube:
    """
    Класс для работы с сейсмическим кубом.

    Attributes
    ----------
    connection : cratonapi.dataconnector.DataConnector
        Объект класса для взаимодействия с WSeis.
    """

    def __init__(self, connection: DataConnector):
        self.connection = connection

    def read(
        self,
        cube_id: int,
        horizon_top_name: str,
        horizon_bot_name: str,
        top_off: float,
        bot_off: float,
        start_inline_idx: int,
        end_inline_idx: int,
        start_crossline_idx: int,
        end_crossline_idx: int,
    ) -> datacontainers.CubeDataSlice:
        """
        Подгружает данные трасс куба в диапазоне.

        Parameters
        ----------
        cube_id: int
            Идентификатор куба.
        horizon_top_name: str
            Имя верхнего горизонта границы.
        horizon_bot_name: str
            Имя нижнего горизонта границы.
        top_off: float
            Смещение для верхнего горизонта.
        bot_off: float
            Смещение для нижней горизонта.
        start_inline_idx: int
            Индекс инлайна с которого начинать набор данных.
        end_inline_idx: int
            Индекс инлайна которым заканчивать набор данных.
        start_crossline_idx: int
            Индекс кросслайна с которого начинать набор данных.
        end_crossline_idx: int
            Индекс кросслайна которым заканчивать набор данных.

        Returns
        -------
        cratonapi.datacontainers.CubeDataSlice
            Куб.
        """

        cube = self.connection.get_cube_data_range(
            cube_id=cube_id,
            horizon_top_name=horizon_top_name,
            horizon_bot_name=horizon_bot_name,
            top_off=top_off,
            bot_off=bot_off,
            start_inline_idx=start_inline_idx,
            end_inline_idx=end_inline_idx,
            start_crossline_idx=start_crossline_idx,
            end_crossline_idx=end_crossline_idx,
        )
        return cube

    def get_info(self) -> dict:
        """
        Подгружает информацию о кубах.

        Returns
        -------
        dict
            Словарь, где ключ - имя куба.
            Значения:
                id: int
                    Идентификатор куба.
                x_min_inl_min_xl: float
                    X координата трассы с минимальными инлайном и кросслайном в кубе.
                y_min_inl_min_xl: float
                    Y координата трассы с минимальными инлайном и кросслайном в кубе.
                x_max_inl_min_xl: float
                    X координата трассы с максимальным инлайном и минимальным кросслайном в кубе.
                y_max_inl_min_xl: float
                    Y координата трассы с максимальным инлайном и минимальным кросслайном в кубе.
                x_min_inl_max_xl: float
                    X координата трассы с минимальным инлайном и максимальным кросслайном в кубе.
                y_min_inl_max_xl: float
                    Y координата трассы с минимальным инлайном и максимальным кросслайном в кубе.
                x_max_inl_max_xl: float
                    X координата трассы с максимальными инлайном и кросслайном в кубе.
                y_max_inl_max_xl: float
                    Y координата трассы с максимальными инлайном и кросслайном в кубе.
                inline_count: int
                    Количество инлайнов в кубе.
                xline_count: int
                    Количество кросслайнов в кубе.
                samples_count: int
                    Количество отсчётов в каждой трассе куба.
                dt: int
                    Шаг дискретизации трасс куба.
                cube_type: int
                    Тип куба.
                min_idx_inline: int
                    Минимальный номер инлайна.
                min_idx_xline: int
                    Минимальный номер кросслайна.
                horizons: list[str]
                    Список имен кубов.
                transform_matrix: cratonapi.datacontainers.TransformMatrix
                    Матрица трансформации.
        """

        cube_list = self.connection.get_cubes()
        info = {}
        for cube in cube_list:
            id_dict = {"id": cube.cube_id}
            properties_dict = asdict(self.connection.get_cube_properties(cube.cube_id))
            horizons_dict = {
                "horizons": list(self.connection.get_cube_horizons(cube.cube_id))
            }
            transforms_dict = {
                "transform_matrix": self.connection.get_transform_matrix(cube.cube_id)
            }

            info_dict = dict(
                id_dict, **properties_dict, **horizons_dict, **transforms_dict
            )
            info[cube.cube_name] = info_dict
        return info

    @staticmethod
    def __get_distance(coord_1: List[float], coord_2: List[float]) -> float:
        return np.sqrt((coord_1[0] - coord_2[0]) ** 2 + (coord_1[1] - coord_2[1]) ** 2)

    @staticmethod
    def __get_transform(
        transform_matrix: TransformMatrix, x: float, y: float
    ) -> Tuple[float, float]:
        x_ = (transform_matrix.a * x + transform_matrix.b * y + transform_matrix.c) / (
            transform_matrix.g * x + transform_matrix.h * y + 1
        )
        y_ = (transform_matrix.d * x + transform_matrix.e * y + transform_matrix.f) / (
            transform_matrix.g * x + transform_matrix.h * y + 1
        )
        return x_, y_

    @staticmethod
    def parse_to_numpy(
        cube: datacontainers.CubeDataSlice, cube_props: dict
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
        """
        Преобразовывает куб в numpy массив.

        Parameters
        ----------
        cube: cratonapi.datacontainers.CubeDataSlice
            Куб.
        cube_props: dict
            Словарь со значениями:
                x_min_inl_min_xl: float
                    X координата трассы с минимальными инлайном и кросслайном в кубе.
                y_min_inl_min_xl: float
                    Y координата трассы с минимальными инлайном и кросслайном в кубе.
                x_max_inl_min_xl: float
                    X координата трассы с максимальным инлайном и минимальным кросслайном в кубе.
                y_max_inl_min_xl: float
                    Y координата трассы с максимальным инлайном и минимальным кросслайном в кубе.
                x_min_inl_max_xl: float
                    X координата трассы с минимальным инлайном и максимальным кросслайном в кубе.
                y_min_inl_max_xl: float
                    Y координата трассы с минимальным инлайном и максимальным кросслайном в кубе.
                x_max_inl_max_xl: float
                    X координата трассы с максимальными инлайном и кросслайном в кубе.
                y_max_inl_max_xl: float
                    Y координата трассы с максимальными инлайном и кросслайном в кубе.
                inline_count: int
                    Количество инлайнов в кубе.
                xline_count: int
                    Количество кросслайнов в кубе.
                transform_matrix: cratonapi.datacontainers.TransformMatrix
                    Матрица трансформации.

        Returns
        -------
        tuple[np.ndarray, np.ndarray, np.ndarray, float]
            2D массив трасс куба.
            Сетка координат по x в виде 2D массива.
            Сетка координат по y в виде 2D массива.
            Код бланковки.
        """

        inlines = cube.inlines
        xlines = cube.xlines

        x_cube_coords = np.array(
            [
                cube_props["x_min_inl_min_xl"],
                cube_props["x_max_inl_min_xl"],
                cube_props["x_min_inl_max_xl"],
                cube_props["x_max_inl_max_xl"],
            ]
        )

        y_cube_coords = np.array(
            [
                cube_props["y_min_inl_min_xl"],
                cube_props["y_max_inl_min_xl"],
                cube_props["y_min_inl_max_xl"],
                cube_props["y_max_inl_max_xl"],
            ]
        )

        data = cube.data
        blank_code = np.max(abs(data))
        blank_mask = data == blank_code

        cube_data = [data[i, ~blank_mask[i, :]] for i in range(len(blank_mask))]
        shapes = np.array([cube_data[i].shape[0] for i in range(len(cube_data))])
        min_size = np.min(shapes)
        if min_size == 0:
            idx = np.where(shapes == 0)[0]
            for i in idx:
                if i > 0:
                    cube_data[i] = cube_data[i - 1]
                else:
                    cube_data[i] = cube_data[i + 1]
                shapes[i] = cube_data[i].shape[0]
            min_size = np.min(shapes)
        cube_slice = np.stack([cube_data[i][:min_size] for i in range(len(cube_data))])

        dx = (
            Cube.__get_distance(
                [x_cube_coords[0], y_cube_coords[0]],
                [x_cube_coords[1], y_cube_coords[1]],
            )
            / cube_props["inline_count"]
        )
        dy = (
            Cube.__get_distance(
                [x_cube_coords[0], y_cube_coords[0]],
                [x_cube_coords[2], y_cube_coords[2]],
            )
            / cube_props["xline_count"]
        )

        dx, dy = int(dx), int(dy)

        idx_dict = {
            (int(inlines[i]), int(xlines[i])): i for i in range(inlines.shape[0])
        }

        x_min = np.min(x_cube_coords)
        y_min = np.min(y_cube_coords)

        x_max = np.max(x_cube_coords)
        y_max = np.max(y_cube_coords)

        size = (int((x_max - x_min) / dx), int((y_max - y_min) / dy))
        grid_values = np.zeros((size[1], size[0], len(cube_slice[0])))
        for i in range(size[1]):
            y_i = y_min + i * dy
            for j in range(size[0]):
                x_j = x_min + j * dx
                inl, xl = Cube.__get_transform(cube_props["transform_matrix"], x_j, y_i)
                inl = int(inl * cube_props["inline_count"])
                xl = int(xl * cube_props["xline_count"])
                if (inl, xl) in idx_dict:
                    idx = int(idx_dict[(inl, xl)])  # type: ignore[assignment]
                    grid_values[i, j, :] = cube_slice[idx][:]
                else:
                    grid_values[i, j, :] = np.nan
        grid_values = np.asarray(grid_values)
        grid_values = np.reshape(
            grid_values,
            newshape=(
                grid_values.shape[0] * grid_values.shape[1],
                grid_values.shape[2],
            ),
        )

        x = np.linspace(x_min, x_max, size[0])
        y = np.linspace(y_min, y_max, size[1])

        xx, yy = np.meshgrid(x, y)

        return grid_values, xx, yy, blank_code
