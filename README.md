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

## Importing entries

To bulk import movie entries from a CSV file, use the `import_entries.py` script:

```sh
uv run python import_entries.py <csv_file> <category_name>
```

To preview what would be imported without making changes, use the `--dry-run` flag:

```sh
uv run python import_entries.py <csv_file> <category_name> --dry-run
```

The CSV file should have columns: `year`, `title`, `imdb_code`, and `pic_url`. For example:

```csv
year,title,imdb_code,pic_url
2026,The Brutalist,tt14905854,https://m.media-amazon.com/images/M/...
2026,Anora,tt28607951,https://m.media-amazon.com/images/M/...
```

The script will:

- Download each image from `pic_url`
- Save it to `main/static/entries/{year}/`
- Create a database entry in the specified category

## Format and lint

Run Python formatting with:

```sh
uv run ruff format
```

Run Python linting with:

```sh
uv run ruff check --fix
```

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
