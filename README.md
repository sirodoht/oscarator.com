# oscarator.com

Share your Oscar predictions.

## Development

This is a standard [Django](https://docs.djangoproject.com/) application with
[uv](https://github.com/astral-sh/uv).

1. Setup environment variables with:

```sh
cp .envrc.example .envrc
source .envrc
```

2. Create database tables with:

```sh
uv run manage.py migrate
```

3. Run development server with:

```sh
uv run manage.py runserver
```

## Format and lint

Run Python formatting with:

```sh
uv run ruff format
```

Run Python linting with:

```sh
uv run ruff check --fix
```

## Add entries for a new year

When a new Oscar season begins, follow these steps to add nominations:

### 1. Prepare Data CSV

Create a CSV file with nomination data in `import_imdb/data.csv` format:

```csv
category, title, pic_url, imdb_code
Best Picture, Movie Title, entries/2027/tt12345678.jpeg, tt12345678
Actor in a Leading Role, Actor Name • Movie Title, entries/2027/tt12345678.jpeg, tt12345678
```

**Required columns:**

* `category` - Award category name (e.g., "Best Picture", "Actor in a Leading Role")
* `title` - Movie title or "Actor Name • Movie Title" for acting categories
* `pic_url` - Path where the poster image will be stored
* `imdb_code` - IMDB ID (e.g., tt12345678)

### 2. Download Poster Images

Find IMDB links of each movie, add them in `import_imdb/links.txt` format (each on a new line).

Use the scraper script to download poster images from IMDB:

```sh
uv run import_imdb/scrape_imdb.py -f import_imdb/links.txt --save-posters
```

This will create an `out_images` directory with poster images named by IMDB ID (e.g., `tt12345678.jpg`).

Minify images (right click -> Quick Actions -> Convert Image -> Medium on macOS) so that they load
fast. We aim for < 10 MB per year.

Move the downloaded images to `main/static/entries/YEAR/` directory.

### 3. Check and Create Categories

Verify that all categories from the CSV exist in the database:

```sh
uv run manage.py checkcategories import_imdb/data.csv
```

### 4. Import Entries

Import all entries from the CSV file:

```sh
# First, do a dry run, see what would be imported
uv run manage.py importentries import_imdb/data.csv --year 2026 --dry-run

# Then, actually import the entries
uv run manage.py importentries import_imdb/data.csv --year 2026
```

The import command will:

* Validate all categories exist
* Show a summary of entries by category
* Report any errors in the CSV data
* Create entries in the database

## Deploy

Every commit on branch `main` auto-deploys using GitHub Actions. To deploy manually:

```sh
cd ansible/
cp .envrc.example .envrc
uv run ansible-playbook playbook.yaml -v
```

## License

This software is licensed under the MIT license. For more information, read the
[LICENSE](LICENSE) file.
