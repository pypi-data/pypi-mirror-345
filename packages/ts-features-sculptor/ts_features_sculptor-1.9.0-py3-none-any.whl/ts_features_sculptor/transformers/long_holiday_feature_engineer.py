import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Sequence
from sklearn.base import BaseEstimator, TransformerMixin


@dataclass
class LongHolidayFeatureEngineer(BaseEstimator, TransformerMixin):
    """Создает ratio и visit‑count признаки для праздничных блоков
    трансформера LongHoliday.

    Parameters
    ----------
    base_name : str, default ``"long3_holiday"``
        Исходные индикаторы для построения новых признаков.
    compute_ratio : bool, default ``True``
        Вычислять признак  ``{base_name}_visit_ratio`` или нет.
    pre_windows, post_windows : sequence of int | None
        Число дней для  вычисления *pre* / *post* числа визитов.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'is_in_long3_holiday_block': [0, 1, 1, 0],
    ...     'is_pre_7days_long3_holiday': [1, 0, 0, 0],
    ...     'is_pre_14days_long3_holiday': [1, 1, 0, 0]
    ... })
    >>> fe = LongHolidayFeatureEngineer(
    ...     pre_windows=[7, 14],
    ...     post_windows=[],
    ...     compute_ratio=True
    ... )
    >>> result_df = fe.transform(df)
    >>> float(result_df['long3_holiday_visit_ratio'].iloc[0])
    0.5
    >>> int(result_df['pre_long3_holiday_visit_count_7d'].iloc[0])
    1
    >>> int(result_df['pre_long3_holiday_visit_count_14d'].iloc[0])
    2
    """

    base_name: str = "long3_holiday"
    compute_ratio: bool = True
    pre_windows: Optional[Sequence[int]] = None
    post_windows: Optional[Sequence[int]] = None

    def _broadcast(
            self, value: float | int | np.floating, index) -> pd.Series:
        return pd.Series(value, index=index)

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_ = X.copy()

        idx = X_.index

        if self.compute_ratio:
            inside_col = f"is_in_{self.base_name}_block"
            ratio_col = f"{self.base_name}_visit_ratio"
            if inside_col in X_:
                ratio_val = float(X_[inside_col].mean(skipna=True))
                X_[ratio_col] = self._broadcast(ratio_val, idx)
            else:
                X_[ratio_col] = np.nan

        for w in self.pre_windows or []:
            src = f"is_pre_{w}days_{self.base_name}"
            dst = f"pre_{self.base_name}_visit_count_{w}d"
            if src in X_:
                cnt_val = int(X_[src].sum(skipna=True))
                X_[dst] = self._broadcast(cnt_val, idx)
            else:
                X_[dst] = np.nan

        for w in self.post_windows or []:
            src = f"is_post_{w}days_{self.base_name}"
            dst = f"post_{self.base_name}_visit_count_{w}d"
            if src in X_:
                cnt_val = int(X_[src].sum(skipna=True))
                X_[dst] = self._broadcast(cnt_val, idx)
            else:
                X_[dst] = np.nan

        return X_
