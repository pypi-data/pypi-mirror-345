import pandas as pd

from examples.interval_events_merge_example_base import df_events
from ts_features_sculptor import IntervalEventsMerge


df_main = pd.DataFrame({
    "time": [
        "2024-12-22 01:01:01",
        "2024-12-26 01:01:01",
        "2025-01-01 01:01:01",
        "2025-01-02 01:01:01",
        "2025-01-03 01:01:01",
        "2025-01-05 01:01:01",
        "2025-01-08 01:01:01",
        "2025-01-11 11:01:01",
        "2025-01-12 01:01:01",
        "2025-01-20 01:01:01",
    ],
    "value": [6.0, 5.1, 5.5, 4.4, 3.3, 2.2, 1.1, 2.2, 3.3, 4.4]
})
df_main["time"] = pd.to_datetime(df_main["time"])
df_main.sort_values(by="time", inplace=True)

df_events = pd.DataFrame([])
# df_events = pd.DataFrame([], columns=['start', 'end'])
# df_events["start"] = pd.to_datetime(df_events.get("start", []))
# df_events["end"]   = pd.to_datetime(df_events.get("end", []))
# df_events = df_events.sort_values(by=["start"])

# Трансформер с тремя колонками, ожидаемыми от events_df
transformer = IntervalEventsMerge(
    time_col="time",
    events_df=df_events,
    start_col="start",
    end_col="end",
    events_cols=["intensity", "category", "priority"],
    fillna=-1.,
    inside_events_flag_col="event_flag"
)
df_result = transformer.transform(df_main)

print("События:")
print(df_events.to_string(index=False))
print("\nРезультат:")
print(df_result.to_string(index=False))
