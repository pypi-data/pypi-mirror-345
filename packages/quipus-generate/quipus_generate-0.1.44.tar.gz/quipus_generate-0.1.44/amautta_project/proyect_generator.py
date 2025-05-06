import os

def create(name):

    estructura = [
        "nginx/ssl",
        "nginx/sites",
        "example_entity/app",
    ]

    archivos = {
        "README.md" : (
            "# Proyecto FastAPI\n"
            "Este es un proyecto FastAPI con arquitectura Hexagonal.\n"
            "## Crear un nuevo proyecto\n"
            "```bash\n"
            "quipus-generate init <nombre_proyecto>\n"
            "```\n"
            "## Crear un microservicio\n"
            "```bash\n"
            "quipus-generate microservice <nombre_microservicio> <nombre_entidad>\n"
            "```\n"
            "## Crear una entity\n"
            "```bash\n"
            "quipus-generate entity <nombre_entity>\n"
            "```\n"
            "## Ejecutar el projecto\n"
            "```bash\n"
            "docker-compose up --build --force-recreate -d\n"
            "```\n"
            "## Destruir el projecto\n"
            "```bash\n"
            "docker-compose down\n"
            "```\n"
            "\n"
            "# 📌 Guía de Comandos Alembic\n"
            "\n"
            "Alembic es una herramienta de migración de bases de datos para SQLAlchemy. Permite **crear, aplicar y revertir** cambios en la base de datos sin perder datos.\n"
            "\n"
            "## 📌 Tabla de Comandos Alembic\n"
            "\n"
            "| Comando | Descripción |\n"
            "|---------|------------|\n"
            "| `docker-compose exec <microservicio> alembic revision --autogenerate -m \"Descripción\"` | Crea una nueva migración detectando cambios automáticamente. |\n"
            "| `docker-compose exec <microservicio> alembic upgrade head` | Aplica todas las migraciones pendientes. |\n"
            "| `docker-compose exec <microservicio> alembic upgrade <revision_id>` | Aplica una migración específica. |\n"
            "| `docker-compose exec <microservicio> alembic downgrade -1` | Revierte la última migración aplicada. |\n"
            "| `docker-compose exec <microservicio> alembic downgrade <revision_id>` | Revierte a una versión específica. |\n"
            "| `docker-compose exec <microservicio> alembic downgrade base` | Elimina todas las migraciones y deja la base vacía. |\n"
            "| `docker-compose exec <microservicio> alembic history` | Lista todas las migraciones creadas. |\n"
            "| `docker-compose exec <microservicio> alembic current` | Muestra la versión de migración actualmente aplicada. |\n"
            "| `docker-compose exec <microservicio> alembic stamp head` | Marca todas las migraciones como aplicadas sin ejecutarlas. |\n"
        ),
        ".env" : (
            "SERVICE_PORT:5000\n"
            "\n"
            "POSTGRES_USER:postgres\n"
            "POSTGRES_PASSWORD:postgres\n"
            "POSTGRES_DB:quipusdb\n"
        ),
        "docker-compose.yaml": (
            "version: '3.8'\n"
            "services:\n"
            "  example:\n"
            "    build:\n"
            "      context: ./example_entity\n"
            "      dockerfile: Dockerfile\n"
            "    container_name: example-service\n"
            "    volumes:\n"
            "      - ./example_entity:/app\n"
            "    command: uvicorn app.main:run --host 0.0.0.0 --port ${SERVICE_PORT} --reload\n"
            "    networks:\n"
            "      - quipus-network\n"
            "    expose:\n"
            "      - ${SERVICE_PORT}\n"
            "    depends_on:\n"
            "      - db\n"
            "  nginx:\n"
            "    image: nginx:latest\n"
            "    container_name: nginx-proxy\n"
            "    ports:\n"
            "      - 80:80\n"
            "      - 443:443\n"
            "    volumes:\n"
            "      - ./nginx/sites:/etc/nginx/conf.d\n"
            "      - ./nginx/ssl:/etc/nginx/ssl\n"
            "    networks:\n"
            "      - quipus-network\n"
            "    depends_on:\n"
            "      - example\n"
            "  db:\n"
            "    image: postgres:latest\n"
            "    container_name: postgres-db\n"
            "    restart: always\n"
            "    environment:\n"
            "      POSTGRES_USER: ${POSTGRES_USER}\n"
            "      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}\n"
            "      POSTGRES_DB: ${POSTGRES_DB}\n"
            "    ports:\n"
            "      - 5432:5432\n"
            "    volumes:\n"
            "      - postgres_data:/var/lib/postgresql/data\n"
            "    networks:\n"
            "      - quipus-network\n"
            "networks:\n"
            "  quipus-network:\n"
            "    driver: bridge\n"
            "volumes:\n"
            "  postgres_data:\n"
            "    driver: local\n"

        ),
        "nginx/sites/example_entity.conf": (
            "server {\n"
            "    #listen 443 ssl;\n"
            "    listen 80;\n"
            "    server_name example_entity.app;\n"
            "    #ssl_certificate /etc/nginx/ssl/certificate.crt; # managed by Certbot\n"
            "    #ssl_certificate_key /etc/nginx/ssl/private.key; #\n"
            "\n"
            "    location / {\n"
            "        proxy_pass http://example:5000;\n"
            "        proxy_set_header Host $host;\n"
            "        proxy_set_header X-Real-IP $remote_addr;\n"
            "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n"
            "        proxy_set_header X-Forwarded-Proto $scheme;\n"
            "    }\n"
            "}\n"
        ),
        "example_entity/app/main.py" : (
            "from fastapi import FastAPI\n"
            "\n"
            "run = FastAPI()\n"
            "\n"
            "@run.get(\"/\")\n"
            "async def root():\n"
            "    return {\"message\": \"Hello World\"}\n"
            "\n"
        ),
        "example_entity/requirements.txt": (
            "fastapi==0.115.12\n"
            "pydantic==2.11.3\n"
            "pydantic_core==2.33.1\n"
            "python-dotenv==1.1.0\n"
            "uvicorn==0.34.0\n"
            "sqlalchemy\n"
            "sqlmodel\n"
            "alembic\n"
            "psycopg2-binary\n"
            "pydantic-settings\n"
            "\n"
        ),
        "example_entity/Dockerfile":(
            "FROM python:3.13.2-slim\n"
            "WORKDIR /app\n"
            "COPY . .\n"
            "RUN pip install --no-cache-dir -r requirements.txt\n"
            "EXPOSE 5000\n"
            "CMD [\"uvicorn\", \"app.main:run\", \"--host\", \"0.0.0.0\", \"--port\", \"5000\", \"--reload\"]\n"
        )
    }

    # Crear directorio base
    os.makedirs(name, exist_ok=True)

    # Crear subdirectorios
    for carpeta in estructura:
        os.makedirs(os.path.join(name, carpeta), exist_ok=True)

    # Crear archivos vacíos
    for archivo, content in archivos.items():
        ruta_archivo = os.path.join(name, archivo)
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"[OK] Proyecto '{name}' creado con exito.")