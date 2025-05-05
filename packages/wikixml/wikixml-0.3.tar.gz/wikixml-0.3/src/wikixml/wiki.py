import bz2
import json

from lxml import etree
from pathlib import Path
from tclogger import logger, logstr, TCLogbar
from tclogger import dict_to_str, dict_get, chars_len, chars_slice, brk
from typing import Union, Generator

from .structures import ElementToDictConverter


class WikiXmlParser:
    def __init__(self, file_path: Union[str, Path]):
        self.file_path = file_path
        self.xmlns = "{http://www.mediawiki.org/xml/export-0.11/}"
        self.logbar = TCLogbar()
        self.converter = ElementToDictConverter()

    def preview_lines(self, max_lines: int = 10):
        with bz2.BZ2File(self.file_path, "rb") as rf:
            for idx, line in enumerate(rf):
                line_str = line.decode("utf-8").rstrip()
                logger.file(line_str)
                if idx >= max_lines:
                    break

    def preview_pages(self, max_pages: int = None):
        with bz2.BZ2File(self.file_path, "rb") as rf:
            context = etree.iterparse(rf, tag=self.xmlns + "page")
            for idx, (_, element) in enumerate(context):
                if max_pages and idx >= max_pages:
                    break
                page_dict = self.converter.convert(element)
                # logger.mesg(dict_to_str(page_dict))
                title = dict_get(page_dict, "title")
                title_part = chars_slice(title, 0, 20)
                text = dict_get(page_dict, "revision.text")
                text_len = chars_len(text)
                logger.note(f"* {title_part} : {logstr.mesg(brk(text_len))}")


class WikiPagesIterater:
    def __init__(self, file_path: Union[str, Path], max_pages: int = None):
        self.file_path = file_path
        self.info_path = file_path.parent / file_path.name.replace(".bz2", ".json")
        self.max_pages = max_pages
        self.xmlns = "{http://www.mediawiki.org/xml/export-0.11/}"
        self.logbar = TCLogbar()
        self.converter = ElementToDictConverter()

    def update_logbar(self, doc: dict):
        title = dict_get(doc, "title")
        title_part = chars_slice(title, 0, 20)
        text = dict_get(doc, "revision.text")
        text_len = chars_len(text)
        text_len_str = brk(f"{text_len:>8}")
        desc = f"* {title_part} : {logstr.mesg(text_len_str)}"
        self.logbar.update(increment=1, desc=desc)

    def get_file_hash(self) -> str:
        return str(self.file_path.stat().st_mtime)

    def get_file_info(self) -> dict:
        if not self.info_path.exists():
            return {}
        file_hash = self.get_file_hash()
        with open(self.info_path, "r", encoding="utf-8") as rf:
            file_info = json.load(rf)
            if file_info.get(file_hash, None) is None:
                return {}
            else:
                return file_info

    def set_file_info(self, new_info: dict):
        if not self.info_path.exists():
            self.info_path.touch()
            info = {}
        else:
            with open(self.info_path, "r", encoding="utf-8") as rf:
                info = json.load(rf)
        info.update(new_info)
        file_hash = self.get_file_hash()
        if info.get("hash", None) != file_hash:
            info["hash"] = file_hash
        logger.note("> Saving info:")
        with open(self.info_path, "w", encoding="utf-8") as wf:
            json.dump(info, wf, indent=4, ensure_ascii=False)
            logger.file(f"  * {self.info_path}")
            logger.mesg(dict_to_str(info), indent=2)

    def count_pages(self) -> int:
        count_bar = TCLogbar()
        count_bar.desc = logstr.note("> Counting pages:")
        file_info = self.get_file_info()
        if file_info.get("count", None) is not None:
            count_bar.count = file_info["count"]
            count_bar.update(flush=True)
        else:
            with bz2.BZ2File(self.file_path, "rb") as rf:
                context = etree.iterparse(rf, tag=self.xmlns + "page", events=("end",))
                for idx, (_, element) in enumerate(context):
                    count_bar.update(increment=1)
                    element.clear()
                del context
            self.set_file_info({"count": count_bar.count})
        self.logbar.total = count_bar.count
        return count_bar.count

    def __iter__(self) -> Generator[dict, None, None]:
        if self.max_pages:
            self.logbar.total = self.max_pages
        else:
            self.count_pages()
        with bz2.BZ2File(self.file_path, "rb") as rf:
            context = etree.iterparse(rf, tag=self.xmlns + "page")
            for idx, (_, element) in enumerate(context):
                if self.max_pages and idx >= self.max_pages:
                    break
                page_dict = self.converter.convert(element)
                self.update_logbar(page_dict)
                yield page_dict
