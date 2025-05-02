import pandas as pd
from ts_features_sculptor import LongHoliday


df = pd.DataFrame({
    "time": [
        "2024-12-22 19:00:00.123",
        "2024-12-29 19:00:00.123",
        "2024-12-30 19:00:00.123",
        "2025-01-02 08:00:00.123",
        "2025-01-01 08:00:00.123",
        "2025-01-03 18:00:00.123",
        "2025-01-03 08:00:00.123",
        "2025-01-09 08:00:00.123",
        "2025-01-11 08:00:00.123",
        "2025-01-12 08:00:00.123",
        "2025-01-13 08:00:00.123",
        "2025-01-20 08:00:00.123",
        "2025-01-21 08:00:00.123",
        "2025-01-22 08:00:00.123"
    ],
})

transformer = LongHoliday(
    time_col="time",
    country_holidays="RU",
    years=[2024, 2025, 2026],
    min_block_length=3,
    days_before_after=[10]
)
result_df = transformer.fit_transform(df)
print(result_df.to_string(index=False))
