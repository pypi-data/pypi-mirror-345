import pandas as pd
import numpy as np
import pytest
from ts_features_sculptor.transformers.long_holiday import LongHoliday


def test_long_holiday_russian_blocks():
    """
    Новогодние праздники представляют собой длинный блок.
    """
    transformer = LongHoliday(
        country_holidays='RU',
        years=[2025],
        min_block_length=3
    )
    
    has_new_year_block = False
    for start, end in transformer.long_blocks:
        if (start.month == 1 and start.day <= 8 and 
            end.month == 1 and end.day >= 1):
            has_new_year_block = True
            break
    
    assert has_new_year_block, "Новогодние праздники --- длинный блок"


def test_long_holiday_transform():
    """Тест трансформации с типичными данными"""
    data = {
        'time': pd.to_datetime([
            '2024-12-28',  # За 2 дня до новогодних праздников
            '2025-01-01',  # Новогодний праздник
            '2025-01-05',  # Новогодний праздник
            '2025-01-10',  # После новогодних праздников
            '2025-01-14',  # Обычный день
        ])
    }
    df = pd.DataFrame(data)
    
    transformer = LongHoliday(
        time_col='time',
        country_holidays='RU',
        years=[2024, 2025],
        min_block_length=3,
        days_before_after=[7]
    )
    
    result_df = transformer.transform(df)
    
    assert 'is_in_long3_holiday_block' in result_df.columns
    assert 'days_to_next_long3_holiday' in result_df.columns
    assert 'is_pre_7days_long3_holiday' in result_df.columns
    assert 'is_post_7days_long3_holiday' in result_df.columns
    
    assert result_df['is_in_long3_holiday_block'].iloc[0] == 0, \
        "is in l3h 2024-12-28"
    assert result_df['is_in_long3_holiday_block'].iloc[1] == 1, \
        "is in l3h 2025-01-01"
    assert result_df['is_in_long3_holiday_block'].iloc[2] == 1, \
        "is in l3h 2025-01-05"
    

    assert result_df['is_pre_7days_long3_holiday'].iloc[0] == 1, \
        "is pre 7d l3h 2024-12-28"
    assert result_df['is_pre_7days_long3_holiday'].iloc[1] == 0, \
        "is pre 7d l3h 2025-01-01"
    
    assert result_df['is_post_7days_long3_holiday'].iloc[4] == 1, \
        "is post 7d l3h 2025-01-14"


def test_long_holiday_days_to_next():
    """
    Расчет дней до следующего длинного праздника
    """
    data = {
        'time': pd.to_datetime([
            '2024-12-29',  # За 1 дня до новогодних праздников
            '2024-12-31',  # За 1 день до следующего праздничного для,
                           # внутри праздничного блока
            '2025-01-01',  # Новогодний праздник
            '2025-01-08',  # Последний день новогодних праздников
            '2025-01-09',  # После новогодних праздников
        ])
    }
    df = pd.DataFrame(data)
    
    transformer = LongHoliday(
        time_col='time',
        country_holidays='RU',
        years=[2024, 2025],
        min_block_length=3
    )
    
    result_df = transformer.transform(df)

    assert result_df['days_to_next_long3_holiday'].iloc[0] == 1.0
    assert result_df['days_to_next_long3_holiday'].iloc[1] == 1.0
    assert result_df['days_to_next_long3_holiday'].iloc[2] == 1.0
    assert np.isnan(result_df['days_to_next_long3_holiday'].iloc[3])
