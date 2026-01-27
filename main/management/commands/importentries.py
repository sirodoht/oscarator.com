"""
Django management command to import entries from CSV file.

Usage:
    uv run manage.py importentries import_imdb/data.csv --year 2026
    uv run manage.py importentries import_imdb/data.csv --year 2026 --dry-run
"""

import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from main.models import Category, Entry


class Command(BaseCommand):
    help = "Import entries from CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to the CSV file containing entry data",
        )
        parser.add_argument(
            "--year",
            "-y",
            type=int,
            required=True,
            help="Year for the entries (e.g., 2026)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be imported without actually importing",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_file"])
        year = options["year"]
        dry_run = options["dry_run"]

        # Validate CSV file exists
        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        # Validate year
        if year < 1900 or year > 2100:
            raise CommandError(f"Invalid year: {year}")

        self.stdout.write(f"Reading CSV file: {csv_path}")
        self.stdout.write(f"Target year: {year}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING("DRY RUN MODE - No changes will be made")
            )

        # Check for existing entries
        existing_count = Entry.objects.filter(year=year).count()
        if existing_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠ Found {existing_count} existing entries for year {year}"
                )
            )
            self.stdout.write("These entries will be added alongside existing ones\n")

        # Parse CSV and collect entries
        entries_to_create = []
        errors = []
        categories_cache = {}

        try:
            with open(csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f, skipinitialspace=True)
                # Normalize field names by stripping whitespace
                reader.fieldnames = [field.strip() for field in reader.fieldnames]

                for line_num, row in enumerate(
                    reader, start=2
                ):  # Start at 2 (header is line 1)
                    try:
                        category_name = row.get("category", "").strip()
                        title = row.get("title", "").strip()
                        pic_url = row.get("pic_url", "").strip()
                        imdb_code = row.get("imdb_code", "").strip()

                        if not category_name:
                            errors.append(f"Line {line_num}: Missing category")
                            continue

                        if not title:
                            errors.append(f"Line {line_num}: Missing title")
                            continue

                        # Get or cache category
                        if category_name not in categories_cache:
                            try:
                                category = Category.objects.get(name=category_name)
                                categories_cache[category_name] = category
                            except Category.DoesNotExist:
                                errors.append(
                                    f"Line {line_num}: Category '{category_name}' does not exist"
                                )
                                continue

                        entry_data = {
                            "category": categories_cache[category_name],
                            "name": title,
                            "pic_url": pic_url,
                            "imdb": imdb_code,
                            "year": year,
                        }
                        entries_to_create.append(entry_data)

                    except Exception as e:
                        errors.append(f"Line {line_num}: {e}")

        except Exception as e:
            raise CommandError(f"Error reading CSV file: {e}") from e

        # Display errors if any
        if errors:
            self.stdout.write(self.style.ERROR(f"\n✗ Found {len(errors)} errors:"))
            for error in errors[:10]:  # Show first 10 errors
                self.stdout.write(f"  {error}")
            if len(errors) > 10:
                self.stdout.write(f"  ... and {len(errors) - 10} more errors")
            self.stdout.write("")

        # Display summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("SUMMARY")
        self.stdout.write("=" * 60)
        self.stdout.write(
            f"Total rows processed: {len(entries_to_create) + len(errors)}"
        )
        self.stdout.write(f"Valid entries: {len(entries_to_create)}")
        self.stdout.write(f"Errors: {len(errors)}")

        if not entries_to_create:
            self.stdout.write(self.style.WARNING("\nNo valid entries to import"))
            return

        # Show breakdown by category
        category_counts = {}
        for entry_data in entries_to_create:
            cat_name = entry_data["category"].name
            category_counts[cat_name] = category_counts.get(cat_name, 0) + 1

        self.stdout.write("\nEntries by category:")
        for cat_name, count in sorted(category_counts.items()):
            self.stdout.write(f"  {cat_name}: {count}")

        # Create entries
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\nDRY RUN: Would create {len(entries_to_create)} entries"
                )
            )
        else:
            self.stdout.write(f"\nCreating {len(entries_to_create)} entries...")
            created_count = 0
            failed_count = 0

            for entry_data in entries_to_create:
                try:
                    Entry.objects.create(**entry_data)
                    created_count += 1
                except Exception as e:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ Error creating entry '{entry_data['name']}': {e}"
                        )
                    )

            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created {created_count} entries")
            )
            if failed_count > 0:
                self.stdout.write(
                    self.style.ERROR(f"Failed to create {failed_count} entries")
                )
            self.stdout.write("=" * 60)
