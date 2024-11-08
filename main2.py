import streamlit as st
import os
import json
from PIL import Image, ExifTags
from streamlit_cookies_manager import CookieManager

# Инициализация cookies
cookies = CookieManager()

# Путь для хранения изображений, лайков и подписей
IMAGE_DIR = "uploaded_images"
LIKES_FILE = "likes.json"
CAPTIONS_FILE = "captions.json"

# Создаем директории и файлы для хранения данных
os.makedirs(IMAGE_DIR, exist_ok=True)
if not os.path.exists(LIKES_FILE):
    with open(LIKES_FILE, "w") as f:
        json.dump({}, f)
if not os.path.exists(CAPTIONS_FILE):
    with open(CAPTIONS_FILE, "w") as f:
        json.dump({}, f)

# Стили CSS для адаптивного макета
st.markdown("""
    <style>
        .gallery {
            display: grid;
            gap: 20px;
        }
        /* Три изображения в ряд для больших экранов */
        @media (min-width: 1024px) {
            .gallery {
                grid-template-columns: repeat(3, 1fr);
            }
        }
        /* Два изображения в ряд для средних экранов */
        @media (min-width: 600px) and (max-width: 1023px) {
            .gallery {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        /* Одно изображение в ряд для маленьких экранов */
        @media (max-width: 599px) {
            .gallery {
                grid-template-columns: 1fr;
            }
        }
    </style>
""", unsafe_allow_html=True)

# def correct_image_orientation(image_path):
#     """Корректирует ориентацию изображения и удаляет EXIF-данные."""
#     image = Image.open(image_path)
#     try:
#         # Определение ориентации изображения по EXIF
#         for orientation in ExifTags.TAGS.keys():
#             if ExifTags.TAGS[orientation] == 'Orientation':
#                 break
#         exif = image._getexif()
#
#         if exif is not None:
#             orientation = exif.get(orientation)
#             # Поворот изображения в зависимости от ориентации
#             if orientation == 3:
#                 image = image.rotate(180, expand=True)
#             elif orientation == 6:
#                 image = image.rotate(270, expand=True)
#             elif orientation == 8:
#                 image = image.rotate(90, expand=True)
#
#         # Сохранение изображения без EXIF-данных
#         image = image.convert("RGB")  # Убирает EXIF, сохраняя в формате RGB
#         image.save(image_path)
#         print(f"Ориентация изображения {image_path} исправлена.")
#     except Exception as e:
#         print(f"Ошибка при обработке {image_path}: {e}")

# Обрабатываем все изображения в папке
# for img_file in os.listdir(IMAGE_DIR):
#     img_path = os.path.join(IMAGE_DIR, img_file)
#     if img_file.lower().endswith(('jpg', 'jpeg', 'png', 'JPG')):
#         correct_image_orientation(img_path)
#

def get_saved_images():
    # Получаем список всех изображений в папке
    if not os.path.exists(IMAGE_DIR):
        return []
    return [f for f in os.listdir(IMAGE_DIR) if f.endswith(('jpg', 'jpeg', 'png', 'JPG'))]

# Функции для загрузки и сохранения данных
def load_likes():
    with open(LIKES_FILE, "r") as f:
        return json.load(f)

def save_likes(likes_data):
    with open(LIKES_FILE, "w") as f:
        json.dump(likes_data, f)

def load_captions():
    with open(CAPTIONS_FILE, "r") as f:
        return json.load(f)

def save_captions(captions_data):
    with open(CAPTIONS_FILE, "w") as f:
        json.dump(captions_data, f)

# Показ загруженных изображений и система лайков
st.header("Галерея изображений")
likes_data = load_likes()
captions_data = load_captions()

# Получаем все файлы изображений
#images = os.listdir(IMAGE_DIR)
images = sorted(get_saved_images())
# Адаптивная галерея изображений
st.markdown('<div class="gallery">', unsafe_allow_html=True)
for file_name in images:
    file_path = os.path.join(IMAGE_DIR, file_name)
    st.markdown(f'<div style="text-align: center;">', unsafe_allow_html=True)

    # Показ изображения
    st.image(file_path, use_column_width="always", caption=file_name)

    # Поле ввода для редактирования подписи
    new_caption = st.text_area(
        captions_data.get(file_name, f"Подпись для {file_name}"),
        value=captions_data.get(file_name, ""),
        key=f"caption_{file_name}"
    )
    # Сохраняем подпись при изменении
    if new_caption != captions_data.get(file_name, ""):
        captions_data[file_name] = new_caption
        save_captions(captions_data)

    # if st.button("Обновить подпись", key="update_caption_button"+str(hash(file_path))):
    #     st.image(file_path, caption=new_caption, use_column_width=True)

    # Кнопка лайка
    like_cookie_key = f"liked_{file_name}"
    if not cookies.get(like_cookie_key):
        if st.button("❤️ Лайк", key=f"like_{file_name}"):
            likes_data[file_name] = likes_data.get(file_name, 0) + 1
            save_likes(likes_data)
            cookies[like_cookie_key] = "true"
            cookies.save()
    else:
        st.write("Вы уже лайкнули это изображение")

    # Счётчик лайков
    st.write(f"Лайки: {likes_data.get(file_name, 0)}")

    # Кнопка для скачивания изображения
    with open(file_path, "rb") as img_file:
        img_bytes = img_file.read()
        st.download_button(
            label="Скачать",
            data=img_bytes,
            file_name=file_name,
            mime="image/jpeg"
        )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # Закрываем контейнер галереи