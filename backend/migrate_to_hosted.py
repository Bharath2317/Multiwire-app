"""Copy wires and entries from the source database into a target database.

Source: whatever backend/.env points at (your SQL Server), or SOURCE_DATABASE_URL.
Target: TARGET_DATABASE_URL (e.g. your hosted Postgres connection string).

    set TARGET_DATABASE_URL=postgresql://user:pass@host/db      (PowerShell: $env:TARGET_DATABASE_URL="...")
    python migrate_to_hosted.py            # dry run: shows what would be copied
    python migrate_to_hosted.py --apply    # actually copy

The source is only read. Wires whose multiwire_no already exists in the target are
skipped together with their entries, so re-running is safe.
"""
import os
import sys

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from config import Config
from models import db
from models.entry import Entry
from models.wire import Wire


def _normalize(url):
    return "postgresql://" + url[len("postgres://"):] if url.startswith("postgres://") else url


def _values(row, model, skip):
    return {
        c.key: getattr(row, c.key)
        for c in model.__table__.columns
        if c.key not in skip
    }


def main(apply):
    target_url = os.getenv("TARGET_DATABASE_URL")
    if not target_url:
        sys.exit("Set TARGET_DATABASE_URL to the hosted database connection string.")

    source_url = os.getenv("SOURCE_DATABASE_URL") or Config.SQLALCHEMY_DATABASE_URI
    source = create_engine(_normalize(source_url))
    target = create_engine(_normalize(target_url), pool_pre_ping=True)

    if source.url == target.url:
        sys.exit("Source and target are the same database; refusing to continue.")

    db.metadata.create_all(target)

    copied_wires = copied_entries = skipped = 0
    with Session(source) as src, Session(target) as dst:
        existing = set(dst.scalars(select(Wire.multiwire_no)))

        for wire in src.scalars(select(Wire).order_by(Wire.id)):
            entries = list(
                src.scalars(
                    select(Entry).where(Entry.wire_id == wire.id).order_by(Entry.id)
                )
            )
            if wire.multiwire_no in existing:
                print(f"skip   {wire.multiwire_no} (already in target)")
                skipped += 1
                continue

            print(f"copy   {wire.multiwire_no}  [{wire.status}]  {len(entries)} entries")
            new_wire = Wire(**_values(wire, Wire, skip={"id"}))
            dst.add(new_wire)
            dst.flush()  # assigns the new id
            for e in entries:
                dst.add(Entry(wire_id=new_wire.id, **_values(e, Entry, skip={"id", "wire_id"})))
            copied_wires += 1
            copied_entries += len(entries)

        if apply:
            dst.commit()
        else:
            dst.rollback()

        total_wires = dst.scalar(select(func.count()).select_from(Wire))
        total_entries = dst.scalar(select(func.count()).select_from(Entry))

    verb = "Copied" if apply else "Would copy"
    print(f"\n{verb} {copied_wires} wires and {copied_entries} entries; skipped {skipped}.")
    if apply:
        print(f"Target now has {total_wires} wires and {total_entries} entries.")
    else:
        print("Dry run only. Re-run with --apply to write to the target.")


if __name__ == "__main__":
    main("--apply" in sys.argv)
