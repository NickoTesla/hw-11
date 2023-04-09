from datetime import datetime, date
from typing import List, Optional


class Field:
    def __init__(self, value: str):
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value!r})"


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value: str):
        self._value = self._clean_value(value)

    @staticmethod
    def _clean_value(value: str) -> str:
        digits = "".join(filter(str.isdigit, value))
        if len(digits) != 10:
            raise ValueError("Invalid phone number")
        return digits

    @Field.value.setter
    def value(self, value: str):
        self._value = self._clean_value(value)


class Birthday(Field):
    DATE_FORMAT = "%d.%m.%Y"

    def __init__(self, value: Optional[str] = None):
        self._value = self._parse_value(value) if value else None

    def _parse_value(self, value: str) -> date:
        try:
            parsed_date = datetime.strptime(value, self.DATE_FORMAT).date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY") from None

        if parsed_date > date.today():
            raise ValueError("Birthday date can't be in the future")

        return parsed_date

    @Field.value.setter
    def value(self, value: str):
        self._value = self._parse_value(value)

    def days_to_birthday(self) -> Optional[int]:
        if not self._value:
            return None
        next_birthday = self._value.replace(year=date.today().year)
        if next_birthday < date.today():
            next_birthday = next_birthday.replace(year=date.today().year + 1)
        time_to_birthday = next_birthday - date.today()
        return time_to_birthday.days


class Record:
    def __init__(
        self,
        name: Name,
        phone: Phone,
        email: Optional[str] = None,
        birthday: Optional[Birthday] = None,
    ):
        self.name = name
        self.phone = phone
        self.email = email
        self.birthday = birthday

    def days_to_birthday(self) -> Optional[int]:
        if not self.birthday:
            return None
        return self.birthday.days_to_birthday()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(name={self.name!r}, "
            f"phone={self.phone!r}, email={self.email!r}, "
            f"birthday={self.birthday!r})"
        )


class AddressBook:
    def __init__(self, records: Optional[List[Record]] = None):
        self._records = records or []

    def add_record(self, record: Record):
        self._records.append(record)

    def delete_record(self, record: Record):
        self._records.remove(record)

    def find_records(self, query: str) -> List[Record]:
        return [
            record
            for record in self._records
            if query in record.name.value or query in record.phone.value
        ]

    def iterator(self, page_size: int):
        current_index = 0
        while current_index < len(self._records):
            yield self._records[current_index: current_index + page_size]
            current_index += page_size

    def __len__(
