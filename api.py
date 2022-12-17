from storage import Storage

WebinarT = dict


class WebinarApi:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def get_name_morph(self, name: str) -> str | None:
        """Suggest name in datv form"""
        return self.storage.get_name_morph(name)

    def set_name_morph(self, name: str, name_datv: str) -> None:
        """Store name and name in datv form as key-pair"""
        self.storage.set_name_morph(name, name_datv)
