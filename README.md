# oscarator.com

> Share your Oscar predictions.

## Development

This is a [Django](https://www.djangoproject.com/) codebase. Check out the [Django docs](https://docs.djangoproject.com/) for general technical documentation.

### Structure

The Django project is [`oscarator`](/oscarator). There is one Django app, [`main`](/main) Django app, with all business logic.

### Dependencies

Create virtualenv, enable it and then install requirements:
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> Note: This project uses [pip-tools](https://github.com/jazzband/pip-tools) for dependencies management.

### Environment variables

You need to create a new file named `.env` in the root of this project once you cloned it.

`.env` should contain the following env variables:
```
SECRET_KEY="thisisthesecretkey"
DATABASE_URL="postgres://username:password@localhost:5432/db_name"
EMAIL_HOST_USER="smtp_user"
EMAIL_HOST_PASSWORD="smtp_password"
```

### Database

This project uses PostgreSQL. See above on how to configure it using the `.env` file.

> [How to: Create PostgreSQL DB](https://gist.github.com/sirodoht/0666e232e1baf76f76bac43eb2600e2b)

After creating your local database, you need to apply the migrations:
```sh
python manage.py migrate
```

### Serve

Finally, you can run the Django development server:
```sh
python manage.py runserver
```

Or, run the production-grade `uwsgi` server:
```sh
uwsgi --ini=uwsgi.ini -H venv/
```

> Note: The `uwsgi` method does not read the `.env` file, so in this case you need to set the env vars in your shell.


## Code linting & formatting

```
black . && isort -y && flake8
```
