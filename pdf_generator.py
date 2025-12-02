#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор PDF из данных CSV/JSON с использованием HTML-шаблонов.
Поддерживает сущности: Product, Invoice, Order.
"""

import os
import json
import csv
import sys
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
from jinja2 import Template
from weasyprint import HTML
import platform


class ExitCommand(Exception):
    """Исключение для выхода из программы по команде пользователя."""
    pass


# Константы путей
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"


def create_directories():
    """Создание необходимых директорий, если их нет."""
    for directory in [DATA_DIR, TEMPLATES_DIR, OUTPUT_DIR]:
        directory.mkdir(exist_ok=True)
        print(f"✓ Директория {directory} готова")


def generate_test_data():
    """Генерация тестовых данных для Product, Invoice, Order."""
    
    # Данные для Product
    products = [
        {"id": 1, "name": "Ноутбук", "price": 45000, "description": "Игровой ноутбук с видеокартой RTX 3060", "category": "Электроника"},
        {"id": 2, "name": "Смартфон", "price": 25000, "description": "Смартфон с камерой 64 МП", "category": "Электроника"},
        {"id": 3, "name": "Наушники", "price": 3500, "description": "Беспроводные наушники с шумоподавлением", "category": "Аудио"},
        {"id": 4, "name": "Клавиатура", "price": 2500, "description": "Механическая клавиатура RGB", "category": "Периферия"},
        {"id": 5, "name": "Мышь", "price": 1500, "description": "Игровая мышь с оптическим сенсором", "category": "Периферия"},
    ]
    
    # Данные для Invoice
    invoices = [
        {"id": 1, "customer_name": "Иван Петров", "date": "2024-01-15", "total": 47500, "status": "Оплачен"},
        {"id": 2, "customer_name": "Мария Сидорова", "date": "2024-01-16", "total": 25000, "status": "Оплачен"},
        {"id": 3, "customer_name": "Алексей Иванов", "date": "2024-01-17", "total": 70500, "status": "В обработке"},
        {"id": 4, "customer_name": "Елена Козлова", "date": "2024-01-18", "total": 6000, "status": "Оплачен"},
        {"id": 5, "customer_name": "Дмитрий Смирнов", "date": "2024-01-19", "total": 4000, "status": "Отменён"},
    ]
    
    # Данные для Order (несколько строк могут принадлежать одному invoice_number)
    orders = [
        {"id": 1, "product_name": "Ноутбук", "invoice_number": 1, "quantity": 1, "price": 45000},
        {"id": 2, "product_name": "Клавиатура", "invoice_number": 1, "quantity": 1, "price": 2500},
        {"id": 3, "product_name": "Смартфон", "invoice_number": 2, "quantity": 1, "price": 25000},
        {"id": 4, "product_name": "Ноутбук", "invoice_number": 3, "quantity": 1, "price": 45000},
        {"id": 5, "product_name": "Наушники", "invoice_number": 3, "quantity": 2, "price": 7000},
        {"id": 6, "product_name": "Мышь", "invoice_number": 3, "quantity": 1, "price": 1500},
        {"id": 7, "product_name": "Наушники", "invoice_number": 4, "quantity": 1, "price": 3500},
        {"id": 8, "product_name": "Клавиатура", "invoice_number": 4, "quantity": 1, "price": 2500},
        {"id": 9, "product_name": "Мышь", "invoice_number": 5, "quantity": 2, "price": 3000},
        {"id": 10, "product_name": "Клавиатура", "invoice_number": 5, "quantity": 1, "price": 2500},
    ]
    
    # Сохранение данных
    entities = {
        "product": products,
        "invoice": invoices,
        "order": orders
    }
    
    for entity_name, data in entities.items():
        # Сохранение в JSON
        json_path = DATA_DIR / f"{entity_name}_1.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ Создан {json_path}")
        
        # Сохранение в CSV
        csv_path = DATA_DIR / f"{entity_name}_1.csv"
        if data:
            df = pd.DataFrame(data)
            df.to_csv(csv_path, index=False, encoding="utf-8")
            print(f"✓ Создан {csv_path}")


def create_html_templates():
    """Создание HTML-шаблонов для каждой сущности."""
    
    # Шаблон для Invoice
    invoice_template = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <style>
        body { 
            font-family: 'DejaVu Sans', 'Roboto', Arial, sans-serif; 
            margin: 40px;
            line-height: 1.6;
        }
        h2 { color: #333; }
        h4 { color: #555; }
        hr { border: 1px solid #ddd; margin: 20px 0; }
        b { color: #2c3e50; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #808080;
            color: white;
            font-weight: bold;
            font-size: 16px;
            text-align: center;
            vertical-align: middle;
        }
        tr:nth-child(even) {
            background-color: #e0e0e0;
        }
        tr:nth-child(odd) {
            background-color: #f5f5f5;
        }
        .total-row {
            font-weight: bold;
            background-color: #b0b0b0;
        }
    </style>
</head>
<body>
    <h2>Чек #{{ invoice.id }} от {{ invoice.date }}</h2>
    <p>Клиент: {{ invoice.customer_name }}</p>
    <p>Сумма: <b>{{ invoice.total }} руб.</b></p>
    <p>Статус: {{ invoice.status }}</p>
    <hr>
    <h4>Состав заказа</h4>
    <table>
        <thead>
            <tr>
                <th>Товар</th>
                <th>Количество, шт</th>
                <th>Цена, руб</th>
                <th>Сумма, руб</th>
            </tr>
        </thead>
        <tbody>
            {% for o in orders %}
            <tr>
                <td>{{ o.product_name }}</td>
                <td>{{ o.quantity }}</td>
                <td>{{ o.price }}</td>
                <td>{{ (o.quantity|int * o.price|int) }}</td>
            </tr>
            {% endfor %}
            <tr class="total-row">
                <td colspan="3" style="text-align: right;">Итого:</td>
                <td>{{ invoice.total }}</td>
            </tr>
        </tbody>
    </table>
    <hr>
    <p>Спасибо за покупку!</p>
</body>
</html>"""
    
    # Шаблон для Product (поддерживает несколько продуктов)
    product_template = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <style>
        body { 
            font-family: 'DejaVu Sans', 'Roboto', Arial, sans-serif; 
            margin: 40px;
            line-height: 1.6;
        }
        h2 { color: #333; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #808080;
            color: white;
            font-weight: bold;
            font-size: 16px;
            text-align: center;
            vertical-align: middle;
        }
        tr:nth-child(even) {
            background-color: #e0e0e0;
        }
        tr:nth-child(odd) {
            background-color: #f5f5f5;
        }
    </style>
