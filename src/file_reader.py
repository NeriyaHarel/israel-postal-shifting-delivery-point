import json
from typing import Protocol
import csv


class FileReader(Protocol):
    def load(self, path) -> list[dict]:
        pass

    def save(self, path, data: list[dict]):
        pass


class JsonFileReader(FileReader):
    def load(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save(self, path, data):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class CsvFileReader(FileReader):
    def load(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def save(self, path, data):
        with open(path, 'w', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

def file_reader_factory(file_type: str) -> FileReader:
    file_type = file_type.lower().strip('.')
    if file_type == 'json':
        return JsonFileReader()
    if file_type == 'csv':
        return CsvFileReader()
    raise ValueError(f'Unsupported file type {file_type}')