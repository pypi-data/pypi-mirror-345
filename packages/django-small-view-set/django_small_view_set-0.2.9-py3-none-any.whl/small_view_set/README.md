# Steps for Releasing to PyPI

1. **Environment variables**
   Copy the .env.example file to .env and set the real token from pypi

2. **Build the Docker Image**:
   ```bash
   docker compose build --no-cache
   docker compose up -d
   ```

3. **Install Dependencies**:
   - Install dependencies inside the container after mounting the directory:
     ```bash
     docker compose run --remove-orphans django-small-view-set-builder poetry install
     ```

4. **Run Tests**:
   - Run tests before releasing:
     ```bash
     docker compose run --remove-orphans django-small-view-set-builder python /app/tests/manage.py test
     ```

5. **Build the Package**:
   Inside the Docker container, build the package:
   ```bash
   docker compose run --remove-orphans django-small-view-set-builder poetry build
     ```

6. **Publish to PyPI**:
   Upload the package to PyPI:
   ```bash
   docker compose run --remove-orphans django-small-view-set-builder poetry publish
     ```

7. **Verify the Release**:
   - Visit your package page on PyPI to confirm the release.