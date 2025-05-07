from pathlib import Path

from ragloader.indexing.documents import Document, Group, DocumentsStructure


class FilesIndexer:
    def __init__(self, data_directory: str | Path):
        self.root_path: Path = Path(data_directory)
        self.documents_structure: DocumentsStructure = DocumentsStructure(self.root_path)

    def scan(self) -> DocumentsStructure:
        """
        Iterates over a root directory, scans all the groups (subfolders) in it
        and adds them to the documents structure.
        """
        for group_path in self.root_path.iterdir():
            if group_path.is_dir():
                group = self.__scan_group(group_path)
                self.documents_structure.add_group(group)

        return self.documents_structure

    def __scan_group(self, group_path: Path) -> Group:
        """
        Iterates over a single group (a subfolder in the root directory), scans each group item
        and adds it to the group as a Document object.

        Args:
            group_path (Path): path to the subfolder corresponding to a single group.
        """
        group: Group = Group(group_path)
        for group_item in group_path.iterdir():
            document: Document | None = self.__scan_group_item(group_item, group.group_name)
            if document is not None:
                group.add_document(document)

        return group

    @staticmethod
    def __scan_group_item(group_item: Path, group_name: str) -> Document | None:
        """
        Processes a single group item (a file or a folder). Return a Document object.

        Args:
            group_item (Path): path to the group item.

        Returns:
            (Document | None): Document object if the group item is a file or a non-empty folder
                           None for an empty folder and if the item is neither a file nor a folder
        """
        if group_item.is_file():
            return Document.from_file_path(group_item, group_name)
        elif group_item.is_dir():
            return Document.from_directory_path(group_item, group_name)
        else:
            return None
