import pandas as pd
import numpy as np
import pytest
from ts_features_sculptor import SegmentLongHoliday


@pytest.fixture
def sample_data():
    """тестовые данные"""
    return pd.DataFrame({
        "time": pd.to_datetime([
            "2021-12-19", "2021-12-21", "2021-12-27", "2021-12-28",
            "2021-12-30", "2022-01-02", "2022-01-17", "2022-01-18",
            "2022-01-23"
        ]),
        "tte": [2.02, 5.96, 1.00, 2.02, 15.0, 4.99, 1.00, 5.01, 1.00],
        "is_in_long3_holiday_block": [0, 0, 0, 0, 0, 1, 0, 0, 0]
    })


def test_segment_long_holiday_initialization():
    """
    Тест инициализации трансформера.
    """
    # Трансформер с параметрами по умолчанию
    transformer1 = SegmentLongHoliday()
    assert transformer1.time_col == "time"
    assert transformer1.tte_col == "tte"
    assert transformer1.min_block_length == 3
    assert transformer1._holiday_flag_col == "is_in_long3_holiday_block"
    assert transformer1._output_col == "long3_holiday_segment"

    # Трансформер с пользовательскими параметрами
    transformer2 = SegmentLongHoliday(
        time_col="date", 
        tte_col="days_to_next", 
        min_block_length=5
    )
    assert transformer2.time_col == "date"
    assert transformer2.tte_col == "days_to_next"
    assert transformer2.min_block_length == 5
    assert transformer2._holiday_flag_col == "is_in_long5_holiday_block"
    assert transformer2._output_col == "long5_holiday_segment"


def test_segment_long_holiday_transform(sample_data):
    transformer = SegmentLongHoliday()
    result_df = transformer.fit_transform(sample_data)
    
    assert "long3_holiday_segment" in result_df.columns
    
    #  до первого праздничного дня сегмент равен 1
    for i in range(5):  # первые 5 строк - не праздники
        assert result_df["long3_holiday_segment"].iloc[i] == 1.0
    
    # после праздничного дня сегмент должен быть между 0 и 1
    holiday_index = 5  # индекс строки с праздничным днем
    for i in range(holiday_index + 1, len(result_df)):
        segment_value = result_df["long3_holiday_segment"].iloc[i]
        assert 0 <= segment_value <= 1
    
def test_segment_long_holiday_only_normal_days():
    """
    Тест только для обычных (нет праздничных) дней.
    """
    df = pd.DataFrame({
        "time": pd.to_datetime(["2022-01-01", "2022-01-02", "2022-01-03"]),
        "tte": [2.0, 3.0, 4.0],
        "is_in_long3_holiday_block": [0, 0, 0]  # Все дни - обычные
    })
    
    transformer = SegmentLongHoliday()
    result_df = transformer.transform(df)
    
    assert all(result_df["long3_holiday_segment"] == 1.0)