</head>
<body>
    <h2>Информация о товарах</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Название</th>
                <th>Цена, руб</th>
                <th>Описание</th>
                <th>Категория</th>
            </tr>
        </thead>
        <tbody>
            {% for product in products %}
            <tr>
                <td>{{ product.id }}</td>
                <td>{{ product.name }}</td>
                <td>{{ product.price }}</td>
                <td>{{ product.description }}</td>
                <td>{{ product.category }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>"""
    
    # Шаблон для Order (может содержать несколько строк для одного invoice_number)
    order_template = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <style>
        body { 
            font-family: 'DejaVu Sans', 'Roboto', Arial, sans-serif; 
            margin: 40px;
            line-height: 1.6;
        }
        h2 { color: #333; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #808080;
            color: white;
            font-weight: bold;
            font-size: 16px;
            text-align: center;
            vertical-align: middle;
        }
        tr:nth-child(even) {
            background-color: #e0e0e0;
        }
        tr:nth-child(odd) {
            background-color: #f5f5f5;
        }
        .total-row {
            font-weight: bold;
            background-color: #b0b0b0;
        }
    </style>
</head>
<body>
    <h2>Заказы по счету #{{ invoice_number }}</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Название товара</th>
                <th>Количество, шт</th>
                <th>Цена, руб</th>
                <th>Сумма, руб</th>
            </tr>
        </thead>
        <tbody>
            {% for o in orders %}
            <tr>
                <td>{{ o.id }}</td>
                <td>{{ o.product_name }}</td>
                <td>{{ o.quantity }}</td>
                <td>{{ o.price }}</td>
                <td>{{ (o.quantity|int * o.price|int) }}</td>
            </tr>
            {% endfor %}
            <tr class="total-row">
                <td colspan="4" style="text-align: right;">Итого:</td>
                <td>{{ total }}</td>
            </tr>
        </tbody>
    </table>
</body>
</html>"""
    
    templates = {
        "invoice_template.html": invoice_template,
        "product_template.html": product_template,
        "order_template.html": order_template
    }
    
    for filename, content in templates.items():
        template_path = TEMPLATES_DIR / filename
        with open(template_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ Создан шаблон {template_path}")


def list_files(directory: Path, pattern: str = "*") -> List[Path]:
    """Получение списка файлов в директории."""
    return sorted(directory.glob(pattern))


def load_data(file_path: Path) -> List[Dict[str, Any]]:
    """Загрузка данных из CSV или JSON файла."""
    if file_path.suffix.lower() == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    elif file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path, encoding="utf-8")
        # Конвертация числовых полей для order
        if "quantity" in df.columns:
            df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
        if "price" in df.columns:
            df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0).astype(int)
        if "invoice_number" in df.columns:
            df["invoice_number"] = pd.to_numeric(df["invoice_number"], errors="coerce").fillna(0).astype(int)
        return df.to_dict("records")
    else:
        raise ValueError(f"Неподдерживаемый формат файла: {file_path.suffix}")


