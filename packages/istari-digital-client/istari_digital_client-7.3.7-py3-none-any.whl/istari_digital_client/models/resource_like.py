import abc
from typing import List

from istari_digital_client.models.file_revision import FileRevision
from istari_digital_client.models.file_revision_having import FileRevisionHaving
from istari_digital_client.models.file import File


class ResourceLike(FileRevisionHaving, abc.ABC):
    @property
    @abc.abstractmethod
    def _file(self) -> File: ...

    @property
    def revisions(self) -> List[FileRevision]:
        return self._file.revisions

    @property
    def revision(self) -> FileRevision:
        return self.revisions[-1]
