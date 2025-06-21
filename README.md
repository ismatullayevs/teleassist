# TeleAssist

**TeleAssist** is an AI-powered assistant for Telegram, featuring a FastAPI backend and a Telegram bot. The system uses PostgreSQL and MongoDB for data storage and is easy to run locally.

## Features

- Telegram Bot powered by AI
- FastAPI backend with RESTful APIs and admin panel
- PostgreSQL and MongoDB support
- Local development with Docker Compose

## Getting Started (Local Development)

### 1. Clone the repository

```sh
git clone <repo-url>
cd teleassist
```

### 2. Prepare environment variables

Copy the example environment file and edit it as needed:

```sh
cp example.env .env
```

Edit `.env` to set your secrets and configuration (e.g., Telegram bot token, database passwords, domain, etc).

#### Hashing the ADMIN_PASSWORD

For the admin panel, you need to provide a hashed password. You can generate it with:

```sh
echo $(htpasswd -nb admin yourpassword) | cut -d: -f2 | xargs
```

This command will output only the password hash (the part after the `$` sign). Copy the output and set it as the value for `ADMIN_PASSWORD` in your `.env` file.

### 3. Run the services locally

```sh
docker compose up --build
```

- The Telegram bot will start and connect to Telegram.
- The admin panel will be available at `http://api.localhost/admin`.
- The Traefik dashboard will be available at `http://traefik.localhost`.

### 4. User Registration and Whitelisting

To use the assistant:

- Users should first start the bot by sending the `/start` command in Telegram.
- After that, an admin must whitelist the user in the admin panel at `http://api.localhost/admin` before they can use the assistant's features.

## Project Structure

- `backend/` – FastAPI backend, admin, database models, API
- `bot/` – Telegram bot using aiogram, MongoDB integration
- `compose.yaml` – Docker Compose configuration
- `example.env` – Example environment variables

## License

MIT License
