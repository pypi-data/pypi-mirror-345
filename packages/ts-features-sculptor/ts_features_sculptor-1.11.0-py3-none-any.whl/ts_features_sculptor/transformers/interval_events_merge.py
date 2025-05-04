import pandas as pd
from dataclasses import dataclass, field
from sklearn.base import BaseEstimator, TransformerMixin
from .time_validator import TimeValidator

@dataclass
class IntervalEventsMerge(BaseEstimator, TransformerMixin, TimeValidator):
    """
    Упрощенный трансформер для врезки интервальных событий в временной
    ряд. Данный трансформер помечает строки основного ряда, попадающие
    внутрь каждого интервального события (включительно на обоих концах),
    флагом inside_event_flag = 1 и добавляет к ним значения указанных
    колонок из events_df.

    Parameters
    ----------
    time_col : str
        Название колонки с временной меткой в основном DataFrame
        (работает как с датами, так и с datetime).
    events_df : pd.DataFrame
        DataFrame с интервальными событиями. Ожидаются колонки
        start и end со значениями date или datetime.
    start_col : str
        Название колонки с временем начала события (push_date)
        в events_df.
    end_col : str
        Название колонки с временем окончания события в events_df.
    events_cols : list of str
        Список колонок из events_df для подстановки в основной ряд.
    fillna : int
        Значение для заполнения параметров события, при отсуствии
        события.
    inside_events_flag_col : str
        Название колонки-флага для строк внутри события.


    Notes
    -----
    В пайплане, данный трансформер является источником
    inside_events_flag_col.

    Если events_df, то врезаются колонки events_cols со значениями
    fillna.

    Examples
    --------
    >>> import pandas as pd
    >>> from ts_features_sculptor import IntervalEventsMerge
    >>> # Основной временной ряд с датой и временем
    >>> df_main = pd.DataFrame({
    ...     'time': pd.to_datetime([
    ...         '2025-01-01 00:00',
    ...         '2025-01-02 08:00',
    ...         '2025-01-03 12:00',
    ...         '2025-01-04 18:00',
    ...         '2025-01-05 00:00'
    ...     ])
    ... })
    >>> # Интервальное событие с полем category
    >>> df_events = pd.DataFrame({
    ...     'start': pd.to_datetime(['2025-01-02 08:00']),
    ...     'end': pd.to_datetime(['2025-01-04 18:00']),
    ...     'category': [1]
    ... })
    >>> transformer = IntervalEventsMerge(
    ...     time_col='time',
    ...     events_df=df_events,
    ...     start_col='start',
    ...     end_col='end',
    ...     events_cols=['category'],
    ...     fillna=0,
    ... )
    >>> result = transformer.transform(df_main)
    >>> print(result.to_string(index=False))
                   time  inside_event_flag  category
    2025-01-01 00:00:00                  0         0
    2025-01-02 08:00:00                  1         1
    2025-01-03 12:00:00                  1         1
    2025-01-04 18:00:00                  1         1
    2025-01-05 00:00:00                  0         0
    """

    time_col: str = "time"
    events_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    start_col: str = "start"
    end_col: str = "end"
    events_cols: list = field(default_factory=list)
    fillna: int = 0
    inside_events_flag_col: str = "inside_event_flag"

    def fit(self, X, y=None):
        return self

    def _check_events_df(self):
        required = {self.start_col, self.end_col, *self.events_cols}
        missing = required - set(self.events_df.columns)
        if missing:
            raise ValueError(
                f"IntervalEventsMerge: events_df не содержит колонок "
                f"{missing}."
            )
        if (
                (self.events_df[self.end_col] <
                 self.events_df[self.start_col]).any()
        ):
            raise ValueError(
                "IntervalEventsMerge: есть события, где end < start.")

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        self._validate_time_column(X)

        X_ = X.copy()

        if self.events_df.empty:
            X_[self.inside_events_flag_col] = 0
            X_[self.inside_events_flag_col] = (
                X_[self.inside_events_flag_col].astype(int)
            )
            for col in self.events_cols:
                X_[col] = self.fillna
            return X_.reset_index(drop=True)

        self._check_events_df()

        X_[self.inside_events_flag_col] = 0
        X_[self.inside_events_flag_col] = X_[
            self.inside_events_flag_col].astype(int)
        for col in self.events_cols:
            X_[col] = self.fillna

        events_sorted = self.events_df.sort_values(by=self.start_col)
        for _, event in events_sorted.iterrows():
            start = event[self.start_col]
            end = event[self.end_col]

            mask = (X_[self.time_col] >= start) & (X_[self.time_col] <= end)
            if not mask.any():
                continue

            X_.loc[mask, self.inside_events_flag_col] = 1
            for col in self.events_cols:
                X_.loc[mask, col] = event[col]

        return X_.reset_index(drop=True)
