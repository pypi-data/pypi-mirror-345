from pathlib import Path
from typing import ClassVar

from parsomics_core.entities.files.validated_file import ValidatedFileWithGenome


class DbcanTsvValidatedFile(ValidatedFileWithGenome):
    _VALID_FILE_TERMINATIONS: ClassVar[list[str]] = [
        ".overview.txt",
        "_rundbcanoverview.txt",
    ]

    @property
    def genome_name(self) -> str:
        path_obj = Path(self.path)
        file_name = path_obj.name

        genome_name: str | None = None
        for termination in DbcanTsvValidatedFile._VALID_FILE_TERMINATIONS:
            if file_name.endswith(termination):
                genome_name = file_name[: -len(termination)]

        if genome_name is None:
            raise Exception("Failed at extracting genome name from dbcan tsv file")

        return genome_name
