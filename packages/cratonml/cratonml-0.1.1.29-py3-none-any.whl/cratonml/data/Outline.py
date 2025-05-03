import numpy as np
from cratonapi import datacontainers
from cratonapi.dataconnector import DataConnector


class Outline:
    """
    Класс для работы с контурами.

    Attributes
    ----------
    connection : cratonapi.dataconnector.DataConnector
        Объект класса для взаимодействия с WSeis.
    """

    def __init__(self, connection: DataConnector):
        self.connection = connection

    def read(self, outline_id_list: list[int]) -> list[datacontainers.Outline]:
        """
        Подгружает контуры.

        Parameters
        ----------
        outline_id_list: list[int]
            Список идентификаторов контуров.

        Returns
        -------
        list[cratonapi.datacontainers.Outline]
            Список контуров.
        """

        outline_list = []
        for outline_id in outline_id_list:
            outlines = self.connection.get_outline(outline_id)
            for outline in outlines:
                if outline.coordinates.shape[0] != 0:
                    outline_list.append(outline)
        return outline_list

    def get_info(self) -> dict:
        """
        Подгружает информацию о контурах.

        Returns
        -------
        dict
            Словарь, где ключ - имя контура.
            Значения:
                id: int
                    Идентификатор контура.
                pen_width: int
                    Ширина линии контура.
                pen_style: int
                    Стиль отображения линии контура(Qt.PenStyle).
                pen_color: tuple[float, float, float, float]
                    Цвет отображения линии контура(Красный, Зелёный, Синий, Альфа). Значения от 0 до 1.
                outline_width: int
                    Ширина подложки контура.
                outline_style: int
                    Стиль отображения подложки контура(Qt.PenStyle).
                outline_color: tuple[float, float, float, float]
                    Цвет отображения подложки контура(Красный, Зелёный, Синий, Альфа). Значения от 0 до 1.
                fill_style: int
                    Стиль отображения заливки(Qt.BrushStyle).
                fill_color: tuple[float, float, float, float]
                    Цвет отображения заливки(Красный, Зелёный, Синий, Альфа). Значения от 0 до 1.
        """

        outlines_list = self.connection.get_outlines_list()
        info = {}
        for outline in outlines_list:
            id_dict = {"id": outline.outline_id}
            pen_width_dict = {"pen_width": outline.pen_width}
            pen_style_dict = {"pen_style": outline.pen_style}
            pen_color_dict = {
                "pen_color": (
                    outline.pen_color.red / 255,
                    outline.pen_color.green / 255,
                    outline.pen_color.blue / 255,
                    outline.pen_color.alpha / 255,
                )
            }
            outline_width_dict = {"outline_width": outline.outline_width}
            outline_style_dict = {"outline_style": outline.outline_style}
            outline_color_dict = {
                "outline_color": (
                    outline.outline_color.red / 255,
                    outline.outline_color.green / 255,
                    outline.outline_color.blue / 255,
                    outline.outline_color.alpha / 255,
                )
            }
            fill_style_dict = {"fill_style": outline.fill_style}
            fill_color_dict = {
                "fill_color": (
                    outline.fill_color.red / 255,
                    outline.fill_color.green / 255,
                    outline.fill_color.blue / 255,
                    outline.fill_color.alpha / 255,
                )
            }

            info_dict = dict(
                **id_dict,
                **pen_width_dict,
                **pen_style_dict,
                **pen_color_dict,
                **outline_width_dict,
                **outline_style_dict,
                **outline_color_dict,
                **fill_style_dict,
                **fill_color_dict
            )
            info[outline.outline_name] = info_dict
        return info

    @staticmethod
    def parse_to_numpy(
        outline_list: list[datacontainers.Outline], dx: float = 25, dy: float = 25
    ) -> tuple[list, list, list]:
        """
        Преобразовывает список контуров в список numpy массивов.

        Parameters
        ----------
        outline_list: list[cratonapi.datacontainers.Outline]
            Список контуров.
        dx: float, default=25
            Шаг по сетке x.
        dy: float, default=25
            Шаг по сетке y.

        Returns
        -------
        tuple[list, list, list]
            Список 1D массивов, каждый из которых является значениями контура.
            Список из сеток координат по x каждого контура в виде 2D массивов.
            Список из сеток координат по y каждого контура в виде 2D массивов.
        """
        assert dx > 0, "dx должен принимать положительное значение"
        assert dy > 0, "dy должен принимать положительное значение"

        outlines = []
        xx = []
        yy = []

        for outline in outline_list:
            x_val, y_val, z_val = outline.coordinates.T
            min_x = np.nanmin(x_val)
            max_x = np.nanmax(x_val)
            min_y = np.nanmin(y_val)
            max_y = np.nanmax(y_val)

            x_line = np.arange(min_x, max_x + dx, dx)
            y_line = np.arange(min_y, max_y + dy, dy)

            grid_xx, grid_yy = np.meshgrid(x_line, y_line)
            map_data = np.zeros(grid_xx.shape)
            map_data[:, :] = np.nan

            uniq_values, counts = np.unique(z_val, return_counts=True)
            uniq_class = np.rint(uniq_values[np.argmax(counts)])
            for i in range(map_data.shape[0]):
                for j in range(map_data.shape[1]):
                    x_ = grid_xx[i, j]
                    y_ = grid_yy[i, j]
                    if np.isnan(map_data[i, j]):
                        k = len(x_val) - 1
                        c = False
                        for u in range(len(x_val)):
                            if (y_val[u] <= y_ < y_val[k]) or (
                                y_val[k] <= y_ < y_val[u]
                            ):
                                if y_val[k] != y_val[u]:
                                    if x_ >= (
                                        (x_val[k] - x_val[u])
                                        * (y_ - y_val[u])
                                        / (y_val[k] - y_val[u])
                                        + x_val[u]
                                    ):
                                        c = not c
                            k = u
                        if c:
                            map_data[i, j] = int(uniq_class)
            outlines.append(map_data.ravel())
            xx.append(grid_xx)
            yy.append(grid_yy)
        return outlines, xx, yy
