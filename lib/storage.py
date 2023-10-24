import json
from dataclasses import dataclass
from dataclasses import field
from functools import partial
from pathlib import Path
from typing import TypedDict

from lib.factory import WebinarTitles


class WebinarDict(TypedDict):
    id: int
    title: str
    url: str


@dataclass(slots=True, frozen=True)
class WebinarModel:
    id: int
    title: WebinarTitles
    url: str

    @classmethod
    def from_dict(cls, webinar_dict: WebinarDict) -> "WebinarModel":
        return cls(
            id=webinar_dict["id"],
            title=WebinarTitles(webinar_dict["title"].lower()),
            url=webinar_dict["url"],
        )

    def to_dict(self) -> WebinarDict:
        return {
            "id": self.id,
            "title": self.title.value,
            "url": self.url,
        }


@dataclass(slots=True)
class WebinarStorage:
    file: Path = field(default_factory=partial(Path, "storage.json"))

    def load(self) -> list[WebinarModel]:
        with open(self.file, "r", encoding="utf-8") as fd:
            return [WebinarModel.from_dict(e) for e in json.loads(fd.read())]

    def save(self, webinars: list[WebinarModel]) -> None:
        with open(self.file, "w", encoding="utf-8") as fd:
            fd.write(json.dumps([webinar.to_dict() for webinar in webinars]))

    def add_webinar(self, url: str, title: WebinarTitles) -> int:
        webinars = self.load()
        for webinar in webinars:
            if webinar.url == url:
                return webinar.id
        webinar_id = len(webinars)
        webinar = WebinarModel(id=webinar_id, url=url, title=title)
        webinars.append(webinar)
        self.save(webinars)
        return webinar_id

    def get_all_webinars(self) -> list[WebinarModel]:
        return self.load()

    def get_webinar_by_id(self, webinar_id: int) -> WebinarModel | None:
        webinars = self.load()
        for webinar in webinars:
            if webinar.id == webinar_id:
                return webinar
        return None
