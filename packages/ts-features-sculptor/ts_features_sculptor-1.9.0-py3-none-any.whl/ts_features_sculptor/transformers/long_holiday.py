import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Set
from sklearn.base import BaseEstimator, TransformerMixin
from .time_validator import TimeValidator

import holidays


@dataclass
class LongHoliday(BaseEstimator, TransformerMixin, TimeValidator):
    """
    Находит длительные праздники (интервалы только из праздничных дней, 
    длиной >= min_block_length) и размечает данные:
    
    - is_in_longN_holiday_block: дата входит в длинный блок;
    - days_to_next_longN_holiday: число дней до ближайшего будущего 
      праздника из длинных блоков;
    - is_pre_Mdays_longN_holiday: дата попадает в период за M дней 
      до начала блока;
    - is_post_Mdays_longN_holiday: дата попадает в период в течение 
      M дней после окончания блока.
      
    Parameters
    ----------
    time_col : str, по умолчанию 'time'
        Название колонки для даты и времени.
    country_holidays : Optional[str], по умолчанию None
        Код страны (например, 'RU' для России) для определения 
        праздников.
    years : Optional[List[int]], по умолчанию None
        Список лет, для которых нужно учитывать праздники.
    min_block_length : int, по умолчанию 3
        Минимальная длина блока праздничных дней для считания его 
        "длинным".
    days_before_after : List[int], по умолчанию [7, 14]
        Список количества дней до и после блока праздников, для которых 
        нужно создать признаки.
       
    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     "time": pd.to_datetime([
    ...         "2024-12-28",
    ...         "2024-12-29",
    ...         "2024-12-30",
    ...         "2025-01-01",
    ...         "2025-01-02",
    ...         "2025-01-03",
    ...         "2025-01-09" 
    ...     ])
    ... })
    >>> transformer = LongHoliday(
    ...     time_col="time",
    ...     country_holidays="RU",
    ...     years=[2024, 2025],
    ...     min_block_length=3,
    ...     days_before_after=[10]
    ... )
    >>> result_df = transformer.fit_transform(df)
    >>> result_df = result_df.rename(columns={
    ...     'is_in_long3_holiday_block': 'is_l3hb',
    ...     'is_pre_10days_long3_holiday': 'is_pre_l3hb',
    ...     'is_post_10days_long3_holiday': 'is_post_l3hb',
    ...     'days_to_next_long3_holiday': 'days_to_l3hb'
    ... })
    >>> print(result_df.to_string(index=False))
          time  is_l3hb  is_pre_l3hb  is_post_l3hb  days_to_l3hb
    2024-12-28        0            1             0           2.0
    2024-12-29        0            1             0           1.0
    2024-12-30        1            0             0           1.0
    2025-01-01        1            0             0           1.0
    2025-01-02        1            0             0           1.0
    2025-01-03        1            0             0           1.0
    2025-01-09        0            0             1           NaN
    """

    time_col: str = "time"
    country_holidays: Optional[str] = None
    years: Optional[List[int]] = None
    min_block_length: int = 3
    days_before_after: List[int] = field(default_factory=lambda: [14])

    def __post_init__(self):
        self._suffix = str(self.min_block_length)

        self.holidays_set = set()
        if self.country_holidays and self.years:
            try:
                hset = holidays.country_holidays(self.country_holidays,
                                                 years=self.years)
                self.holidays_set = {
                    pd.Timestamp(k) for k in hset.keys()}
            except KeyError:
                raise ValueError(
                    f"LongHoliday: код страны {self.country_holidays} "
                    f"не поддерживается.")

        self.long_blocks: List[Tuple[pd.Timestamp, pd.Timestamp]] = []
        self._compute_long_blocks()

        self.all_block_days: List[pd.Timestamp] = \
            self._make_block_days_list()

        self.pre_days_dict: dict = {}
        self.post_days_dict: dict = {}
        self._compute_pre_and_post_block_days()

    def _compute_long_blocks(self):
        if not self.holidays_set:
            return

        sorted_days = sorted(self.holidays_set)
        start = sorted_days[0]
        prev = sorted_days[0]

        for d in sorted_days[1:]:
            # если дни идут подряд
            if (d - prev).days == 1:
                prev = d
            else:
                # достаточно ли длинен блок (start..prev)
                length = (prev - start).days + 1
                if length >= self.min_block_length:
                    self.long_blocks.append((start, prev))
                # новый блок
                start = d
                prev = d

        # проверяем последний потенциальный блок
        length = (prev - start).days + 1
        if length >= self.min_block_length:
            self.long_blocks.append((start, prev))

    def _make_block_days_list(self) -> List[pd.Timestamp]:
        """
        Создаёт список всех календарных дат, входящих в длинные блочные 
        праздники.
        """        
        block_days = []
        for (start, end) in self.long_blocks:
            block_range = pd.date_range(
                start=start, end=end, freq="D").tolist()
            block_days.extend(block_range)
        block_days.sort()
        return block_days

    def _compute_pre_and_post_block_days(self):
        """
        Формирует множества дат для предпраздничных и постпраздничных 
        периодов для каждого значения дней из параметра 
        days_before_after.
        """
        for days in self.days_before_after:
            self.pre_days_dict[days] = set()
            self.post_days_dict[days] = set()
            
            for (start, end) in self.long_blocks:
                pre_days = pd.date_range(
                    start=start - pd.Timedelta(days=days),
                    end=start - pd.Timedelta(days=1),
                    freq="D"
                )
                self.pre_days_dict[days].update(pre_days)

                post_days = pd.date_range(
                    start=end + pd.Timedelta(days=1),
                    end=end + pd.Timedelta(days=days), 
                    freq="D"
                )
                self.post_days_dict[days].update(post_days)

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        self._validate_time_column(X)

        df = X.copy()
        df[self.time_col] = df[self.time_col].dt.normalize()

        if self.min_block_length <= 0:
            raise ValueError(
                "LongHoliday: min_block_lengtth должен быть больше нуля.")

        if any(d <= 0 for d in self.days_before_after):
            raise ValueError(
                f"LongHoliday: значения в days_before_after должны быть"
                f"больше нуля.")

        col_in_block = f"is_in_long{self._suffix}_holiday_block"
        col_distance = f"days_to_next_long{self._suffix}_holiday"

        in_block = np.zeros(len(df), dtype=int)
        for i, day_val in enumerate(df[self.time_col]):
            for (start, end) in self.long_blocks:
                if start <= day_val <= end:
                    in_block[i] = 1
                    break
        df[col_in_block] = in_block

        for days in self.days_before_after:
            # "is_pre_Mdays_longN_holiday"
            col_pre = f"is_pre_{days}days_long{self._suffix}_holiday"
            df[col_pre] = df[self.time_col].isin(
                self.pre_days_dict[days]).astype(int)
            
            # "is_post_Mdays_longN_holiday"
            col_post = f"is_post_{days}days_long{self._suffix}_holiday"
            df[col_post] = df[self.time_col].isin(
                self.post_days_dict[days]).astype(int)

        # "days_to_next_longN_holiday"
        if not self.all_block_days:
            df[col_distance] = np.nan
        else:
            arr_block_days = np.array(self.all_block_days,
                                      dtype="datetime64[ns]")
            distances = []
            for current_date in df[self.time_col]:
                pos = np.searchsorted(arr_block_days,
                                      np.datetime64(current_date),
                                      side="right")
                if pos == len(arr_block_days):
                    distances.append(np.nan)
                else:
                    next_day = arr_block_days[pos]
                    diff_days = (
                        (next_day - current_date.to_datetime64()) / 
                        np.timedelta64(1, 'D')
                    )
                    distances.append(diff_days)
            df[col_distance] = distances

        return df
