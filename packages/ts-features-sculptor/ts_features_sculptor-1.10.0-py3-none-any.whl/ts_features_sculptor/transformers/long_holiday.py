import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict
from sklearn.base import BaseEstimator, TransformerMixin
from .time_validator import TimeValidator

import holidays


@dataclass
class LongHoliday(BaseEstimator, TransformerMixin, TimeValidator):
    """
    Находит длительные праздники и добавляет признаки:
    
    - is_in_long_holiday_block: дата входит в длинный блок;
    - is_pre_Ndays_long_holiday: дата попадает в период за M дней
      до начала блока;
    - is_post_Ndays_long_holiday: дата попадает в период в течение
      M дней после окончания блока.
    - is_hist_cross_long_holiday_boundary: флаг того, что таймсерия
      от первой строки до текущей содержит внутри себя праздничный блок.
    - visit_long_holiday_log_odds: логарифм отношения шансов
      (log odds) со сглаживанием (см. ниже)

    Расчет логарифма отношения шансов:

    M = (A + 0.5) * (D + 0.5)
    N = (B + 0.5) * (C + 0.5)
    log_odds = log (M / N)

    где

    A - число блочных праздничных дней с записью в таймсерии
    B - число блочных праздничных дней без записи в таймсерии
    C - число будней с записью в таймсерии
    D - число бунией без записи в таймсерии

      
    Parameters
    ----------
    time_col : str, по умолчанию 'time'
        Название колонки для даты и времени.
    block_ranges: List[Tuple[str, str]], по умолчению
                  ("01-01", "01-10"), ("05-01", "05-10")
        Длинные праздничные блоки.
    window_days: int = 10
        Размер окна для разметки pre и post праздничных дней.
    compute_hist_cross_boundary: bool, по умолчанию True
        Вычислять или нет флаг is_hist_cross_long_holiday_boundary.
    compute_visit_log_odds: bool, по умолчению True
        Вычислять или нет visit_long_holiday_log_odds.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     "time": pd.to_datetime([
    ...         "2024-12-28",
    ...         "2024-12-29",
    ...         "2024-12-30",
    ...         "2025-01-15",
    ...         "2025-01-25",
    ...         "2025-05-29",
    ...         "2025-12-29",
    ...         "2026-01-01",
    ...         "2026-01-02"
    ...     ])
    ... })
    >>> transformer = LongHoliday(
    ...     time_col="time",
    ...     window_days=10
    ... )
    >>> result_df = transformer.fit_transform(df)
    >>> print(result_df.to_string(index=False))
          time  is_in_long_holiday_block  is_pre_10days_long_holiday  is_post_10days_long_holiday  is_hist_cross_long_holiday_boundary  visit_long_holiday_log_odds
    2024-12-28                         0                           1                            0                                    0                          NaN
    2024-12-29                         0                           1                            0                                    0                          NaN
    2024-12-30                         0                           1                            0                                    0                          NaN
    2025-01-15                         0                           0                            1                                    1                    -2.843852
    2025-01-25                         0                           0                            0                                    1                    -2.075122
    2025-05-29                         0                           0                            0                                    1                    -0.737258
    2025-12-29                         0                           1                            0                                    1                     0.101940
    2026-01-01                         1                           0                            0                                    1                     1.206409
    2026-01-02                         1                           0                            0                                    1                     1.717234
    """

    time_col: str = "time"
    block_ranges: List[Tuple[str, str]] = field(
        default_factory=lambda: [("01-01", "01-10"), ("05-01", "05-10")])
    window_days: int = 10
    compute_hist_cross_boundary: bool = True
    compute_visit_log_odds: bool = True

    long_blocks: List[Tuple[pd.Timestamp, pd.Timestamp]] = field(
        init=False, default_factory=list)
    _block_days_arr: np.ndarray = field(init=False, default=None)
    _pre_days_set: set = field(init=False, default_factory=set)
    _post_days_set: set = field(init=False, default_factory=set)

    _daily_start: Optional[np.datetime64] = field(init=False, default=None)
    _holiday_prefix: np.ndarray = field(init=False, default=None)

    # ------------------------------------------------- helpers --------------------------------------------------
    def _generate_long_blocks(self, start_year: int, end_year: int):
        self.long_blocks.clear()
        for year in range(start_year, end_year + 1):
            for start_md, end_md in self.block_ranges:
                start = pd.Timestamp(f"{year}-{start_md}").normalize()
                end = pd.Timestamp(f"{year}-{end_md}").normalize()
                if end < start:
                    end = pd.Timestamp(f"{year + 1}-{end_md}").normalize()
                self.long_blocks.append((start, end))

    def _cache_day_sets(self):
        block_days, pre_days, post_days = set(), set(), set()
        win = self.window_days

        for s, e in self.long_blocks:
            block_days.update(
                pd.date_range(s, e, freq="D").to_pydatetime()
            )
            pre_days.update(
                pd.date_range(
                    s - pd.Timedelta(days=win),
                    s - pd.Timedelta(days=1),
                    freq="D"
                ).to_pydatetime()
            )
            post_days.update(
                pd.date_range(
                    e + pd.Timedelta(days=1),
                    e + pd.Timedelta(days=win),
                    freq="D"
                ).to_pydatetime()
            )

        self._block_days_arr = np.array(
            sorted({np.datetime64(d, "D") for d in block_days}),
            dtype="datetime64[D]"
        )
        self._pre_days_set = {np.datetime64(d, "D") for d in pre_days}
        self._post_days_set = {np.datetime64(d, "D") for d in post_days}

    def _prepare_prefix_sum(
            self, daily_start: pd.Timestamp, daily_end: pd.Timestamp
    ):
        self._daily_start = np.datetime64(daily_start, "D")
        daily_dates = np.arange(
            self._daily_start,
            np.datetime64(daily_end, "D") +
                np.timedelta64(1, "D"),
            dtype="datetime64[D]"
        )
        holiday_mask = np.isin(daily_dates, self._block_days_arr)
        self._holiday_prefix = np.concatenate(
            ([0], np.cumsum(holiday_mask.astype(np.int32), dtype=np.int32))
        )

    def fit(self, X: pd.DataFrame, y=None):
        self._validate_time_column(X)
        if X.empty:
            return self

        min_date = X[self.time_col].min().normalize()
        max_date = X[self.time_col].max().normalize()

        self._generate_long_blocks(min_date.year - 1, max_date.year + 1)
        self._cache_day_sets()

        self._prepare_prefix_sum(min_date, max_date)

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        self._validate_time_column(X)
        if not self.long_blocks:
            return X.copy()

        df = X.copy()
        date_ser = df[self.time_col].dt.normalize()
        date_arr = date_ser.to_numpy().astype("datetime64[D]")

        in_holiday = np.isin(date_arr, self._block_days_arr)
        df["is_in_long_holiday_block"] = in_holiday.astype(np.int8)

        df[f"is_pre_{self.window_days}days_long_holiday"] = np.fromiter(
            (d in self._pre_days_set for d in date_arr),
            dtype=np.int8,
            count=len(date_arr)
        )
        df[f"is_post_{self.window_days}days_long_holiday"] = np.fromiter(
            (d in self._post_days_set for d in date_arr),
            dtype=np.int8,
            count=len(date_arr)
        )

        if self.compute_hist_cross_boundary:
            idx_arr = (
                (date_arr - self._daily_start) /
                np.timedelta64(1, "D")
            ).astype(int)
            hol_cnt_cal = self._holiday_prefix[idx_arr]
            cross = (hol_cnt_cal > 0) & (hol_cnt_cal < idx_arr)
            df["is_hist_cross_long_holiday_boundary"] = cross.astype(np.int8)
        else:
            df["is_hist_cross_long_holiday_boundary"] = 0
            cross = np.zeros(len(df), dtype=bool)

        if self.compute_visit_log_odds:
            sorted_idx = np.argsort(date_arr, kind="mergesort")

            cum_hol_visits_sorted = np.cumsum(
                in_holiday[sorted_idx].astype(np.int32))
            cum_all_visits_sorted = np.arange(1, len(df) + 1, dtype=np.int32)
            cum_week_visits_sorted = (
                    cum_all_visits_sorted - cum_hol_visits_sorted)

            idx_arr_sorted = (
                (date_arr[sorted_idx] - self._daily_start) /
                np.timedelta64(1, "D")
            ).astype(int)
            hol_calendar_sorted = self._holiday_prefix[idx_arr_sorted + 1]
            week_calendar_sorted = (idx_arr_sorted + 1) - hol_calendar_sorted

            A = cum_hol_visits_sorted
            C = cum_week_visits_sorted
            B = hol_calendar_sorted - A
            D = week_calendar_sorted - C

            log_odds_sorted = np.log(
                ((A + 0.5) * (D + 0.5)) / ((B + 0.5) * (C + 0.5)))

            log_odds = np.empty_like(log_odds_sorted, dtype=float)
            log_odds[sorted_idx] = log_odds_sorted

            log_odds[~cross] = np.nan
            df["visit_long_holiday_log_odds"] = log_odds
        else:
            df["visit_long_holiday_log_odds"] = np.nan

        return df
