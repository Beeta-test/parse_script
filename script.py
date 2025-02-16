import pandas as pd
from fuzzywuzzy import process
import re


def normalize_name(name):
    """Функция для нормализации названия"""
    if not isinstance(name, str):
        return ""
    name = name.lower()
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def extract_price(text):
    """Функция извлекает цену из строки, исключая неподходящие значения"""
    if not isinstance(text, str):
        return None

    prices = re.findall(r"\b\d{4,6}\b", text)
    prices = [int(p) for p in prices if int(p) >= 2500]

    return min(prices) if prices else None


def match_products(shop_file, suppliers_file, output_file):
    """Функция соппоставления товаров"""
    shop_df = pd.read_csv(shop_file)
    suppliers_df = pd.read_csv(suppliers_file)

    shop_df["normalized_name"] = shop_df[
        "Наименование"].apply(normalize_name)
    suppliers_df["normalized_name"] = suppliers_df[
        "прайс"].apply(normalize_name)

    matched_data = []

    for _, shop_product in shop_df.iterrows():
        best_matches = process.extract(shop_product["normalized_name"],
                                       suppliers_df["normalized_name"],)

        matched_item = {
            "Внешний код": shop_product["Внешний код"],
            "Наше название": shop_product["Наименование"]
        }

        match_index = 1
        for matched_name, score, idx in best_matches:
            original_text = suppliers_df.loc[idx, "прайс"]
            price = extract_price(original_text)

            if price is not None:
                supplier = suppliers_df.loc[idx, "поставщик"]
                matched_item[f"прайс {match_index}"] = price
                matched_item[f"поставщик {match_index}"] = supplier
                match_index += 1
        matched_data.append(matched_item)

    final_df = pd.DataFrame(matched_data)
    final_df.to_csv(output_file, index=False, encoding="utf-8-sig")


match_products(
    "Товары магазина.csv",
    "Прайсы с телеграма.csv",
    "matched_products.csv"
)
