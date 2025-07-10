# 📘 API Membres (`/api/v1/member/`)

---

## 🔹 Liste des membres

- **URL** : `http://127.0.0.1:8000/api/v1/member/all/`
- **Méthode HTTP** : `GET`
- **Réponse (format JSON)** :

```json
{
  "dataset": [
    {
      "id": 2,
      "image": "test",
      "email": "test@example.com",
      "type": "ADMIN",
      "first_name": "test",
      "last_name": "test",
      "telnumber": "0320000000",
      "password": "motdepasse123",
      "active_notification": true,
      "udid": "abc123",
      "login_date": null,
      "is_valid_email": true,
      "updated_at": "2025-07-10T17:05:39.861009Z",
      "created_at": "2025-07-10T17:04:55.504050Z"
    }
  ],
  "pagination": {
    "per_page": 12,
    "current_page": 1,
    "total_count": 1,
    "total_pages": 1
  }
}
```

---

## 🟢 Créer un membre

- **URL** : `http://127.0.0.1:8000/api/v1/member/create/`
- **Méthode HTTP** : `POST`
- **Requête (format JSON)** :

```json
{
  "image": "str",
  "email": "juliofaralahy23.com",
  "type": "USER",
  "first_name": "Julio",
  "last_name": "FARALAHY",
  "telnumber": "0320000000",
  "password": "12345678",
  "active_notification": true,
  "udid": "abc123",
  "is_valid_email": true
}
```

---

## 🟡 Modifier un membre

- **URL** : `http://127.0.0.1:8000/api/v1/member/{id}/`
- **Méthode HTTP** : `PUT`
- **Requête (format JSON)** :

```json
{
  "image": "str",
  "email": "juliofaralahy23.com",
  "type": "USER",
  "first_name": "Julio",
  "last_name": "FARALAHY",
  "telnumber": "0320000000",
  "password": "12345678",
  "active_notification": true,
  "udid": "abc123",
  "is_valid_email": true
}
```

---

## 🔍 Consulter un membre

- **URL** : `http://127.0.0.1:8000/api/v1/member/{id}/`
- **Méthode HTTP** : `GET`
- **Réponse (format JSON)** :

```json
{
  "id": 2,
  "image": "str",
  "email": "juliofaralahy23.com",
  "type": "USER",
  "first_name": "Julio",
  "last_name": "FARALAHY",
  "telnumber": "0320000000",
  "password": "12345678",
  "active_notification": true,
  "udid": "abc123",
  "login_date": null,
  "is_valid_email": true,
  "updated_at": "2025-07-10T17:05:39.861009Z",
  "created_at": "2025-07-10T17:04:55.504050Z"
}
```

---