def display_menu(items: List[Any], title: str, item_name: str = "элемент") -> int:
    """Отображение меню и получение выбора пользователя."""
    print(f"\n{title}")
    print("=" * 50)
    for i, item in enumerate(items, 1):
        if isinstance(item, Path):
            print(f"{i}. {item.name}")
        else:
            print(f"{i}. {item}")
    print("=" * 50)
    print("Для выхода введите: exit, quit или q")
    
    while True:
        try:
            choice = input(f"Выберите {item_name} (1-{len(items)}) или 'exit' для выхода: ").strip().lower()
            
            # Проверка команд выхода
            if choice in ['exit', 'quit', 'q', 'выход', 'в']:
                raise ExitCommand()
            
            index = int(choice) - 1
            if 0 <= index < len(items):
                return index
            else:
                print(f"Пожалуйста, введите число от 1 до {len(items)} или 'exit' для выхода")
        except ValueError:
            print("Пожалуйста, введите корректное число или 'exit' для выхода")
        except KeyboardInterrupt:
            print("\n\nОперация отменена пользователем.")
            sys.exit(0)


def display_multi_select_menu(items: List[Any], title: str, item_name: str = "элемент") -> List[int]:
    """Отображение меню с возможностью множественного выбора."""
    print(f"\n{title}")
    print("=" * 50)
    for i, item in enumerate(items, 1):
        if isinstance(item, Path):
            print(f"{i}. {item.name}")
        else:
            print(f"{i}. {item}")
    print("=" * 50)
    print("Введите номера через запятую (например: 1,3,5), 'all' для выбора всех")
    print("Для выхода введите: exit, quit или q")
    
    while True:
        try:
            choice = input(f"Выберите {item_name} или 'exit' для выхода: ").strip().lower()
            
            # Проверка команд выхода
            if choice in ['exit', 'quit', 'q', 'выход', 'в']:
                raise ExitCommand()
            
            if choice == "all":
                return list(range(len(items)))
            
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            if all(0 <= idx < len(items) for idx in indices):
                return indices
            else:
                print(f"Пожалуйста, введите числа от 1 до {len(items)} или 'exit' для выхода")
        except ValueError:
            print("Пожалуйста, введите корректные числа через запятую или 'exit' для выхода")
        except KeyboardInterrupt:
            print("\n\nОперация отменена пользователем.")
            sys.exit(0)


