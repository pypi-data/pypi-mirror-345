from typing import List, Optional

import numpy as np
from cratonapi import datacontainers
from cratonapi.dataconnector import DataConnector
from scipy.interpolate import RegularGridInterpolator


class Grid:
    """
    Класс для работы с гридами.

    Attributes
    ----------
    connection : cratonapi.dataconnector.DataConnector
        Объект класса для взаимодействия с WSeis.
    """

    def __init__(self, connection: DataConnector):
        self.connection = connection

    def read(
        self, grid_id_list: list[int], grid_type_list: list[int]
    ) -> list[datacontainers.Grid]:
        """
        Подгружает cетки(гриды).

        Parameters
        ----------
        grid_id_list: list[int]
            Список идентификаторов гридов.
        grid_type_list: list[int]
            Список типов гридов. Тип грида: 0 — обычный, 1 — смешанный.

        Returns
        -------
        list[cratonapi.datacontainers.Grid]
            Список гридов.
        """

        assert len(grid_id_list) == len(
            grid_type_list
        ), "grid_id_list и grid_type_list должны иметь одинаковую длину"

        grid_list = []
        for grid_id, grid_type in zip(grid_id_list, grid_type_list):
            if grid_type == 0:
                grid = self.connection.get_grid(grid_id)
                if grid.data.shape[0] != 0:
                    grid_list.append(grid)
            elif grid_type == 1:
                grids = self.connection.get_grid_sp(grid_id)
                for grid in grids:
                    grid_list.append(grid)
        return grid_list

    def save(self, name: str, grid: datacontainers.Grid) -> None:
        """
        Загружает грид в Desmana.

        Parameters
        ----------
        name: str
            Имя грида.
        grid: cratonapi.datacontainers.Grid
            Сеточная модель.
        """

        self.connection.upload_grid(name, grid)

    def get_info(self) -> dict:
        """
        Подгружает информацию о гридах.

        Returns
        -------
        dict
            Словарь, где ключ - имя грида.
            Значения:
                id: int
                    Идентификатор грида.
                type: int
                    Тип грида: 0 — обычный, 1 — смешанный.
                visibility: int
                    Видимость грида: 0 — скрытый на планшете, 1 — отображается на планшете.
        """

        grids_list = self.connection.get_grids_list()
        info = {
            grid.grid_name: {
                "id": grid.grid_id,
                "type": grid.grid_type,
                "visibility": grid.grid_visibility,
            }
            for grid in grids_list
        }
        return info

    @staticmethod
    def numpy_to_grid(
        data: np.ndarray,
        x: np.ndarray,
        y: np.ndarray,
        blank_code: float,
        grid_id: int = 0,
    ) -> datacontainers.Grid:
        """
        Преобразовывает numpy массив в грид.

        Parameters
        ----------
        data: np.ndarray
            1D массив значений грида.
        x: np.ndarray
            Сетка координат по x в виде 2D массива.
        y: np.ndarray
            Сетка координат по y в виде 2D массива.
        blank_code: float
            Код бланковки.
        grid_id: int, default=0
            Идентификатор грида.

        Returns
        -------
        cratonapi.datacontainers.Grid
            Грид.
        """

        assert data.ndim == 1, "data: Ожидался 1D массив"
        assert x.ndim == 2, "x: Ожидался 2D массив"
        assert y.ndim == 2, "y: Ожидался 2D массив"
        assert grid_id >= 0, "grid_id должен принимать неотрицательное значение"

        data_to_save = np.nan_to_num(data, nan=blank_code)
        grid_to_save = datacontainers.Grid(
            n_id=grid_id,
            n_x=x.shape[1],
            n_y=x.shape[0],
            x_min=np.min(x),
            x_max=np.max(x),
            y_min=np.min(y),
            y_max=np.max(y),
            z_min=np.nanmin(data[data != blank_code]),
            z_max=np.nanmax(data[data != blank_code]),
            blank_code=blank_code,
            data=data_to_save,
        )
        return grid_to_save

    @staticmethod
    def parse_to_numpy(
        grid_list: list[datacontainers.Grid],
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Преобразовывает список гридов в numpy массив.

        Parameters
        ----------
        grid_list: list[cratonapi.datacontainers.Grid]
            Список гридов.

        Returns
        -------
        tuple[np.ndarray, np.ndarray, np.ndarray]
            2D массив значений грида.
            Сетка координат по x в виде 2D массива.
            Сетка координат по y в виде 2D массива.
        """

        x_min = np.max([grid.x_min for grid in grid_list])
        x_max = np.min([grid.x_max for grid in grid_list])

        y_min = np.max([grid.y_min for grid in grid_list])
        y_max = np.min([grid.y_max for grid in grid_list])

        dx = np.min([(grid.x_max - grid.x_min) / grid.n_x for grid in grid_list])
        dy = np.min([(grid.y_max - grid.y_min) / grid.n_y for grid in grid_list])

        x = np.arange(x_min, x_max, dx)
        y = np.arange(y_min, y_max, dy)

        xx, yy = np.meshgrid(x, y)
        grid_data_list: List[np.ndarray] = []
        mask_list: List[np.ndarray] = []
        for grid in grid_list:
            blank_code = grid.blank_code
            x_grid = np.linspace(grid.x_min, grid.x_max, grid.n_x)
            y_grid = np.linspace(grid.y_min, grid.y_max, grid.n_y)
            grid_2d = np.reshape(grid.data, (grid.n_y, grid.n_x))
            grid_2d[grid_2d == blank_code] = np.nan

            interp_func = RegularGridInterpolator((y_grid, x_grid), grid_2d)
            new_grid = interp_func((yy, xx))
            mask = np.isnan(new_grid)
            mask_list.append(mask.ravel())
            grid_data_list.append(new_grid.ravel())

        mask_array: np.ndarray = np.asarray(mask_list)
        general_mask = np.logical_or.reduce(mask_array).T
        data: np.ndarray = np.asarray(grid_data_list).T
        data[general_mask] = np.nan
        return data, xx, yy

    @staticmethod
    def get_attribute_values_by_coords(
        grid_data: np.ndarray,
        grid_xx: np.ndarray,
        grid_yy: np.ndarray,
        coords: np.ndarray,
    ) -> Optional[np.ndarray]:
        """
        Находит значение гридов в точке.

        Parameters
        ----------
        grid_data: np.ndarray
            Массив значений гридов размера (X*Y, M) или (X*Y,)
        grid_xx: np.ndarray
            Сетка координат по x в виде 2D массива размера (X, Y).
        grid_yy: np.ndarray
            Сетка координат по y в виде 2D массива размера (X, Y).
        coords: np.ndarray
            Координаты точки в виде 1D массива длины 2.

        Returns
        -------
        Optional[np.ndarray]
            Массив длины M значений гридов в точке.
        """

        assert (
            grid_data.ndim == 1 or grid_data.ndim == 2
        ), "grid_data: Ожидался 1D или 2D массив"
        assert grid_xx.ndim == 2, "grid_xx: Ожидался 2D массив"
        assert (
            grid_xx.shape == grid_yy.shape
        ), "grid_xx, grid_yy: Ожидались массивы одинакового размера"
        assert (
            coords.ndim == 1 and len(coords) == 2
        ), "coords: Ожидался 1D массив длины 2"
        assert (
            grid_data.shape[0] == grid_xx.shape[0] * grid_xx.shape[1]
        ), "grid_data: Ожидался массив длины grid_xx.shape[0] * grid_xx.shape[1]"

        if np.any(np.isnan(coords)):
            if grid_data.ndim == 1:
                return np.tile(np.nan, 1)
            if grid_data.ndim == 2:
                return np.tile(np.nan, grid_data.shape[1])
        else:
            x_idx = np.argmin(np.abs(grid_xx - coords[0])[0, :])
            y_idx = np.argmin(np.abs(grid_yy - coords[1])[:, 0])
            if grid_data.ndim == 1:
                return grid_data[y_idx * grid_xx.shape[1] + x_idx]
            if grid_data.ndim == 2:
                return grid_data[y_idx * grid_xx.shape[1] + x_idx, :]

        return None
