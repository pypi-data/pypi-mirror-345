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
    pre_days: int, по умолчанию 7
        Длина предпразничного периода.
        
    Notes    
    -----
    Перед использованием трансформера SegmentLongHoliday требуется
    запустить трансформер LongHoliday. При этом параметры
    `min_block_length` и `pre_days` у обоих трансформеров должен быть
    одинаковыми. Последнее обеспечит наличие колонок
    `is_in_longN_holiday_block` и `is_pre_{pre_days}days_longN_holiday`.

    Выходные признаки начинают принимать числовые значения только
    после того, как исходный временной ряд пересечет границу
    праздничного блока или временной ряд начинается с праздничного
    блока.

    Examples
    ------
    >>> import pandas as pd
    >>> import numpy as np
    >>> df = pd.DataFrame({
    ...     "time": [
    ...         "2021‑12‑27", "2021‑12‑28",
    ...         "2021‑12‑30", "2022‑01‑02",
    ...         "2022‑01‑17", "2022‑01‑18"
    ...     ],
    ...     "tte": [1, 2, 15, 5, 1, np.nan],
    ...     "is_in_long3_holiday_block": [0, 0, 0, 1, 0, 0],
    ...     "is_pre_7days_long3_holiday":  [1, 1, 1, 1, 0, 0]
    ... })
    >>> seg = SegmentLongHoliday(
    ...     time_col="time",
    ...     tte_col="tte",
    ...     min_block_length=3,
    ...     pre_days=7
    ... )
    >>> result_df = seg.fit_transform(df)
    >>> print(result_df.to_string(index=False))
          time  tte  is_in_long3_holiday_block  is_pre_7days_long3_holiday  long3_holiday_segment  tte_shift_ratio_long3_holiday
    2021‑12‑27  1.0                          0                           1                    NaN                            NaN
    2021‑12‑28  2.0                          0                           1                    NaN                            NaN
    2021‑12‑30 15.0                          0                           1                    NaN                            NaN
    2022‑01‑02  5.0                          1                           1               0.454545                       0.833333
    2022‑01‑17  1.0                          0                           0               0.512821                       1.052632
    2022‑01‑18  NaN                          0                           0               0.512821                       1.052632
    """

    time_col: str = "time"
    tte_col: str = "tte"
    min_block_length: int = 3
    pre_days: int = 7

    _holiday_flag_cols: list[str] = field(init=False, repr=False)
    _segment_col: str = field(init=False, repr=False)
    _ratio_col: str = field(init=False, repr=False)

    def __post_init__(self):
        if not isinstance(self.pre_days, int) or self.pre_days <= 0:
            raise ValueError("pre_days must be a positive integer.")
        base = f"long{self.min_block_length}_holiday"

        self._holiday_flag_cols = [
            f"is_in_{base}_block",
            f"is_pre_{self.pre_days}days_{base}",
        ]

        self._segment_col = f"{base}_segment"
        self._ratio_col = f"tte_shift_ratio_{base}"

    def fit(self, X: pd.DataFrame, y=None):
        return self

    @staticmethod
    def _safe_div(num: float, den: int) -> float:
        return np.nan if den == 0 else num / den

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if X.empty:
            out = X.copy()
            out[self._segment_col] = np.nan
            out[self._ratio_col] = np.nan
            return out

        req_cols = [self.time_col, self.tte_col, *self._holiday_flag_cols]
        missing = [c for c in req_cols if c not in X.columns]
        if missing:
            raise KeyError(
                f"SegmentLongHoliday: отсутствуют необходимые колонки: "
                f"{', '.join(missing)}"
            )

        df = X.copy()
        df["_orig_idx"] = df.index
        df = df.sort_values(self.time_col).reset_index(drop=True)

        cross_idx: Optional[int] = None
        for i in range(len(df)):
            is_in_block = bool(df.loc[i, self._holiday_flag_cols[0]])
            is_pre_block = bool(df.loc[i, self._holiday_flag_cols[1]])
            if cross_idx is None:
                if is_in_block:
                    cross_idx = i
                    break
                else:
                    if i > 0:
                        prev_is_pre = bool(
                            df.loc[i-1, self._holiday_flag_cols[1]])
                        prev_is_in = bool(
                            df.loc[i-1, self._holiday_flag_cols[0]])

                        if prev_is_pre and not prev_is_in and not is_pre_block:
                            cross_idx = i
                            break

        if cross_idx is None:
            out = X.copy()
            out[self._segment_col] = np.nan
            out[self._ratio_col] = np.nan
            return out

        tte = df[self.tte_col]
        valid_tte = tte.notna()
        holiday_any = df[self._holiday_flag_cols].fillna(0).astype(bool) \
            .any(axis=1)
        cross_mask = np.zeros(len(df), dtype=bool)
        cross_mask[cross_idx:] = True

        active_holiday = holiday_any & cross_mask

        mask_holiday = active_holiday & valid_tte
        mask_normal = (~active_holiday) & valid_tte

        df["cum_tte_h"] = tte.where(mask_holiday, 0).cumsum()
        df["cum_cnt_h"] = mask_holiday.cumsum()
        df["cum_tte_n"] = tte.where(mask_normal, 0).cumsum()
        df["cum_cnt_n"] = mask_normal.cumsum()

        seg_values = np.full(len(df), np.nan)
        ratio_values = np.full(len(df), np.nan)

        for i in range(len(df)):
            if not cross_mask[i]:
                 continue

            cnt_h = int(df.loc[i, "cum_cnt_h"])
            cnt_n = int(df.loc[i, "cum_cnt_n"])

            if cnt_h == 0:
                seg_values[i] = 1.0
                ratio_values[i] = 0.0

            elif cnt_n == 0:
                seg_values[i] = 0.0
                ratio_values[i] = np.inf
            else:
                h_mean = self._safe_div(df.loc[i, "cum_tte_h"], cnt_h)
                n_mean = self._safe_div(df.loc[i, "cum_tte_n"], cnt_n)

                if not pd.isna(h_mean) and not pd.isna(n_mean):
                    R = h_mean / n_mean
                    seg_values[i] = R / (1.0 + R)
                    ratio_values[i] = R
                else:
                    seg_values[i] = np.nan
                    ratio_values[i] = np.nan

        df[self._segment_col] = seg_values
        df[self._ratio_col] = ratio_values

        df.drop(
            columns=["cum_tte_h", "cum_cnt_h", "cum_tte_n", "cum_cnt_n"],
            inplace=True
        )
        df = df.set_index("_orig_idx")
        result_df = df.reindex(X.index)

        return result_df
