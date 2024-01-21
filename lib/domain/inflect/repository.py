from dataclasses import dataclass
from dataclasses import field

from lib.clients.db import DB
from lib.domain.inflect.inflector import Inflector
from lib.domain.inflect.models import Inflection


@dataclass(frozen=True, slots=True)
class InflectStorage:
    db: DB = field(default_factory=DB)

    def get_datv_by_name(self, name: str) -> str | None:
        query = """
            SELECT
                name_datv
            FROM inflect_name
            WHERE name = :name
        """
        params = {"name": name}
        if row := self.db.connection.execute(query, params).fetchone():
            return str(row[0])
        return None

    def set_datv_by_name(self, name: str, name_datv: str) -> None:
        query = """
            INSERT INTO inflect_name (
                name,
                name_datv
            )
            VALUES (
                :name,
                :name_datv
            )
            ON CONFLICT(name) DO UPDATE SET
                name_datv = :name_datv
        """
        params = {
            "name": name,
            "name_datv": name_datv,
        }
        self.db.connection.execute(query, params)

    def get_datv_by_family_name(self, family_name: str) -> str | None:
        query = """
            SELECT
                family_name_datv
            FROM inflect_family_name
            WHERE family_name = :family_name
        """
        params = {"family_name": family_name}
        if row := self.db.connection.execute(query, params).fetchone():
            return str(row[0])
        return None

    def set_datv_by_family_name(self, family_name: str, family_name_datv: str) -> None:
        query = """
            INSERT INTO inflect_family_name (
                family_name,
                family_name_datv
            )
            VALUES (
                :family_name,
                :family_name_datv
            )
            ON CONFLICT(family_name) DO UPDATE SET
                family_name_datv = :family_name_datv
        """
        params = {
            "family_name": family_name,
            "family_name_datv": family_name_datv,
        }
        self.db.connection.execute(query, params)

    def get_datv_by_father_name(self, father_name: str) -> str | None:
        query = """
            SELECT
                father_name_datv
            FROM inflect_father_name
            WHERE father_name = :father_name
        """
        params = {"father_name": father_name}
        if row := self.db.connection.execute(query, params).fetchone():
            return str(row[0])
        return None

    def set_datv_by_father_name(self, father_name: str, father_name_datv: str) -> None:
        query = """
            INSERT INTO inflect_father_name (
                father_name,
                father_name_datv
            )
            VALUES (
                :father_name,
                :father_name_datv
            )
            ON CONFLICT(father_name) DO UPDATE SET
                father_name_datv = :father_name_datv
        """
        params = {
            "father_name": father_name,
            "father_name_datv": father_name_datv,
        }
        self.db.connection.execute(query, params)


@dataclass(frozen=True, slots=True)
class InflectRepository:
    inflector: Inflector = field(default_factory=Inflector)
    inflect_storage: InflectStorage = field(default_factory=InflectStorage)

    def get_datv_by_name(self, name: str) -> Inflection:
        if name_datv := self.inflect_storage.get_datv_by_name(name):
            return Inflection(
                base=name,
                datv=name_datv,
                is_confirmed=True,
            )
        return Inflection(
            base=name,
            datv=self.inflector.inflect_datv(name),
            is_confirmed=False,
        )

    def set_datv_by_name(self, name: str, name_datv: str) -> Inflection:
        self.inflect_storage.set_datv_by_name(name, name_datv)
        return Inflection(
            base=name,
            datv=name_datv,
            is_confirmed=True,
        )

    def get_datv_by_family_name(self, family_name: str) -> Inflection:
        if family_name_datv := self.inflect_storage.get_datv_by_family_name(family_name):
            return Inflection(
                base=family_name,
                datv=family_name_datv,
                is_confirmed=True,
            )
        return Inflection(
            base=family_name,
            datv=self.inflector.inflect_datv(family_name),
            is_confirmed=False,
        )

    def set_datv_by_family_name(self, family_name: str, family_name_datv: str) -> Inflection:
        self.inflect_storage.set_datv_by_family_name(family_name, family_name_datv)
        return Inflection(
            base=family_name,
            datv=family_name_datv,
            is_confirmed=True,
        )

    def get_datv_by_father_name(self, father_name: str) -> Inflection:
        if father_name_datv := self.inflect_storage.get_datv_by_father_name(father_name):
            return Inflection(
                base=father_name,
                datv=father_name_datv,
                is_confirmed=True,
            )
        return Inflection(
            base=father_name,
            datv=self.inflector.inflect_datv(father_name),
            is_confirmed=False,
        )

    def set_datv_by_father_name(self, father_name: str, father_name_datv: str) -> Inflection:
        self.inflect_storage.set_datv_by_father_name(father_name, father_name_datv)
        return Inflection(
            base=father_name,
            datv=father_name_datv,
            is_confirmed=True,
        )
