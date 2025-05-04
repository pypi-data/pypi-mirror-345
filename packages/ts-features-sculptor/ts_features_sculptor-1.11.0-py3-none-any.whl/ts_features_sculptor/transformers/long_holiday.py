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

    def _generate_long_blocks(self, start_year: int, end_year: int):
        self.long_blocks.clear()
        for year in range(start_year, end_year + 1):
            for start_md, end_md in self.block_ranges:
                s = pd.Timestamp(f"{year}-{start_md}")
                e = pd.Timestamp(f"{year}-{end_md}")
                if e < s:
                    e = pd.Timestamp(f"{year + 1}-{end_md}")
                self.long_blocks.append((s.normalize(), e.normalize()))

    def _cache_day_sets(self):
        win = self.window_days
        block_days, pre_days, post_days = set(), set(), set()
        for s, e in self.long_blocks:
            block_days.update(pd.date_range(s, e, freq="D"))
            pre_days.update(
                pd.date_range(
                    s - pd.Timedelta(days=win),
                    s - pd.Timedelta(days=1),
                    freq="D"
                )
            )
            post_days.update(
                pd.date_range(
                    e + pd.Timedelta(days=1),
                    e + pd.Timedelta(days=win),
                    freq="D"
                )
            )
        self._block_days_arr = np.array(
            sorted(block_days), dtype="datetime64[D]")
        self._pre_days_set = {np.datetime64(d, "D") for d in pre_days}
        self._post_days_set = {np.datetime64(d, "D") for d in post_days}

    def _prepare_prefix_sum(self, start: pd.Timestamp, end: pd.Timestamp):
        self._daily_start = np.datetime64(start, "D")
        daily = np.arange(
            self._daily_start,
            np.datetime64(end, "D") +
                np.timedelta64(1, "D"),
            dtype="datetime64[D]"
        )
        mask = np.isin(daily, self._block_days_arr)
        self._holiday_prefix = np.concatenate(
            [[0], np.cumsum(mask.astype(np.int32))])

    def fit(self, X: pd.DataFrame, y=None):
        self._validate_time_column(X)
        if X.empty:
            return self
        start = X[self.time_col].min().normalize()
        end = X[self.time_col].max().normalize()
        self._generate_long_blocks(start.year - 1, end.year + 1)
        self._cache_day_sets()
        self._prepare_prefix_sum(start, end)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        self._validate_time_column(X)
        if not self.long_blocks:
            return X.copy()

        df = X.copy()
        dates = df[self.time_col].dt.normalize() \
            .to_numpy(dtype="datetime64[D]")

        in_holiday = np.isin(dates, self._block_days_arr)
        df["is_in_long_holiday_block"] = in_holiday.astype(np.int8)
        df[f"is_pre_{self.window_days}days_long_holiday"] = np.fromiter(
            (d in self._pre_days_set for d in dates), dtype=np.int8)
        df[f"is_post_{self.window_days}days_long_holiday"] = np.fromiter(
            (d in self._post_days_set for d in dates), dtype=np.int8)

        if self.compute_hist_cross_boundary:
            idx = (
                (dates - self._daily_start) / np.timedelta64(1, "D")
            ).astype(int)
            hol_cnt = self._holiday_prefix[idx]
            cross = (hol_cnt > 0) & (hol_cnt < idx)
            df["is_hist_cross_long_holiday_boundary"] = cross.astype(np.int8)
        else:
            cross = np.zeros(len(df), dtype=bool)
            df["is_hist_cross_long_holiday_boundary"] = 0

        if self.compute_visit_log_odds:
            order = np.argsort(dates, kind="mergesort")
            dates_sorted = dates[order]
            in_holiday_sorted = in_holiday[order]

            first_of_day = np.concatenate(
                [[True], dates_sorted[1:] != dates_sorted[:-1]])

            inc_A = first_of_day & in_holiday_sorted
            inc_C = first_of_day & (~in_holiday_sorted)

            A = np.cumsum(inc_A.astype(np.int32))
            C = np.cumsum(inc_C.astype(np.int32))

            idx_sorted = (
                (dates_sorted - self._daily_start) /
                np.timedelta64(1, "D")
            ).astype(int)
            hol_cal = self._holiday_prefix[idx_sorted + 1]
            week_cal = (idx_sorted + 1) - hol_cal

            B = hol_cal - A
            D = week_cal - C

            ratio = ((A + 0.5) * (D + 0.5)) / ((B + 0.5) * (C + 0.5))
            ratio = np.where(ratio <= 0, np.nan, ratio)
            log_odds_sorted = np.log(ratio)

            log_odds = np.empty_like(log_odds_sorted)
            log_odds[order] = log_odds_sorted
            log_odds[~cross] = np.nan
            df["visit_long_holiday_log_odds"] = log_odds
        else:
            df["visit_long_holiday_log_odds"] = np.nan

        return df