"""
Django management command to check and create categories from CSV file.

Usage:
    uv run manage.py checkcategories import_imdb/data.csv
    uv run manage.py checkcategories import_imdb/data.csv --yes
"""

import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from main.models import Category


class Command(BaseCommand):
    help = "Check if all categories from CSV exist, and optionally create missing ones"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to the CSV file containing category data",
        )
        parser.add_argument(
            "--yes",
            "-y",
            action="store_true",
            help="Automatically create all missing categories without prompting",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_file"])
        auto_yes = options["yes"]

        # Validate CSV file exists
        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        self.stdout.write(f"Reading CSV file: {csv_path}")

        # Parse CSV and collect unique categories
        categories_in_csv = set()
        try:
            with open(csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f, skipinitialspace=True)
                # Normalize field names by stripping whitespace
                reader.fieldnames = [field.strip() for field in reader.fieldnames]
                for row in reader:
                    # Strip whitespace from category name
                    category = row.get("category", "").strip()
                    if category:
                        categories_in_csv.add(category)
        except Exception as e:
            raise CommandError(f"Error reading CSV file: {e}") from e

        if not categories_in_csv:
            self.stdout.write(self.style.WARNING("No categories found in CSV file"))
            return

        self.stdout.write(
            f"\nFound {len(categories_in_csv)} unique categories in CSV file:"
        )
        for cat in sorted(categories_in_csv):
            self.stdout.write(f"  - {cat}")

        # Check which categories exist in database
        existing_categories = set(
            Category.objects.filter(name__in=categories_in_csv).values_list(
                "name", flat=True
            )
        )

        if existing_categories:
            self.stdout.write(
                f"\n{self.style.SUCCESS('✓')} {len(existing_categories)} categories already exist:"
            )
            for cat in sorted(existing_categories):
                self.stdout.write(f"  - {cat}")

        # Find missing categories
        missing_categories = categories_in_csv - existing_categories

        if not missing_categories:
            self.stdout.write(
                f"\n{self.style.SUCCESS('All categories already exist in database!')}"
            )
            return

        # Handle missing categories
        self.stdout.write(
            f"\n{self.style.WARNING('⚠')} {len(missing_categories)} categories are missing:"
        )
        for cat in sorted(missing_categories):
            self.stdout.write(f"  - {cat}")

        # Ask for confirmation for each category (unless --yes is provided)
        categories_to_create = []

        if auto_yes:
            categories_to_create = list(missing_categories)
            self.stdout.write(
                f"\n{self.style.WARNING('Auto-creating all missing categories...')}"
            )
        else:
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("Would you like to create the missing categories?")
            self.stdout.write("=" * 60)

            for category in sorted(missing_categories):
                answer = input(f"\nCreate category '{category}'? [y/N]: ").lower()
                if answer in ["y", "yes"]:
                    categories_to_create.append(category)
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✓ Will create: {category}")
                    )
                else:
                    self.stdout.write(self.style.WARNING(f"  ✗ Skipping: {category}"))

        # Create the categories
        if not categories_to_create:
            self.stdout.write(f"\n{self.style.WARNING('No categories were created')}")
            return

        created_count = 0
        for category_name in categories_to_create:
            try:
                Category.objects.create(name=category_name)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created category: {category_name}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Error creating '{category_name}': {e}")
                )

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {created_count} out of {len(categories_to_create)} categories"
            )
        )
        self.stdout.write("=" * 60)