def ask_continue() -> bool:
    """Спросить пользователя, хочет ли он продолжить работу."""
    while True:
        try:
            choice = input("\nПродолжить работу? (да/нет) или 'exit' для выхода: ").strip().lower()
            
            # Проверка команд выхода
            if choice in ['exit', 'quit', 'q', 'выход', 'в']:
                raise ExitCommand()
            
            if choice in ["да", "д", "yes", "y"]:
                return True
            elif choice in ["нет", "н", "no", "n"]:
                return False
            else:
                print("Пожалуйста, введите 'да', 'нет' или 'exit' для выхода")
        except KeyboardInterrupt:
            return False


def open_pdf(file_path: Path):
    """Открытие PDF файла в системной программе просмотра."""
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(str(file_path))
        elif system == "Darwin":  # macOS
            os.system(f"open '{file_path}'")
        else:  # Linux
            os.system(f"xdg-open '{file_path}'")
        print(f"✓ PDF открыт в системной программе просмотра")
    except Exception as e:
        print(f"⚠ Не удалось автоматически открыть PDF: {e}")
        print(f"  Файл сохранён: {file_path}")


def generate_pdf(template_path: Path, data: Dict[str, Any], output_path: Path):
    """Генерация PDF из HTML-шаблона и данных."""
    # Загрузка шаблона
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()
    
    # Рендеринг шаблона
    template = Template(template_content)
    html_content = template.render(**data)
    
    # Генерация PDF
    HTML(string=html_content).write_pdf(output_path)
    print(f"✓ PDF создан: {output_path}")


def process_document():
    """Обработка одного документа - выбор файла, шаблона и генерация PDF."""
    # Обновление списков файлов
    data_files = list_files(DATA_DIR)
    template_files = list_files(TEMPLATES_DIR, "*.html")
    
    if not data_files:
        print("❌ Ошибка: не найдены файлы данных в директории /data")
        return False
    
    if not template_files:
        print("❌ Ошибка: не найдены шаблоны в директории /templates")
        return False
    
    try:
        # Выбор файла данных
        data_file_index = display_menu(data_files, "\n📁 Доступные файлы данных:", "файл данных")
        selected_data_file = data_files[data_file_index]
        
        # Выбор шаблона
        template_index = display_menu(template_files, "\n📄 Доступные шаблоны:", "шаблон")
        selected_template = template_files[template_index]
    except ExitCommand:
        raise  # Пробрасываем исключение выше для обработки в main
    
    # Загрузка данных
    print(f"\nЗагрузка данных из {selected_data_file.name}...")
    try:
        all_data = load_data(selected_data_file)
        print(f"✓ Загружено {len(all_data)} записей")
    except Exception as e:
        print(f"❌ Ошибка при загрузке данных: {e}")
        return False
    
    # Определение типа сущности по имени файла
    entity_type = selected_data_file.stem.split("_")[0].lower()
    
    # Обработка в зависимости от типа сущности
    try:
        if entity_type == "invoice":
            print("\n📋 Доступные чеки:")
            invoice_ids = [item["id"] for item in all_data]
            invoice_index = display_menu(invoice_ids, "", "ID чека")
            selected_invoice = all_data[invoice_index]
            
            # Загрузка связанных данных (orders) по invoice_number
            order_files = list_files(DATA_DIR, "order_*.csv") + list_files(DATA_DIR, "order_*.json")
            orders = []
            if order_files:
                try:
                    all_orders = load_data(order_files[0])
                    # Используем invoice_number вместо invoice_id
                    orders = [o for o in all_orders if o.get("invoice_number") == selected_invoice["id"]]
                except Exception as e:
                    print(f"⚠ Не удалось загрузить заказы: {e}")
            
            # Генерация PDF
            output_filename = f"invoice_{selected_invoice['id']}.pdf"
            output_path = OUTPUT_DIR / output_filename
            
            generate_pdf(
                selected_template,
                {"invoice": selected_invoice, "orders": orders},
                output_path
            )
            
            # Открытие PDF
            open_pdf(output_path)
        
        elif entity_type == "product":
            # Множественный выбор продуктов
            print("\n📦 Доступные товары:")
            product_list = [f"{item['id']} - {item['name']}" for item in all_data]
            selected_indices = display_multi_select_menu(product_list, "", "товары")
            selected_products = [all_data[idx] for idx in selected_indices]
            
            # Генерация PDF
            if len(selected_products) == 1:
                output_filename = f"product_{selected_products[0]['id']}.pdf"
            else:
                output_filename = f"products_{len(selected_products)}.pdf"
            output_path = OUTPUT_DIR / output_filename
            
            generate_pdf(
                selected_template,
                {"products": selected_products},
                output_path
            )
            
            # Открытие PDF
            open_pdf(output_path)
        
        elif entity_type == "order":
            # Группировка заказов по invoice_number
            order_files = list_files(DATA_DIR, "order_*.csv") + list_files(DATA_DIR, "order_*.json")
            if not order_files:
                print("❌ Ошибка: не найдены файлы заказов")
                return False
            
            all_orders = load_data(order_files[0])
            
            # Группировка по invoice_number
            invoice_numbers = sorted(set([o.get("invoice_number") for o in all_orders if o.get("invoice_number")]))
            
            print("\n🛒 Доступные счета (по номеру счета):")
            invoice_display = [f"Счет #{inv_num} ({len([o for o in all_orders if o.get('invoice_number') == inv_num])} позиций)" 
                              for inv_num in invoice_numbers]
            invoice_index = display_menu(invoice_display, "", "номер счета")
            selected_invoice_number = invoice_numbers[invoice_index]
            
            # Получение всех заказов для выбранного invoice_number
            orders_for_invoice = [o for o in all_orders if o.get("invoice_number") == selected_invoice_number]
            
            # Вычисление итоговой суммы
            total_sum = sum(int(o.get("quantity", 0)) * int(o.get("price", 0)) for o in orders_for_invoice)
            
            # Генерация PDF
            output_filename = f"order_invoice_{selected_invoice_number}.pdf"
            output_path = OUTPUT_DIR / output_filename
            
            generate_pdf(
                selected_template,
                {"invoice_number": selected_invoice_number, "orders": orders_for_invoice, "total": total_sum},
                output_path
            )
            
            # Открытие PDF
            open_pdf(output_path)
        
        else:
            print(f"❌ Неизвестный тип сущности: {entity_type}")
            return False
    except ExitCommand:
        raise  # Пробрасываем исключение выше для обработки в main
    
    return True


