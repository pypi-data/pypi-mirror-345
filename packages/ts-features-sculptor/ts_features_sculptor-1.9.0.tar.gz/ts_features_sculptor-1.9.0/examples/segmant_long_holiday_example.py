import pandas as pd
from ts_features_sculptor import SegmentLongHoliday


df = pd.DataFrame({
    "time": [
        "2021-12-19", "2021-12-21", "2021-12-27", "2021-12-28",
        "2021-12-30", "2022-01-02", "2022-01-17", "2022-01-18",
        "2022-01-23"
    ],
    "tte": [2.02, 5.96, 1.00, 2.02, 15.0, 4.99, 1.00, 5.01, 1.00],
    "is_in_long3_holiday_block": [0, 0, 0, 0, 0, 1, 0, 0, 0]
})

transformer = SegmentLongHoliday(
    time_col="time",
    tte_col="tte",
    min_block_length=3
)
result_df = transformer.fit_transform(df)

print(result_df.to_string(index=False))
