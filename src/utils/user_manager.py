import json
import bcrypt
import os


BASE_DIR = os.path.dirname(__file__)
FILE_PATH = os.path.join(BASE_DIR, "users.json")


def load_users():
    # se não existir, cria
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "w") as f:
            json.dump({"users": []}, f, indent=4)

    # se estiver vazio
    if os.path.getsize(FILE_PATH) == 0:
        return {"users": []}

    try:
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"users": []}


def save_users(data):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)


def add_user(username, password, role="user"):
    data = load_users()
    for user in data["users"]:
        if user["username"] == username:
            return False, "Utilizador já existe."
    if len(password.encode()) > 72:
        return False, "Password demasiado longa (máx 72 caracteres)."

    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    data["users"].append({
        "username": username,
        "password": hashed,
        "role": role
    })

    save_users(data)
    return True, "Conta criada com sucesso."


def authenticate(username, password):
    data = load_users()

    for user in data["users"]:
        if user["username"] == username:
            if bcrypt.checkpw(
                password.encode(),
                user["password"].encode()
            ):
                return user

    return None


def delete_user(username):
    data = load_users()

    users_before = len(data["users"])
    data["users"] = [u for u in data["users"] if u["username"] != username]

    if len(data["users"]) == users_before:
        return False, "Utilizador não encontrado."

    save_users(data)
    return True, f"Utilizador '{username}' eliminado."


def change_role(username, new_role):
    if new_role not in ("user", "admin"):
        return False, "Role inválido."

    data = load_users()

    for user in data["users"]:
        if user["username"] == username:
            user["role"] = new_role
            save_users(data)
            return True, f"Role de '{username}' alterado para '{new_role}'."

    return False, "Utilizador não encontrado."
