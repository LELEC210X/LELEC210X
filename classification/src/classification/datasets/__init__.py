from pathlib import Path
from typing import List


def get_cls_from_path(file: Path) -> str:
    return file.stem.split("_", maxsplit=1)[0]


class Dataset:
    def __init__(
        self, folder: Path = Path(__file__).parent / "soundfiles", format: str = "wav"
    ) -> "Dataset":
        files = {}

        for file in folder.glob("**/*." + format):
            cls = get_cls_from_path(file)
            files.setdefault(cls, []).append(file)

        self.files = files

    def __getitem__(self, cls_index) -> Path:
        cls, index = cls_index
        return self.files[cls][index]

    def list_classes(self) -> List[str]:
        return list(self.files.keys())
