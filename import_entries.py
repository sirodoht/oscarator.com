#!/usr/bin/env python3
"""
Script to import entries from a CSV file.

CSV format: year,title,imdb_code,pic_url
Example: 2026,The Brutalist,tt14138650,https://example.com/image.jpg

Usage:
    python import_entries.py <csv_file> <category_name> [--dry-run]

Example:
    python import_entries.py entries_2026.csv "Best Picture"
    python import_entries.py entries_2026.csv "Best Picture" --dry-run
"""

import argparse
import csv
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import django
import httpx

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oscarator.settings")
django.setup()

# ruff: noqa: E402
from main.models import Category, Entry


def download_image(url, destination_path, dry_run=False):
    """Download an image from URL and save it to destination_path."""
    if dry_run:
        print(f"  [DRY RUN] Would download to: {destination_path.name}")
        return True

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url)
            response.raise_for_status()

            with open(destination_path, "wb") as f:
                f.write(response.content)

        print(f"  ✓ Downloaded: {destination_path.name}")
        return True
    except httpx.HTTPError as e:
        print(f"  ✗ Failed to download {url}: {e}")
        return False


def get_image_filename(url, imdb_code):
    """
    Extract filename from URL or generate one from IMDB code.
    Priority: use URL filename if available, otherwise use imdb_code.
    """
    parsed = urlparse(url)
    path = parsed.path

    # Get filename from URL
    filename = os.path.basename(path)

    # If no filename in URL or it's generic, use IMDB code
    if not filename or "." not in filename:
        # Try to get extension from URL or default to .jpg
        ext = ".jpg"
        if "." in filename:
            ext = os.path.splitext(filename)[1]
        filename = f"{imdb_code}{ext}"

    return filename


def import_entries(csv_file, category_name, dry_run=False):
    """
    Import entries from a CSV file.

    Args:
        csv_file: Path to CSV file with columns: year,title,imdb_code,pic_url
        category_name: Name of the category to assign to all entries
        dry_run: If True, only show what would be done without making changes
    """

    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")

    # Verify category exists
    try:
        category = Category.objects.get(name=category_name)
        print(f"Using category: {category_name}")
    except Category.DoesNotExist:
        print(f"Error: Category '{category_name}' does not exist in the database.")
        print("\nAvailable categories:")
        for cat in Category.objects.all():
            print(f"  - {cat.name}")
        return

    # Read CSV
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found.")
        return

    entries_to_import = []
    with open(csv_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Check if required columns exist
        required_columns = {"year", "title", "imdb_code", "pic_url"}
        if not required_columns.issubset(set(reader.fieldnames)):
            print(f"Error: CSV must have columns: {', '.join(required_columns)}")
            print(f"Found columns: {', '.join(reader.fieldnames)}")
            return

        for row in reader:
            entries_to_import.append(
                {
                    "year": int(row["year"]),
                    "title": row["title"],
                    "imdb_code": row["imdb_code"],
                    "pic_url": row["pic_url"],
                }
            )

    print(f"\nFound {len(entries_to_import)} entries to import\n")

    # Process each entry
    for i, entry_data in enumerate(entries_to_import, 1):
        year = entry_data["year"]
        title = entry_data["title"]
        imdb_code = entry_data["imdb_code"]
        pic_url = entry_data["pic_url"]

        print(f"[{i}/{len(entries_to_import)}] Processing: {title} ({year})")

        # Create year directory if it doesn't exist
        year_dir = BASE_DIR / "main" / "static" / "entries" / str(year)
        year_dir.mkdir(parents=True, exist_ok=True)

        # Determine image filename
        image_filename = get_image_filename(pic_url, imdb_code)
        image_path = year_dir / image_filename

        # Download image
        if image_path.exists():
            print(f"  ℹ Image already exists: {image_filename}")
        else:
            success = download_image(pic_url, image_path, dry_run=dry_run)
            if not success and not dry_run:
                print("  ⚠ Skipping database insert due to download failure")
                continue

        # Create relative path for database (from static/)
        relative_pic_url = f"entries/{year}/{image_filename}"

        # Check if entry already exists
        existing_entry = Entry.objects.filter(
            year=year, name=title, category=category
        ).first()

        if existing_entry:
            print(f"  ℹ Entry already exists in database: {title}")
            # Update pic_url and imdb if needed
            if existing_entry.pic_url != relative_pic_url:
                if dry_run:
                    print("  [DRY RUN] Would update pic_url")
                else:
                    existing_entry.pic_url = relative_pic_url
                    existing_entry.save()
                    print("  ✓ Updated pic_url")
            if existing_entry.imdb != imdb_code:
                if dry_run:
                    print("  [DRY RUN] Would update imdb code")
                else:
                    existing_entry.imdb = imdb_code
                    existing_entry.save()
                    print("  ✓ Updated imdb code")
        else:
            # Create new entry
            if dry_run:
                print("  [DRY RUN] Would create database entry")
            else:
                Entry.objects.create(
                    category=category,
                    name=title,
                    pic_url=relative_pic_url,
                    imdb=imdb_code,
                    is_winner=False,
                    year=year,
                )
                print("  ✓ Created database entry")

        print()

    if dry_run:
        print(f"\n✅ DRY RUN complete! Reviewed {len(entries_to_import)} entries.")
        print("Run without --dry-run to apply changes.")
    else:
        print(f"\n✅ Import complete! Processed {len(entries_to_import)} entries.")


def main():
    parser = argparse.ArgumentParser(
        description="Import movie entries from a CSV file into the Oscarator database.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python import_entries.py entries_2026.csv "Best Picture"
  python import_entries.py entries_2026.csv "Best Picture" --dry-run

CSV format:
  year,title,imdb_code,pic_url
  2026,The Brutalist,tt14138650,https://example.com/image.jpg
        """,
    )
    parser.add_argument("csv_file", help="Path to CSV file with entry data")
    parser.add_argument("category_name", help="Category name for the entries")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making any changes",
    )

    args = parser.parse_args()

    # Show available categories if requested or on error
    if not args.csv_file or not args.category_name:
        print("\nAvailable categories:")
        for cat in Category.objects.all():
            print(f"  - {cat.name}")
        sys.exit(1)

    import_entries(args.csv_file, args.category_name, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
