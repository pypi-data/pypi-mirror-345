from dataclasses import dataclass
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


@dataclass
class Expression(BaseEstimator, TransformerMixin):
    """
    Выполняет вычисления на основе заданного выражения с использованием 
    столбцов DataFrame и функций из numpy.

    Parameters
    ----------
    expression : str
        Выражение для вычисления, например, '(A + B) / C'.
    result_column : str
        Название нового столбца, в который будет записан результат.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [10, 20]})
    >>> transformer = Expression(
    ...     expression='(a + b) / c', 
    ...     out_col='result'
    ... )
    >>> result_df = transformer.transform(df)
    >>> print(result_df.to_string())
       a  b   c  result
    0  1  3  10     0.4
    1  2  4  20     0.3

    Notes
    -----
    Предназначен для быстрого редактирование формул в пайплане
    в ходе иссдедований. Для безопастного построения дополнительных
    результирующих признаков используйте FunctionTransformer.
    """

    expression: str
    out_col: str

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_copy = X.copy()
        
        namespace = {
            'np': np,
            'pd': pd,
            **X.to_dict('series')
        }
            
        try:
            X_copy[self.out_col] = eval(
                self.expression, {"__builtins__": None}, namespace)
        except Exception as e:
            raise ValueError(
                f"Ошибка при вычислении выражения '{self.expression}':\n {e}")
        
        return X_copy
