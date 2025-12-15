from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from datetime import datetime
import os
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'na1-carwash-secret-key-2024'

# --- Конфигурация файлов данных ---
DATA_DIR = 'data'
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
SERVICES_FILE = os.path.join(DATA_DIR, 'services.json')
REVIEWS_FILE = os.path.join(DATA_DIR, 'reviews.json')

# Создаем папку data если ее нет
os.makedirs(DATA_DIR, exist_ok=True)

# --- Функции для работы с данными ---
def load_data(file_path, default_data):
    """Загружает данные из JSON файла"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return default_data

def save_data(file_path, data):
    """Сохраняет данные в JSON файл"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def init_default_data():
    """Инициализирует файлы с данными по умолчанию"""
    default_settings = {
        'site_name': 'РОБОТ МОЙКА ГИДРА',
        'work_hours': {
            'monday': {'open': '08:00', 'close': '22:00', 'enabled': True},
            'tuesday': {'open': '08:00', 'close': '22:00', 'enabled': True},
            'wednesday': {'open': '08:00', 'close': '22:00', 'enabled': True},
            'thursday': {'open': '08:00', 'close': '22:00', 'enabled': True},
            'friday': {'open': '08:00', 'close': '22:00', 'enabled': True},
            'saturday': {'open': '09:00', 'close': '20:00', 'enabled': True},
            'sunday': {'open': '09:00', 'close': '20:00', 'enabled': True}
        },
        'contact_info': {
            'phone': '+7 (495) 123-45-67',
            'address': 'г. Москва, ул. Автомойщиков, 15',
            'email': 'info@na1-carwash.ru'
        },
        'social_links': {
            'vk': '#',
            'instagram': '#',
            'telegram': '#'
        }
    }
    
    default_services = [
        {
            'id': 1,
            'title': 'Стандартная мойка',
            'description': 'Комплексная наружная мойка кузова, колес и арок. Нанесение воска для защиты лакокрасочного покрытия.',
            'price': 'от 500 руб.',
            'image': 'https://images.unsplash.com/photo-1507136566006-cfc505b114fc?ixlib=rb-4.0.3&auto=format&fit=crop&w=1021&q=80'
        },
        {
            'id': 2,
            'title': 'Комплексная мойка',
            'description': 'Полная мойка кузова с шампунем, чистка колес, арок, порогов. Сушка и нанесение защитного полимера.',
            'price': 'от 1000 руб.',
            'image': 'https://images.unsplash.com/photo-1620706857370-e1b9770e8bb1?ixlib=rb-4.0.3&auto=format&fit=crop&w=1064&q=80'
        }
    ]
    
    default_reviews = [
        {
            'id': 1,
            'name': 'Александр Петров',
            'rating': 5,
            'text': 'Отличная автомойка! Быстро, качественно и по доступной цене. Персонал вежливый и профессиональный.',
            'date': '2 дня назад'
        }
    ]
    
    # Сохраняем данные по умолчанию если файлов нет
    if not os.path.exists(SETTINGS_FILE):
        save_data(SETTINGS_FILE, default_settings)
    
    if not os.path.exists(SERVICES_FILE):
        save_data(SERVICES_FILE, default_services)
    
    if not os.path.exists(REVIEWS_FILE):
        save_data(REVIEWS_FILE, default_reviews)

# Инициализируем данные
init_default_data()

# --- Загрузка данных ---
def get_settings():
    return load_data(SETTINGS_FILE, {})

def get_services():
    return load_data(SERVICES_FILE, [])

def get_reviews():
    return load_data(REVIEWS_FILE, [])

# --- Декоратор для проверки авторизации ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Требуется авторизация', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ГЛАВНЫЕ МАРШРУТЫ САЙТА ====================
@app.route('/')
def index():
    current_year = datetime.now().year
    settings = get_settings()
    reviews = get_reviews()
    return render_template('index.html', current_year=current_year, settings=settings, reviews=reviews)

@app.route('/services')
def services():
    current_year = datetime.now().year
    settings = get_settings()
    services_data = get_services()
    return render_template('services.html', current_year=current_year, settings=settings, services=services_data)

