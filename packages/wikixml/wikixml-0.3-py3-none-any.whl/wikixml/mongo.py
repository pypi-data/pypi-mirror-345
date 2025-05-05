import argparse
import sys
import time

from pathlib import Path
from pymongo import UpdateOne
from sedb import MongoOperator
from tclogger import logger, logstr, dict_to_str, get_now_ts
from typing import Union, TypedDict

from .wiki import WikiPagesIterater


class MongoConfigsType(TypedDict):
    host: str
    port: int
    dbname: str
    collection: str


class WikiPagesMongoWriter:
    """Sync wiki pages from XML to MongoDB."""

    def __init__(
        self,
        file_path: Union[str, Path],
        mongo_configs: MongoConfigsType,
        max_pages: int = None,
        bulk_size: int = 10000,
    ):
        self.file_path = Path(file_path).resolve()
        self.monog_configs = mongo_configs
        self.bulk_size = bulk_size
        self.iterator = WikiPagesIterater(self.file_path, max_pages=max_pages)
        self.now_ts = get_now_ts()
        self.init_mongo()

    def init_mongo(self):
        self.mongo = MongoOperator(
            self.monog_configs, connect_msg=f"from {self.__class__.__name__}"
        )
        self.pages_collect = self.mongo.db[
            self.monog_configs.get("collection", "pages")
        ]

    def doc_to_operation(self, doc: dict) -> UpdateOne:
        opration = UpdateOne({"_id": doc["id"]}, {"$set": doc}, upsert=True)
        return opration

    def docs_to_operations(self, docs: list[dict]) -> list[UpdateOne]:
        now_ts = get_now_ts()
        for doc in docs:
            doc["insert_at"] = now_ts
        operations = [self.doc_to_operation(doc) for doc in docs]
        return operations

    def bulk(self, operations: list[UpdateOne]):
        retry_count = 3
        while retry_count > 0:
            try:
                self.pages_collect.bulk_write(operations)
                operations.clear()
                break
            except Exception as e:
                logger.warn(f"× {e}")
                retry_count -= 1
                time.sleep(0.25)

    def run(self):
        logger.note("> Write from XML to MongoDB")
        info = {
            "file_path": self.file_path,
            "info_path": self.iterator.info_path,
            "collection": self.pages_collect.full_name,
            "max_pages": self.iterator.max_pages,
            "bulk_size": self.bulk_size,
        }
        logger.success(dict_to_str(info), indent=2)

        docs_bulk = []
        for doc in self.iterator:
            docs_bulk.append(doc)
            if self.bulk_size and len(docs_bulk) >= self.bulk_size:
                desc = logstr.note(f"> Bulking {len(docs_bulk)} docs ...")
                self.iterator.logbar.update(desc=desc, flush=True)
                oprations_bulk = self.docs_to_operations(docs_bulk)
                self.bulk(oprations_bulk)
                docs_bulk.clear()

        if docs_bulk:
            oprations_bulk = self.docs_to_operations(docs_bulk)
            self.bulk(oprations_bulk)
            docs_bulk.clear()


class ArgParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument(
            "-f",
            "--file",
            type=str,
            default="zhwiki-latest-pages-meta-current.xml.bz2",
        )
        self.add_argument("-s", "--host", type=str, default="127.0.0.1")
        self.add_argument("-p", "--port", type=int, default=27017)
        self.add_argument("-d", "--dbname", type=str, default="wiki")
        self.add_argument("-c", "--collection", type=str, default="pages")
        self.add_argument("-m", "--max-pages", type=int, default=None)
        self.add_argument("-b", "--bulk-size", type=int, default=10000)

        self.args, self.unknown_args = self.parse_known_args(sys.argv[1:])


if __name__ == "__main__":
    args = ArgParser().args
    mongo_configs = {
        "host": args.host,
        "port": args.port,
        "dbname": args.dbname,
        "collection": args.collection,
    }
    writer = WikiPagesMongoWriter(
        file_path=args.file,
        mongo_configs=mongo_configs,
        max_pages=args.max_pages,
        bulk_size=args.bulk_size,
    )
    writer.run()

    # python -m wikixml.mongo -d zhwiki -f "../data/zhwiki-latest-pages-meta-current.xml.bz2"
