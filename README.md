# Volleyball Player List — EECE 430 Assignment 4

A Django web application to manage a list of volleyball players, supporting full CRUD operations (Create, Read, Update, Delete).

---

## Project Structure

```
PhilippeDoumet_hw4_202303965/
├── manage.py                   # Django entry point
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image definition
├── .dockerignore               # Files excluded from Docker build
├── .gitignore                  # Files excluded from Git
│
├── volley_project/             # Django project configuration
│   ├── settings.py             # App settings (DB, installed apps, etc.)
│   ├── urls.py                 # Root URL routing
│   ├── wsgi.py                 # WSGI entry point
│   └── asgi.py                 # ASGI entry point
│
└── players/                    # Django app — core logic
    ├── models.py               # Player data model
    ├── views.py                # Class-based views (List, Create, Update, Delete)
    ├── urls.py                 # App-level URL patterns
    ├── forms.py                # Player form definition
    ├── admin.py                # Django admin registration
    ├── migrations/             # Database migration files
    └── templates/players/      # HTML templates
        ├── base.html           # Base layout template
        ├── player_list.html    # Lists all players
        ├── player_form.html    # Create / Edit form
        └── player_confirm_delete.html  # Delete confirmation page
```

---

## Player Model

| Field | Type | Description |
|---|---|---|
| `name` | CharField | Player's full name |
| `date_joined` | DateField | Date the player joined |
| `position` | CharField | Playing position |
| `salary` | DecimalField | Player salary |
| `contact_person` | CharField | Emergency / contact name |

---

## URL Routes

| URL | View | Description |
|---|---|---|
| `/` | `PlayerListView` | List all players |
| `/new/` | `PlayerCreateView` | Add a new player |
| `/<id>/edit/` | `PlayerUpdateView` | Edit an existing player |
| `/<id>/delete/` | `PlayerDeleteView` | Delete a player |
| `/admin/` | Django Admin | Admin dashboard |

---

## Running Locally (without Docker)

**Prerequisites:** Python 3.12+

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations
python manage.py migrate

# 4. Start the development server
python manage.py runserver
```

Open your browser at `http://localhost:8000`.

---

## Running with Docker

### Option 1 — Build and run locally

```bash
# Build the image
docker build -t volleyball-app .

# Run the container
docker run -p 8000:8000 volleyball-app
```

### Option 2 — Pull and run from GitHub Container Registry

```bash
# Pull the image
docker pull ghcr.io/philippedoumet/eece430sp25-26group20:latest

# Run the container
docker run -p 8000:8000 ghcr.io/philippedoumet/eece430sp25-26group20:latest
```

Open your browser at `http://localhost:8000`.

To stop the container:
```bash
docker stop $(docker ps -q --filter ancestor=ghcr.io/philippedoumet/eece430sp25-26group20:latest)
```

---

## GitHub Repository

[https://github.com/philippedoumet/EECE430Sp25-26Group20](https://github.com/philippedoumet/EECE430Sp25-26Group20)

## Docker Image

`ghcr.io/philippedoumet/eece430sp25-26group20:latest`

---

## Author

Philippe Doumet — 202303965
