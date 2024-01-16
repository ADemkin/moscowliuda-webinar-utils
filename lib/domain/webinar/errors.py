from lib.domain.base import RepoError


class WebinarNotFoundError(RepoError):
    ...


class WebinarAlreadyExistsError(RepoError):
    ...


class AccountNotFoundError(RepoError):
    ...


class AccountAlreadyExistsError(RepoError):
    ...
