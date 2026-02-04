from __future__ import annotations

from pathlib import Path
import re
import xml.etree.ElementTree as ET

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from bible.models import BibleBook, BibleChapter, BibleVerse


# OSIS book code -> (slug, English name, order)  (OT only)
OT_BOOKS = [
    ("Gen", "gen", "Genesis", 1),
    ("Exod", "exod", "Exodus", 2),
    ("Lev", "lev", "Leviticus", 3),
    ("Num", "num", "Numbers", 4),
    ("Deut", "deut", "Deuteronomy", 5),
    ("Josh", "josh", "Joshua", 6),
    ("Judg", "judg", "Judges", 7),
    ("Ruth", "ruth", "Ruth", 8),
    ("1Sam", "1sam", "1 Samuel", 9),
    ("2Sam", "2sam", "2 Samuel", 10),
    ("1Kgs", "1kgs", "1 Kings", 11),
    ("2Kgs", "2kgs", "2 Kings", 12),
    ("1Chr", "1chr", "1 Chronicles", 13),
    ("2Chr", "2chr", "2 Chronicles", 14),
    ("Ezra", "ezra", "Ezra", 15),
    ("Neh", "neh", "Nehemiah", 16),
    ("Esth", "esth", "Esther", 17),
    ("Job", "job", "Job", 18),
    ("Ps", "ps", "Psalms", 19),
    ("Prov", "prov", "Proverbs", 20),
    ("Eccl", "eccl", "Ecclesiastes", 21),
    ("Song", "song", "Song of Solomon", 22),
    ("Isa", "isa", "Isaiah", 23),
    ("Jer", "jer", "Jeremiah", 24),
    ("Lam", "lam", "Lamentations", 25),
    ("Ezek", "ezek", "Ezekiel", 26),
    ("Dan", "dan", "Daniel", 27),
    ("Hos", "hos", "Hosea", 28),
    ("Joel", "joel", "Joel", 29),
    ("Amos", "amos", "Amos", 30),
    ("Obad", "obad", "Obadiah", 31),
    ("Jonah", "jonah", "Jonah", 32),
    ("Mic", "mic", "Micah", 33),
    ("Nah", "nah", "Nahum", 34),
    ("Hab", "hab", "Habakkuk", 35),
    ("Zeph", "zeph", "Zephaniah", 36),
    ("Hag", "hag", "Haggai", 37),
    ("Zech", "zech", "Zechariah", 38),
    ("Mal", "mal", "Malachi", 39),
]
BOOK_BY_OSIS = {osis: (slug, name, order) for (osis, slug, name, order) in OT_BOOKS}

WS_RE = re.compile(r"\s+")
SPACE_BEFORE_PUNCT_RE = re.compile(r"\s+([־׃])")


def clean_hebrew_text(raw: str) -> str:
    s = raw.replace("\u200f", "").replace("\u200e", "")  # bidi marks
    s = WS_RE.sub(" ", s).strip()
    s = SPACE_BEFORE_PUNCT_RE.sub(r"\1", s)
    return s


def parse_osis_id(osis_id: str) -> tuple[str, int, int]:
    # Expect e.g. 'Gen.1.1' or '1Sam.3.2'
    parts = osis_id.split(".")
    if len(parts) < 3:
        raise ValueError(osis_id)
    return parts[0], int(parts[1]), int(parts[2])


class Command(BaseCommand):
    help = "Import WLC OSIS XML (bible_data/morphhb/wlc) into BibleBook/BibleChapter/BibleVerse."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="bible_data/morphhb/wlc",
            help="Path to the morphhb 'wlc' folder containing OSIS XML files.",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing BibleBook/Chapter/Verse records before importing.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        wlc_path = Path(options["path"]).resolve()

        # Safety: only allow importing from a folder named 'wlc'
        if wlc_path.name.lower() != "wlc":
            raise CommandError(f"Refusing to import: path must end with '/wlc'. Got: {wlc_path}")

        if not wlc_path.exists() or not wlc_path.is_dir():
            raise CommandError(f"Folder not found: {wlc_path}")

        xml_files = sorted(wlc_path.glob("*.xml"))
        if not xml_files:
            raise CommandError(f"No .xml files found in: {wlc_path}")

        if options["reset"]:
            BibleVerse.objects.all().delete()
            BibleChapter.objects.all().delete()
            BibleBook.objects.all().delete()

        # Ensure OT books exist
        for osis, slug, name, order in OT_BOOKS:
            BibleBook.objects.get_or_create(
                osis=osis,
                defaults={"slug": slug, "name_en": name, "order": order},
            )

        created = 0
        for file_path in xml_files:
            try:
                tree = ET.parse(file_path)
            except ET.ParseError as e:
                raise CommandError(f"XML parse error in {file_path.name}: {e}")

            root = tree.getroot()

            # namespace-safe "endswith('verse')" search
            verse_elems = [
                el for el in root.iter()
                if el.tag.lower().endswith("verse") and el.attrib.get("osisID")
            ]

            if not verse_elems:
                self.stdout.write(self.style.WARNING(f"No verses found in {file_path.name}, skipping"))
                continue

            chapter_cache: dict[tuple[int, int], BibleChapter] = {}
            batch: list[BibleVerse] = []

            for el in verse_elems:
                osis_id = el.attrib.get("osisID", "")
                try:
                    book_osis, chap_num, verse_num = parse_osis_id(osis_id)
                except Exception:
                    continue

                if book_osis not in BOOK_BY_OSIS:
                    continue

                book = BibleBook.objects.get(osis=book_osis)

                ck = (book.id, chap_num)
                chap = chapter_cache.get(ck)
                if chap is None:
                    chap, _ = BibleChapter.objects.get_or_create(book=book, number=chap_num)
                    chapter_cache[ck] = chap

                text = clean_hebrew_text("".join(el.itertext()))
                if not text:
                    continue

                batch.append(BibleVerse(chapter=chap, number=verse_num, text=text))

                if len(batch) >= 2000:
                    BibleVerse.objects.bulk_create(batch, ignore_conflicts=True)
                    created += len(batch)
                    batch.clear()

            if batch:
                BibleVerse.objects.bulk_create(batch, ignore_conflicts=True)
                created += len(batch)

            self.stdout.write(self.style.SUCCESS(f"Imported {file_path.name}"))

        self.stdout.write(self.style.SUCCESS(f"Done. Inserted ~{created} verses (conflicts ignored)."))
