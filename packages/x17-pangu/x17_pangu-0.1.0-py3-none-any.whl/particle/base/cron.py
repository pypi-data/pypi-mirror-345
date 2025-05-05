from pyawscron import AWSCron
from datetime import datetime as py_native_dt
from datetime import timezone as py_native_tz

import pytz

from pangu.particle.datestamp import Datestamp


class Cron:
    """
    In lib pyawscron
    All time-related operations are done in UTC
    Manually convert to the desired timezone if needed.
    """

    DEFAULT_TIME_ZONE_NAME = "UTC"

    @classmethod
    def validate(cls, cron_str: str) -> bool:
        try:
            _ = AWSCron(cron_str)
            return True
        except Exception:
            return False

    def __init__(self, cron_str: str):
        self.cron_str = cron_str
        self.cron_obj = AWSCron(cron_str)
        self.minutes = self.cron_obj.minutes
        self.hours = self.cron_obj.hours
        self.days_of_month = self.cron_obj.days_of_month
        self.months = self.cron_obj.months
        self.days_of_week = self.cron_obj.days_of_week
        self.years = self.cron_obj.years
        self.timezone = pytz.timezone(self.DEFAULT_TIME_ZONE_NAME)

    def __str__(self):
        return f"Cron({self.cron_obj.cron})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Cron) and self.cron_str == other.cron_str

    def __ne__(self, other):
        return not self.__eq__(other)

    def __dict__(self):
        return {
            "minutes": self.minutes,
            "hours": self.hours,
            "days_of_month": self.days_of_month,
            "months": self.months,
            "days_of_week": self.days_of_week,
            "years": self.years,
            "timezone": str(self.timezone),
        }

    def get_schedules_between(self, start: Datestamp, end: Datestamp, time_zone_name: str = "UTC"):
        start_utc = start.to_timezone("UTC")
        end_utc = end.to_timezone("UTC")

        results = AWSCron.get_all_schedule_bw_dates(
            py_native_dt.strptime(start_utc.datestamp_str, Datestamp.DATE_TIME_FORMAT).replace(tzinfo=py_native_tz.utc),
            py_native_dt.strptime(end_utc.datestamp_str, Datestamp.DATE_TIME_FORMAT).replace(tzinfo=py_native_tz.utc),
            self.cron_str,
        )

        return [
            Datestamp.from_datetime(dt, time_zone_name="UTC").to_timezone(time_zone_name)
            for dt in results
        ]

    def get_schedules_next(self, start: Datestamp = None, time_zone_name: str = "UTC", count: int = 1):
        if count > 100:
            count = 100

        if start is None:
            start = Datestamp.now(time_zone_name)

        start_utc = start.to_timezone("UTC")

        results = AWSCron.get_next_n_schedule(
            count,
            py_native_dt.strptime(start_utc.datestamp_str, Datestamp.DATE_TIME_FORMAT).replace(tzinfo=py_native_tz.utc),
            self.cron_str,
        )

        return [
            Datestamp.from_datetime(dt, time_zone_name="UTC").to_timezone(time_zone_name)
            for dt in results
        ]

    def get_schedules_prev(self, start: Datestamp = None, time_zone_name: str = "UTC", count: int = 1):
        if count > 100:
            count = 100

        if start is None:
            start = Datestamp.now(time_zone_name)

        start_utc = start.to_timezone("UTC")

        results = AWSCron.get_prev_n_schedule(
            count,
            py_native_dt.strptime(start_utc.datestamp_str, Datestamp.DATE_TIME_FORMAT).replace(tzinfo=py_native_tz.utc),
            self.cron_str,
        )

        return [
            Datestamp.from_datetime(dt, time_zone_name="UTC").to_timezone(time_zone_name)
            for dt in results
        ]
