# Student Records

A small web application for recording student names, ages, genders, and marks. Student records are stored in PostgreSQL.

## Run with Docker Compose

1. Install Docker Desktop and start it.
2. From this directory, run:

   ```sh
   docker compose up
   ```

3. Open [http://localhost:5000](http://localhost:5000).
4. Stop the app with `Ctrl+C`. Run `docker compose down` to stop and remove the containers. The database data remains in the `postgres_data` volume.

The app validates names, ages from 1 to 120, and marks from 0 to 100. Gender is selected from the options in the form.

The web service uses the official Python image directly. Compose mounts the app files into the container and installs the packages from `requirements.txt` when the service starts; there is no Dockerfile.

For local use, the Compose file supplies default PostgreSQL credentials. Set `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` in your environment before starting Compose to override them. Keep credentials private and use strong values outside local development.
