#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产品描述翻译脚本
将所有产品描述翻译为7种语言
"""

import json
import os

# 产品描述的通用翻译映射（基于常见术语）
COMMON_TRANSLATIONS = {
    # 通用词汇
    "模板系统": {"en": "formwork system", "es": "sistema de encofrado", "de": "Schalungssystem", "pt": "sistema de cofragem", "sr": "sistem oplate", "hu": "zsaluzási rendszer"},
    "适用于": {"en": "suitable for", "es": "adecuado para", "de": "geeignet für", "pt": "adequado para", "sr": "pogodan za", "hu": "alkalmas"},
    "高效": {"en": "efficient", "es": "eficiente", "de": "effizient", "pt": "eficiente", "sr": "efikasan", "hu": "hatékony"},
    "灵活": {"en": "flexible", "es": "flexible", "de": "flexibel", "pt": "flexível", "sr": "fleksibilan", "hu": "rugalmas"},
    "轻质": {"en": "lightweight", "es": "ligero", "de": "leicht", "pt": "leve", "sr": "lagan", "hu": "könnyű"},
    "经济": {"en": "economical", "es": "económico", "de": "wirtschaftlich", "pt": "econômico", "sr": "ekonomičan", "hu": "gazdaságos"},
    "坚固": {"en": "robust", "es": "robusto", "de": "robust", "pt": "robusto", "sr": "robustan", "hu": "robusztus"},
    "快速": {"en": "fast", "es": "rápido", "de": "schnell", "pt": "rápido", "sr": "brz", "hu": "gyors"},
    "简单": {"en": "simple", "es": "simple", "de": "einfach", "pt": "simples", "sr": "jednostavan", "hu": "egyszerű"},
    "模块化": {"en": "modular", "es": "modular", "de": "modular", "pt": "modular", "sr": "modularan", "hu": "moduláris"},
}

# 手动翻译的产品描述（基于PERI官网的标准描述）
PRODUCT_TRANSLATIONS = {
    "便于徒手操作、灵活、轻质的模板系统": {
        "en": "Easy-to-handle, flexible, lightweight formwork system",
        "es": "Sistema de encofrado flexible y ligero, fácil de manejar",
        "de": "Handliches, flexibles, leichtes Schalungssystem",
        "pt": "Sistema de cofragem flexível e leve, fácil de manusear",
        "sr": "Fleksibilan, lagan sistem oplate, lak za rukovanje",
        "hu": "Könnyen kezelhető, rugalmas, könnyű zsaluzási rendszer"
    },
    "久经考验的GT 24木梁模板系统，适用于任何类型的工程。": {
        "en": "Proven GT 24 girder formwork system, suitable for any type of project.",
        "es": "Sistema de encofrado de vigas GT 24 probado, adecuado para cualquier tipo de proyecto.",
        "de": "Bewährtes GT 24 Trägerschalungssystem, geeignet für jede Art von Projekt.",
        "pt": "Sistema de cofragem de vigas GT 24 comprovado, adequado para qualquer tipo de projeto.",
        "sr": "Provereni GT 24 sistem gredne oplate, pogodan za bilo koji tip projekta.",
        "hu": "Bevált GT 24 gerendazsaluzási rendszer, bármilyen típusú projekthez alkalmas."
    },
    "适用于相同构造的住宅建筑，立模简单、高效、快速。": {
        "en": "Suitable for residential buildings with identical structures, simple, efficient, and fast assembly.",
        "es": "Adecuado para edificios residenciales con estructuras idénticas, montaje simple, eficiente y rápido.",
        "de": "Geeignet für Wohngebäude mit identischen Strukturen, einfache, effiziente und schnelle Montage.",
        "pt": "Adequado para edifícios residenciais com estruturas idênticas, montagem simples, eficiente e rápida.",
        "sr": "Pogodan za stambene zgrade sa identičnim strukturama, jednostavna, efikasna i brza montaža.",
        "hu": "Azonos szerkezetű lakóépületekhez alkalmas, egyszerű, hatékony és gyors szerelés."
    },
    "TRIO框式模板系统，用于各种墙体浇筑。": {
        "en": "TRIO framed formwork system for all types of wall concreting.",
        "es": "Sistema de encofrado enmarcado TRIO para todo tipo de hormigonado de muros.",
        "de": "TRIO Rahmenschalungssystem für alle Arten von Wandbetonierungen.",
        "pt": "Sistema de cofragem emoldurada TRIO para todos os tipos de concretagem de paredes.",
        "sr": "TRIO sistem ramovske oplate za sve vrste betoniranja zidova.",
        "hu": "TRIO keretes zsaluzási rendszer minden típusú falbetonozáshoz."
    },
    "高效、坚固的大型框式模板系统，适用于大面积墙体浇筑，拥有出色的混凝土成型质量。": {
        "en": "Efficient, robust large-panel formwork system for large-area wall concreting with excellent concrete finish quality.",
        "es": "Sistema de encofrado de paneles grandes eficiente y robusto para hormigonado de muros de gran área con excelente calidad de acabado de hormigón.",
        "de": "Effizientes, robustes Großtafelschalungssystem für großflächige Wandbetonierungen mit hervorragender Betonqualität.",
        "pt": "Sistema de cofragem de painéis grandes eficiente e robusto para concretagem de paredes de grande área com excelente qualidade de acabamento de concreto.",
        "sr": "Efikasan, robustan sistem velikih panela oplate za betoniranje zidova velikih površina sa odličnim kvalitetom završne obrade betona.",
        "hu": "Hatékony, robusztus nagyméretű panelzsaluzási rendszer nagyfelületű falbetonozáshoz kiváló betonfelület-minőséggel."
    },
    "模块化框式模板，灵活适用于各种工程。": {
        "en": "Modular framed formwork, flexibly applicable to various projects.",
        "es": "Encofrado enmarcado modular, aplicable de forma flexible a varios proyectos.",
        "de": "Modulare Rahmenschalung, flexibel einsetzbar für verschiedene Projekte.",
        "pt": "Cofragem emoldurada modular, aplicável de forma flexível a vários projetos.",
        "sr": "Modularna ramovska oplata, fleksibilno primenljiva na različite projekte.",
        "hu": "Moduláris keretes zsaluzat, rugalmasan alkalmazható különböző projektekhez."
    },
    "轻型钢框模板，高效经济。": {
        "en": "Lightweight steel-framed formwork, efficient and economical.",
        "es": "Encofrado de marco de acero ligero, eficiente y económico.",
        "de": "Leichte Stahlrahmenschalung, effizient und wirtschaftlich.",
        "pt": "Cofragem de estrutura de aço leve, eficiente e econômica.",
        "sr": "Lagana čelična ramovska oplata, efikasna i ekonomična.",
        "hu": "Könnyű acélkeretes zsaluzat, hatékony és gazdaságos."
    },
    "为高达8.75米的单侧模板提供可靠的受力支撑。": {
        "en": "Provides reliable load-bearing support for single-sided formwork up to 8.75 meters high.",
        "es": "Proporciona soporte de carga confiable para encofrado de un solo lado de hasta 8.75 metros de altura.",
        "de": "Bietet zuverlässige Lastunterstützung für einseitige Schalung bis zu 8,75 Meter Höhe.",
        "pt": "Fornece suporte de carga confiável para cofragem unilateral de até 8,75 metros de altura.",
        "sr": "Pruža pouzdanu nosivost za jednostranu oplatu do 8,75 metara visine.",
        "hu": "Megbízható teherhordó támogatást nyújt egyoldalas zsaluzathoz 8,75 méter magasságig."
    },
    "用于浇筑圆形或弧形结构的曲面模板系统。": {
        "en": "Curved formwork system for concreting circular or curved structures.",
        "es": "Sistema de encofrado curvo para hormigonado de estructuras circulares o curvas.",
        "de": "Rundschalungssystem für Betonierung von runden oder gebogenen Strukturen.",
        "pt": "Sistema de cofragem curva para concretagem de estruturas circulares ou curvas.",
        "sr": "Sistem zakrivljene oplate za betoniranje kružnih ili zakrivljenih struktura.",
        "hu": "Ívelt zsaluzási rendszer kör alakú vagy ívelt szerkezetek betonozásához."
    },
    "适用于各种半径的圆形墙体浇筑。": {
        "en": "Suitable for circular wall concreting with various radii.",
        "es": "Adecuado para hormigonado de muros circulares con varios radios.",
        "de": "Geeignet für Rundwandbetonierung mit verschiedenen Radien.",
        "pt": "Adequado para concretagem de paredes circulares com vários raios.",
        "sr": "Pogodan za betoniranje kružnih zidova sa različitim radijusima.",
        "hu": "Alkalmas különböző sugarú kör alakú falak betonozásához."
    },
    "无需穿墙拉杆，对桶形结构建筑进行浇筑。": {
        "en": "Concreting of cylindrical structures without through-wall ties.",
        "es": "Hormigonado de estructuras cilíndricas sin tirantes de pared.",
        "de": "Betonierung von zylindrischen Strukturen ohne Durchgangsanker.",
        "pt": "Concretagem de estruturas cilíndricas sem tirantes de parede.",
        "sr": "Betoniranje cilindričnih struktura bez prolaznih ankera.",
        "hu": "Hengeres szerkezetek betonozása átmenő falkötők nélkül."
    }
}

def translate_description(desc_zh):
    """翻译产品描述到6种语言"""
    if desc_zh in PRODUCT_TRANSLATIONS:
        return PRODUCT_TRANSLATIONS[desc_zh]

    # 如果没有预定义翻译，返回占位符（需要手动翻译）
    return {
        "en": desc_zh,  # 暂时保留中文，需要手动翻译
        "es": desc_zh,
        "de": desc_zh,
        "pt": desc_zh,
        "sr": desc_zh,
        "hu": desc_zh
    }

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    products_file = os.path.join(base_dir, 'products_v2.json')

    with open(products_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 统计需要翻译的产品
    total_products = 0
    translated_products = 0
    untranslated_descs = set()

    for cat_key, cat in data.items():
        if 'subcategories' in cat:
            for sc_key, sc in cat['subcategories'].items():
                for p in sc['products']:
                    total_products += 1
                    desc_zh = p[2]
                    if desc_zh in PRODUCT_TRANSLATIONS:
                        translated_products += 1
                    else:
                        untranslated_descs.add(desc_zh)
        else:
            for p in cat.get('products', []):
                total_products += 1
                desc_zh = p[2]
                if desc_zh in PRODUCT_TRANSLATIONS:
                    translated_products += 1
                else:
                    untranslated_descs.add(desc_zh)

    print(f"总产品数: {total_products}")
    print(f"已翻译: {translated_products}")
    print(f"待翻译: {len(untranslated_descs)}")
    print(f"\n待翻译的描述:")
    for desc in sorted(untranslated_descs):
        print(f"  - {desc}")

if __name__ == '__main__':
    main()
