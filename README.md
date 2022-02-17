# oscarator.com

Share your Oscar predictions.

## Development

This is a [Django](https://www.djangoproject.com/) codebase. Check out the
[Django docs](https://docs.djangoproject.com/) for general technical
documentation.

### Structure

The Django project is `oscarator`. There is one Django app, `main`, with all
business logic. Application CLI commands are generally divided into two
categories, those under `python manage.py` and those under `make`.

### Dependencies

This project is configured using Nix and direnv and venv. After cd-ing into it:

```sh
pip install -r requirements_dev.txt
```

Or for production use:

```
pip install -r requirements.txt
```

This project also uses [pip-tools](https://github.com/jazzband/pip-tools) for
dependency management.

### Serve

To run the Django development server:

```sh
python manage.py runserver
```

### Environment variables

One can create a new file named `.envrc` in the root of this project. An example
of what this file should look like exists, named `.envrc.example`.

These are the environment variables supported. The only one that is required
is the database URL.

```
DATABASE_URL=postgres://username:password@localhost:5432/oscarator
SECRET_KEY=thisisthesecretkey
EMAIL_HOST_USER=smtp_user
EMAIL_HOST_PASSWORD=smtp_password
DEBUG=1
```

### Database

This project uses PostgreSQL. See above on how to configure it using the
`.envrc` file.

After creating your local database, you need to apply the migrations:

```sh
python manage.py migrate
```

## Code linting & formatting

The following tools are used for code linting and formatting:

* [black](https://github.com/psf/black) for code formatting.
* [isort](https://github.com/pycqa/isort) for imports order consistency.
* [flake8](https://gitlab.com/pycqa/flake8) for code linting.

To use:

```sh
make format
make lint
```

## License

This software is licensed under the MIT license. For more information, read the
[LICENSE](LICENSE) file.
