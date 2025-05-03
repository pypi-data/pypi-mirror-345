from typing import Dict, Literal

import polars as pl
from node_hermes_core.nodes.data_generator_node import AbstractWorker
from node_hermes_core.nodes.sink_node import SinkNode
from node_hermes_core.utils.frequency_counter import FrequencyCounter
from pydantic import BaseModel, Field


class DataTrackerPoint:
    series: pl.Series | None = None
    timestamps: pl.Series | None = None

    class Config(BaseModel):
        cache_size: int = 5000

    def __init__(self, config: Config, id: str):
        self.config = config
        self.id = id
        self.last_value = 0
        self.display_name = id
        self.frequency_counter = FrequencyCounter()

    @property
    def name(self):
        return self.display_name

    def clear(self):
        self.series = None
        self.timestamps = None

    def update(self, value: pl.Series, timestamp: pl.Series):
        if len(value) == 0:
            return

        if self.series is None or self.timestamps is None:
            self.series = pl.Series(value)
            self.timestamps = pl.Series(timestamp)
        else:
            self.timestamps, self.series = pl.concat([self.timestamps, timestamp]), pl.concat([self.series, value])

        self.last_value = value[-1]
        self.frequency_counter.update(len(value), timestamp[-1])

        # Trim the series
        if len(self.series) > self.config.cache_size:
            self.series = self.series.slice(self.config.cache_size // 10)
            self.timestamps = self.timestamps.slice(self.config.cache_size // 10)

    def get_values(self):
        if self.series is None or self.timestamps is None:
            return pl.Series([]), pl.Series([])

        if len(self.series) > self.config.cache_size:
            self.series = self.series.slice(self.config.cache_size // 10)
            self.timestamps = self.timestamps.slice(self.config.cache_size // 10)

        # TODO: Add check that the series and timestamps are the same length
        # because of a race condition they can differ
        return self.timestamps.clone(), self.series.clone()

    def __hash__(self):
        return hash(self.id)


class DataTrackerNode(SinkNode, AbstractWorker):
    class Config(SinkNode.Config):
        type: Literal["data_tracker"] = "data_tracker"
        value_tracking: DataTrackerPoint.Config = Field(
            description="The configuration for the value tracking", default_factory=DataTrackerPoint.Config
        )

        @classmethod
        def default(cls):
            return cls()

    config: Config  # type: ignore
    tracked_points: Dict[str, DataTrackerPoint]

    def __init__(self, config: Config | None = None):
        if config is None:
            config = self.Config.default()
        super().__init__(config=config)

    def init(self):
        super().init()
        self.tracked_points = {}

    def clear(self):
        """Clear the data points"""
        self.tracked_points = {}

    def get_timeseries_trace(self, source: str) -> DataTrackerPoint:
        if source not in self.tracked_points:
            self.tracked_points[source] = DataTrackerPoint(config=self.config.value_tracking, id=source)

        return self.tracked_points[source]

    def work(self):
        # Process the data
        while self.has_data():
            # Get the data
            data = self.get_data()
            if data is None:
                continue

            df = data.as_dataframe(add_prefix=True)

            for id in df.columns:
                # We to skip the timestamp column
                if id == "timestamp":
                    continue

                # Update the tracked point with the data
                self.get_timeseries_trace(id).update(df[id], df["timestamp"])

    def deinit(self):
        self.clear()
        super().deinit()