@app.route('/submit_form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        message = request.form.get('message', '').strip()
        
        if name and phone:
            print(f"Новая заявка: {name}, {phone}")
            if message:
                print(f"Сообщение: {message}")
            flash(f'Спасибо, {name}! Ваша заявка принята. Мы свяжемся с вами в ближайшее время.', 'success')
        else:
            flash('Пожалуйста, заполните имя и телефон', 'error')
        
        return redirect(url_for('services'))

# ==================== АДМИН-ПАНЕЛЬ ====================
# --- Аутентификация ---
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Успешный вход в админ-панель', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Неверные данные для входа', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Вы вышли из админ-панели', 'info')
    return redirect(url_for('index'))

# --- Главная админ-панели ---
@app.route('/admin')
@admin_required
def admin_dashboard():
    settings = get_settings()
    services = get_services()
    reviews = get_reviews()
    return render_template('admin/dashboard.html', settings=settings, services_count=len(services), reviews_count=len(reviews))

# --- Управление услугами ---
@app.route('/admin/services')
@admin_required
def admin_services():
    services = get_services()
    return render_template('admin/services.html', services=services)

@app.route('/admin/services/add', methods=['GET', 'POST'])
@admin_required
def admin_add_service():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '').strip()
        image = request.form.get('image', '').strip()
        
        if not title or not description or not price:
            flash('Заполните все обязательные поля', 'error')
            return redirect(url_for('admin_add_service'))
        
        services = get_services()
        new_id = max([s['id'] for s in services], default=0) + 1
        
        new_service = {
            'id': new_id,
            'title': title,
            'description': description,
            'price': price,
            'image': image or 'https://images.unsplash.com/photo-1507136566006-cfc505b114fc?ixlib=rb-4.0.3&auto=format&fit=crop&w=1021&q=80'
        }
        
        services.append(new_service)
        if save_data(SERVICES_FILE, services):
            flash('Услуга успешно добавлена', 'success')
        else:
            flash('Ошибка при сохранении услуги', 'error')
        
        return redirect(url_for('admin_services'))
    
    return render_template('admin/add_service.html')

@app.route('/admin/services/edit/<int:service_id>', methods=['GET', 'POST'])  # ← ИСПРАВЛЕНО
@admin_required
def admin_edit_service(service_id):
    services = get_services()
    service = next((s for s in services if s['id'] == service_id), None)
    
    if not service:
        flash('Услуга не найдена', 'error')
        return redirect(url_for('admin_services'))
    
    if request.method == 'POST':
        service['title'] = request.form.get('title', '').strip()
        service['description'] = request.form.get('description', '').strip()
        service['price'] = request.form.get('price', '').strip()
        service['image'] = request.form.get('image', '').strip()
        
        if save_data(SERVICES_FILE, services):
            flash('Услуга успешно обновлена', 'success')
        else:
            flash('Ошибка при сохранении услуги', 'error')
        
        return redirect(url_for('admin_services'))
    
    return render_template('admin/edit_service.html', service=service)

@app.route('/admin/services/delete/<int:service_id>', methods=['POST'])  # ← ИСПРАВЛЕНО
@admin_required
def admin_delete_service(service_id):
    services = get_services()
    
    # Находим индекс услуги
    service_index = None
    for i, service in enumerate(services):
        if service['id'] == service_id:
            service_index = i
            break
    
    if service_index is not None:
        # Удаляем услугу
        deleted_service = services.pop(service_index)
        
        if save_data(SERVICES_FILE, services):
            flash(f'Услуга "{deleted_service["title"]}" успешно удалена', 'success')
        else:
            flash('Ошибка при удалении услуги', 'error')
    else:
        flash('Услуга не найдена', 'error')
    
    return redirect(url_for('admin_services'))

# --- Управление отзывами ---
@app.route('/admin/reviews')
@admin_required
def admin_reviews():
    reviews = get_reviews()
    return render_template('admin/reviews.html', reviews=reviews)

