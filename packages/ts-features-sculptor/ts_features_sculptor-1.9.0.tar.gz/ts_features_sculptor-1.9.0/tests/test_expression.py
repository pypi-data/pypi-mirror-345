import pandas as pd
import numpy as np
import pytest
from ts_features_sculptor import Expression


def test_expression_transformer_basic():
    """
    Тест трансформера Expression. Арифметические выражения.
    """

    data = {
        'a': [1, 2, 3],
        'b': [4, 5, 6]
    }
    df = pd.DataFrame(data)
    
    transformer = Expression(expression='a + b', out_col='sum_a_b')
    result_df = transformer.transform(df)
    
    assert 'sum_a_b' in result_df.columns
    
    expected_values = [5, 7, 9]
    assert list(result_df['sum_a_b'].values) == expected_values


def test_expression_transformer_complex():
    """
    Тест выражений с использованием numpy
    """

    data = {
        'x': [1, 2, 3],
        'y': [4, 5, 6]
    }
    df = pd.DataFrame(data)
    
    transformer = Expression(
        expression='np.sqrt(x**2 + y**2)', 
        out_col='dist'
    )
    result_df = transformer.transform(df)
    

    expected_values = [
        np.sqrt(1**2 + 4**2), 
        np.sqrt(2**2 + 5**2), 
        np.sqrt(3**2 + 6**2)
    ]
    np.testing.assert_array_almost_equal(
        result_df['dist'].values,
        expected_values,
        decimal=10
    )


def test_expression_transformer_with_conditions():
    """
    Тест выражений с условиями
    """
    data = {
        'value': [10, 20, 30, 40, 50]
    }
    df = pd.DataFrame(data)
    
    transformer = Expression(
        expression='np.where(value > 30, "h", "l")', 
        out_col='category'
    )
    result_df = transformer.transform(df)
    
    expected_values = ['l', 'l', 'l', 'h', 'h']
    assert list(result_df['category'].values) == expected_values
