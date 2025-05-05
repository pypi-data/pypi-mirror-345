from pangu.particle.datestamp import Datestamp
from datetime import date, datetime
import holidays


class Holiday:
    DEFAULT_COUNTRY = "AU"
    DEFAULT_SUBDIV = None

    @classmethod
    def au_nsw(cls, year=None):
        if year is None:
            year = Datestamp.now().year
        return cls(
            country_code="AU",
            subdiv="NSW",
            year=year,
        )

    @classmethod
    def au(cls, year=None):
        if year is None:
            year = Datestamp.now().year
        return cls(
            country_code="AU",
            year=year,
        )

    @classmethod
    def set_default_country(cls, country_code):
        cls.DEFAULT_COUNTRY = country_code

    @classmethod
    def set_default_subdiv(cls, subdiv):
        cls.DEFAULT_SUBDIV = subdiv

    def __init__(
        self,
        country_code="AU",
        subdiv=None,
        year=None,
    ):
        self.country_code = country_code or self.DEFAULT_COUNTRY
        self.subdiv = subdiv or self.DEFAULT_SUBDIV
        self.year = year or Datestamp.now().year

        params = {
            "subdiv": self.subdiv,
            "years": self.year,
        }
        params = {k: v for k, v in params.items() if v is not None}
        self.holidays = holidays.country_holidays(
            self.country_code,
            **params,
        )

    def __str__(self):
        return f"{self.country_code} {self.subdiv} {self.year}"

    def __dict__(self):
        return {
            "country_code": self.country_code,
            "subdiv": self.subdiv,
            "year": self.year,
        }

    def is_holiday(self, datestamp: Datestamp) -> bool:
        return datestamp.datetime.date() in self.holidays

    def list_holidays(self):
        return sorted(self.holidays.items())

    def list_holiday_dates(self, as_datestamp=False):
        return [
            Datestamp.from_datetime(datetime.combine(holiday_date, datetime.min.time()))
            if as_datestamp else holiday_date
            for holiday_date, _ in self.list_holidays()
        ]

    def list_holiday_names(self):
        return [holiday_name for _, holiday_name in self.list_holidays()]

    def export(self, as_datestamp=False):
        result = {}
        for holiday_date, holiday_name in self.list_holidays():
            value = (
                Datestamp.from_datetime(datetime.combine(holiday_date, datetime.min.time()))
                if as_datestamp else holiday_date
            )
            result[holiday_name] = value
        return result