@app.route('/admin/reviews/add', methods=['GET', 'POST'])
@admin_required
def admin_add_review():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        text = request.form.get('text', '').strip()
        rating = int(request.form.get('rating', 5))
        
        if not name or not text:
            flash('Заполните все обязательные поля', 'error')
            return redirect(url_for('admin_add_review'))
        
        reviews = get_reviews()
        new_id = max([r['id'] for r in reviews], default=0) + 1
        
        new_review = {
            'id': new_id,
            'name': name,
            'text': text,
            'rating': rating,
            'date': 'Только что'
        }
        
        reviews.append(new_review)
        if save_data(REVIEWS_FILE, reviews):
            flash('Отзыв успешно добавлен', 'success')
        else:
            flash('Ошибка при сохранении отзыва', 'error')
        
        return redirect(url_for('admin_reviews'))
    
    return render_template('admin/add_review.html')

@app.route('/admin/reviews/edit/<int:review_id>', methods=['GET', 'POST'])  # ← ИСПРАВЛЕНО
@admin_required
def admin_edit_review(review_id):
    reviews = get_reviews()
    review = next((r for r in reviews if r['id'] == review_id), None)
    
    if not review:
        flash('Отзыв не найден', 'error')
        return redirect(url_for('admin_reviews'))
    
    if request.method == 'POST':
        review['name'] = request.form.get('name', '').strip()
        review['text'] = request.form.get('text', '').strip()
        review['rating'] = int(request.form.get('rating', 5))
        
        if save_data(REVIEWS_FILE, reviews):
            flash('Отзыв успешно обновлен', 'success')
        else:
            flash('Ошибка при сохранении отзыва', 'error')
        
        return redirect(url_for('admin_reviews'))
    
    return render_template('admin/edit_review.html', review=review)

@app.route('/admin/reviews/delete/<int:review_id>', methods=['POST'])  # ← ИСПРАВЛЕНО
@admin_required
def admin_delete_review(review_id):
    reviews = get_reviews()
    
    # Находим индекс отзыва
    review_index = None
    for i, review in enumerate(reviews):
        if review['id'] == review_id:
            review_index = i
            break
    
    if review_index is not None:
        # Удаляем отзыв
        deleted_review = reviews.pop(review_index)
        
        if save_data(REVIEWS_FILE, reviews):
            flash(f'Отзыв от "{deleted_review["name"]}" успешно удален', 'success')
        else:
            flash('Ошибка при удалении отзыва', 'error')
    else:
        flash('Отзыв не найден', 'error')
    
    return redirect(url_for('admin_reviews'))

# --- Настройки сайта ---
@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    settings = get_settings()
    
    if request.method == 'POST':
        # Контактная информация
        settings['contact_info']['phone'] = request.form.get('phone', '').strip()
        settings['contact_info']['address'] = request.form.get('address', '').strip()
        settings['contact_info']['email'] = request.form.get('email', '').strip()
        
        # Время работы
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            settings['work_hours'][day]['open'] = request.form.get(f'{day}_open', '').strip()
            settings['work_hours'][day]['close'] = request.form.get(f'{day}_close', '').strip()
            settings['work_hours'][day]['enabled'] = request.form.get(f'{day}_enabled') == 'on'
        
        # Социальные сети
        settings['social_links']['vk'] = request.form.get('vk', '').strip()
        settings['social_links']['instagram'] = request.form.get('instagram', '').strip()
        settings['social_links']['telegram'] = request.form.get('telegram', '').strip()
        
        if save_data(SETTINGS_FILE, settings):
            flash('Настройки успешно сохранены', 'success')
        else:
            flash('Ошибка при сохранении настроек', 'error')
        
        return redirect(url_for('admin_settings'))
    
    return render_template('admin/settings.html', settings=settings)

# --- API для загрузки данных ---
@app.route('/api/reviews')
@admin_required
def api_reviews():
    reviews = get_reviews()
    return jsonify(reviews)

@app.route('/api/services')
@admin_required
def api_services():
    services = get_services()
    return jsonify(services)

# --- Обработка ошибок ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)