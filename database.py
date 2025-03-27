import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CREDENTIALS

cred = credentials.Certificate(FIREBASE_CREDENTIALS)
firebase_admin.initialize_app(cred)

db = firestore.client()

def create_tables():
    try:
        users_ref = db.collection('users')
        vacancies_ref = db.collection('vacancies')
        print("Таблицы успешно созданы.")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")

def add_user(user_id, name):
    try:
        user_ref = db.collection('users').document(str(user_id))
        user_ref.set({
            'name': name,
            'phone': ''
        })
    except Exception as e:
        print(f"Ошибка при добавлении пользователя: {e}")

def update_user_phone(user_id, phone):
    try:
        user_ref = db.collection('users').document(str(user_id))
        user_ref.update({'phone': phone})
    except Exception as e:
        print(f"Ошибка при обновлении номера телефона: {e}")

def add_vacancy(title, description, category):
    try:
        vacancy_ref = db.collection('vacancies').document()
        vacancy_ref.set({
            'title': title,
            'description': description,
            'category': category
        })
    except Exception as e:
        print(f"Ошибка при добавлении вакансии: {e}")

def get_vacancies_by_category_paginated(category, last_doc=None, limit=5):
    try:
        vacancies_ref = db.collection('vacancies').where('category', '==', category)
        
        if last_doc:
            vacancies_ref = vacancies_ref.start_after(last_doc).limit(limit)
        else:
            vacancies_ref = vacancies_ref.limit(limit)
            
        vacancies = vacancies_ref.stream()
        
        result = []
        last_document = None
        
        for vacancy in vacancies:
            data = vacancy.to_dict()
            result.append((vacancy.id, data['title'], data['description'], data['category']))
            last_document = vacancy
            
        return result, last_document
        
    except Exception as e:
        print(f"Ошибка при получении вакансий: {e}")
        return [], None

def get_vacancy_by_id(vacancy_id):
    try:
        vacancy_ref = db.collection('vacancies').document(vacancy_id).get()
        if vacancy_ref.exists:
            data = vacancy_ref.to_dict()
            return (vacancy_ref.id, data['title'], data['description'], data['category'])
        else:
            return None
    except Exception as e:
        print(f"Ошибка при получении вакансии по ID: {e}")
        return None

def get_user(user_id):
    try:
        user_ref = db.collection('users').document(str(user_id)).get()
        if user_ref.exists:
            return user_ref.to_dict()
        else:
            return None
    except Exception as e:
        print(f"Ошибка при получении пользователя: {e}")
        return None

def get_all_vacancies():
    try:
        vacancies_ref = db.collection('vacancies').stream()
        vacancies = [
            (vacancy.id, vacancy.to_dict()['title'], vacancy.to_dict()['description'], vacancy.to_dict()['category'])
            for vacancy in vacancies_ref
        ]
        return vacancies
    except Exception as e:
        print(f"Ошибка при получении всех вакансий: {e}")
        return []