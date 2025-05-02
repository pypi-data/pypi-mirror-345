import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional
from sklearn.base import BaseEstimator, TransformerMixin


@dataclass
class SegmentLongHoliday(BaseEstimator, TransformerMixin):
    """
    Вычисляет сегментационный признак временного ряда относительно
    особых периодов - длительных календарных праздничных блоков.

    Логика:
        - Если до текущей точки не было наблюдений в особые периоды,
            то сегмент = 1 (субъект избегает особые периоды).
        - Если до текущей точки наблюдения были только в особые периоды,
            то сегмент = 0.
        - Если средние TTE для особых и стандартных периодов равны,
            то сегмент = 0.5.
        - Если TTE в особый период больше обычного, то сегмент 
          стремится к 1.
        - Если TTE в особый период меньше обычного, то сегмент 
          стремится к 0.

    Parameters
    ---------
    time_col : str, по умолчанию 'time'
        Название колонки для даты и времени.
    tte_col : str, по умолчанию 'tte'
        Название колонки со значениями Time To Event.
    min_block_length : int, по умолчанию 3
        Минимальная длина блока праздничных дней.
        
    Notes    
    -----
    Перед использованием трансформера SegmentLongHoliday требуется
    запустить трансформер LongHoliday. При этом параметр 
    `min_block_length` у обоих трансформеров должен быть одинаковым.

    По умолчанию считается, что объект изначально не активен в особые 
    периоды.
    
    Examples
    ------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     "time": [
    ...         "2021-12-19", "2021-12-21", "2021-12-27", "2021-12-28",
    ...         "2021-12-30", "2022-01-02", "2022-01-17", "2022-01-18"
    ...     ],
    ...     "tte": [2.0, 6.0, 1.0, 2.0, 15.0, 5.0, 1.0, np.nan],
    ...     "is_in_long3_holiday_block": [0, 0, 0, 0, 0, 1, 0, 0]
    ... })
    >>> transformer = SegmentLongHoliday(
    ...     time_col="time",
    ...     tte_col="tte",
    ...     min_block_length=3
    ... )
    >>> result_df = transformer.fit_transform(df)
    >>> print(result_df.to_string(index=False))
          time  tte  is_in_long3_holiday_block  long3_holiday_segment
    2021-12-19  2.0                          0                    NaN
    2021-12-21  6.0                          0                    NaN
    2021-12-27  1.0                          0                    NaN
    2021-12-28  2.0                          0                    NaN
    2021-12-30 15.0                          0                    NaN
    2022-01-02  5.0                          1               0.490196
    2022-01-17  1.0                          0               0.526316
    2022-01-18  NaN                          0               0.526316
    """

    time_col: str = "time"
    tte_col: str = "tte"
    min_block_length: int = 3

    def __post_init__(self):
        self._holiday_flag_col = (
            f"is_in_long{self.min_block_length}_holiday_block")
        self._output_col = f"long{self.min_block_length}_holiday_segment"

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def _segment_from_row(self, row) -> float:
        if row["cum_cnt_holiday"] == 0:
            return np.nan  # не понятно как в особые дни себя ведет,
                           # так как особых дней не было

        if row["cum_cnt_normal"] == 0:
            return 0.0

        holiday_mean = row["cum_tte_holiday"] / row["cum_cnt_holiday"]
        normal_mean  = row["cum_tte_normal"]  / row["cum_cnt_normal"]

        if pd.isna(holiday_mean) or pd.isna(normal_mean):
            return np.nan

        R = holiday_mean / normal_mean
        return R / (1 + R)

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if X.empty:
            return X.copy()

        req_cols = [self.time_col, self.tte_col, self._holiday_flag_col]
        miss = [c for c in req_cols if c not in X.columns]
        if miss:
            out = X.copy()
            out[self._output_col] = np.nan
            return out

        df = X.copy()
        df["_orig_idx"] = df.index  # для возврата порядка строк
        df = df.sort_values(self.time_col).reset_index(drop=True)

        tte          = df[self.tte_col]
        not_nan_mask = tte.notna()

        holiday_flag = df[self._holiday_flag_col].fillna(0).astype(int)
        holiday_mask = (holiday_flag == 1) & not_nan_mask
        normal_mask  = (holiday_flag == 0) & not_nan_mask

        df["cum_tte_holiday"]   = (tte.where(holiday_mask, 0)).cumsum()
        df["cum_cnt_holiday"]   = holiday_mask.cumsum()
        df["cum_tte_normal"]    = (tte.where(normal_mask, 0)).cumsum()
        df["cum_cnt_normal"]    = normal_mask.cumsum()

        df[self._output_col] = df.apply(self._segment_from_row, axis=1)

        df = df.drop(columns=[
            "cum_tte_holiday", "cum_cnt_holiday",
            "cum_tte_normal", "cum_cnt_normal"])

        # вернули порядок строк
        df = df.set_index("_orig_idx")
        df = df.reindex(X.index)

        return df