def main():
    """Основная функция программы."""
    print("=" * 60)
    print("ГЕНЕРАТОР PDF ИЗ ДАННЫХ")
    print("=" * 60)
    print("\n💡 Подсказка: В любой момент можно выйти из программы,")
    print("   введя команду: exit, quit или q")
    print("=" * 60)
    
    # Создание директорий
    create_directories()
    
    # Генерация данных и шаблонов (если их нет)
    data_files = list_files(DATA_DIR)
    template_files = list_files(TEMPLATES_DIR, "*.html")
    
    if not data_files:
        print("\nГенерация тестовых данных...")
        generate_test_data()
    
    # Всегда пересоздаем шаблоны, чтобы гарантировать актуальность
    print("\nСоздание/обновление HTML-шаблонов...")
    create_html_templates()
    
    # Основной цикл работы
    while True:
        try:
            success = process_document()
            if success:
                print("\n" + "=" * 60)
                print("Документ создан! ✓")
                print("=" * 60)
            
            if not ask_continue():
                break
        except ExitCommand:
            print("\n\nВыход из программы по команде пользователя.")
            break
        except KeyboardInterrupt:
            print("\n\nОперация отменена пользователем.")
            break
        except Exception as e:
            print(f"\n❌ Произошла ошибка: {e}")
            try:
                if not ask_continue():
                    break
            except ExitCommand:
                print("\n\nВыход из программы по команде пользователя.")
                break
    
    print("\n" + "=" * 60)
    print("Работа завершена. До свидания!")
    print("=" * 60)


if __name__ == "__main__":
    main()

