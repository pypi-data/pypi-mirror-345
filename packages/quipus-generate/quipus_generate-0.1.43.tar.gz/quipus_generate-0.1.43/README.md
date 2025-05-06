# 🚀 quipus-generate

**quipus-generate** es una base de proyecto en Python que implementa una arquitectura **hexagonal** (puertos y adaptadores) con **FastAPI**, **PostgreSQL**, **SQLAlchemy** y **Alembic**. Está pensado para escalar y adaptarse a microservicios, con migraciones gestionadas por servicio.

---

## 📦 Características

- ✅ Arquitectura hexagonal (Domain Driven Design)
- 🔧 CRUD de entidades
- 🛢️ PostgreSQL como base de datos
- 🧱 SQLAlchemy como ORM
- 📜 Alembic para control de migraciones
- 🐳 Soporte para Docker y Docker Compose
- ⚙️ Configuración por entorno

---

# Comandos cli

## 🐳 Crear proyecto
```
quipus-generate init <nombre-del-proyecto>
```

## 🧩 Crear microservicio
```
quipus-generate microservice <microservicio> <entidad>
```

## 🐍 Crear entidad
```
quipus-generate entity <entidad>
```

