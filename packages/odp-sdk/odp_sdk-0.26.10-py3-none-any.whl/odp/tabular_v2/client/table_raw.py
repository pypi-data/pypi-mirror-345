from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from odp.tabular_v2.client import Table


class Raw:
    def __init__(self, table: "Table"):
        self.table = table

    def list(self) -> list:
        res = self.table._client._request(
            "/api/table/v2/raw/list",
            params={"table_id": self.table._id},
            data={},
        )
        body = res.json()
        return body["files"]

    def upload(self, name: str, data: bytes) -> str:
        res = self.table._client._request(
            "/api/table/v2/raw/upload",
            params={"table_id": self.table._id, "name": name},
            data=data,
        )
        body = res.json()
        return body["raw_id"]

    def download(self, raw_id: str) -> Iterator[bytes]:
        res = self.table._client._request(
            "/api/table/v2/raw/download",
            params={"table_id": self.table._id, "raw_id": raw_id},
        )
        return res.iter()

    def ingest(self, raw_id: str) -> dict:
        res = self.table._client._request(
            "/api/table/v2/raw/ingest",
            params={"table_id": self.table._id, "raw_id": raw_id},
            data={},
        )
        body = res.json()
        return body
