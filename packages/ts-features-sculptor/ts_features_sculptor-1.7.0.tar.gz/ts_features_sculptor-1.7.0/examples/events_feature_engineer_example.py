import pandas as pd
from ts_features_sculptor import (
    IntervalEventsMerge,
    EventsFeatureEngineer
)

# Исходный ряд
df_main = pd.DataFrame({
    'time': pd.to_datetime([
        '2025-01-01', '2025-01-02',
        '2025-01-03', '2025-01-04', '2025-01-08'
    ]),
    'value': [6.0, 2.2, 2.1, 2.5, 5.1]
})
# Интервальное событие
df_events = pd.DataFrame({
    'start': pd.to_datetime(['2025-01-02']),
    'end': pd.to_datetime(['2025-01-04']),
    'intensity': [0.8]
})
# Применяем IntervalEventsMerge
merged = IntervalEventsMerge(
    time_col='time',
    events_df=df_events,
    start_col='start',
    end_col='end',
    events_cols=['intensity'],
    fillna=0
).transform(df_main)
# Применяем EventsFeatureEngineer с ratio и diff
efe = EventsFeatureEngineer(
    time_col='time',
    value_col='value',
    flag_col='inside_event_flag',
    agg_funcs=['mean'],
    fillna=0.0,
    extras=['ratio', 'diff']
)
df_feat = efe.transform(merged)
print(df_feat.to_string(index=False))
