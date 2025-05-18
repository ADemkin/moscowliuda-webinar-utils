from enum import IntEnum


class Month(IntEnum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12


MONTH2NAME = {
    Month.JANUARY: "января",
    Month.FEBRUARY: "февраля",
    Month.MARCH: "марта",
    Month.APRIL: "апреля",
    Month.MAY: "мая",
    Month.JUNE: "июня",
    Month.JULY: "июля",
    Month.AUGUST: "августа",
    Month.SEPTEMBER: "сентября",
    Month.OCTOBER: "октября",
    Month.NOVEMBER: "ноября",
    Month.DECEMBER: "декабря",
}

NAME2MONTH = {val: key for key, val in MONTH2NAME.items()}
