#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PERI GCB Website Rebuild Script v2
- 6 categories matching cn.peri.com (建筑模板系统 split into 4 subcategories)
- Correct product photos
- Fixed navigation paths
Run: python3 rebuild_site_v2.py
"""

import os, json, re, urllib.parse

# YouTube video IDs for key products (from @perigroup channel)
YT_IDS = {
    'handset-alpha':                      'c3FOoHAjQEs',
    'trio-rahmenschalung':                'ypBa9srkqy8',
    'trio-schalungssystem':               'ypBa9srkqy8',
    'skydeck-slab-formwork':              'CgOEI3YtG_E',
    'multiflex-girder-slab-formwork':     'kHOmVl6O5us',
    'gridflex-deckenschalung':            '8DCFAQnCUPk',
    'domino-panel-formwork':              'nlUE8QqL5DQ',
    'maximo-panel-formwork':              'ROJJQ-tdidw',
    'peri-up-modular-scaffold':           'rHppk1GCUvo',
    'peri-up-rosett-modular-scaffold':    'lZOnUabo08E',
    'peri-up-easy-frame-scaffolding':     'X2rFztimNQk',
    'peri-up-facade-scaffolding':         'rHppk1GCUvo',
    'peri-up-flex-shoring':               'rHppk1GCUvo',
    'variokit-engineering-construction-kit': 'zrv7Lkd5qgI',
    'acs-self-climbing-system':           'sforIL7rU3Q',
    'rcs-rail-climbing-system':           '9lWscq51Soc',
    'rcs-max-klettersystem':              'XrLlZQf0flQ',
    'scs-climbing-system':                'nQFyXcSVc1Q',
    'multiprop-aluminium-slab-props':     'dothgJ6xPz8',
    'liwa-%E9%92%A2%E6%A1%86%E6%A8%A1%E6%9D%BF': 'fpmvkKH-hc8',
}

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(BASE, 'mnt', '创建产品网站')
CATS_DIR = os.path.join(SITE, 'categories')
PRODS_DIR = os.path.join(SITE, 'products')

os.makedirs(CATS_DIR, exist_ok=True)
os.makedirs(PRODS_DIR, exist_ok=True)

with open(os.path.join(BASE, 'products_v2.json'), encoding='utf-8') as f:
    DATA = json.load(f)

PERI_RED   = '#e3000f'
PERI_YELLOW= '#f5a800'

def total_products_in_cat(cat):
    """Return product count whether cat has subcategories or products."""
    if 'subcategories' in cat:
        return sum(len(sc['products']) for sc in cat['subcategories'].values())
    return len(cat.get('products', []))

# ---- Translations --------------------------------------------------------
# Build flat label lookups (main cats only; subcats handled inline)
CAT_LABELS = {
    'zh': {k: k.replace('_', '/') for k in DATA},
    'en': {k: DATA[k]['en'] for k in DATA},
    'es': {k: DATA[k]['es'] for k in DATA},
    'de': {k: DATA[k]['de'] for k in DATA},
}
NAV_ITEMS = {
    'zh': {'home':'首页','products':'产品目录','contact':'联系我们','search':'搜索产品'},
    'en': {'home':'Home','products':'Products','contact':'Contact','search':'Search'},
    'es': {'home':'Inicio','products':'Productos','contact':'Contacto','search':'Buscar'},
    'de': {'home':'Startseite','products':'Produkte','contact':'Kontakt','search':'Suche'},
}
BTN = {
    'zh': {'learn':'了解更多','inquiry':'发送询价','view_all':'查看全部产品','visit':'访问中文官网'},
    'en': {'learn':'Learn More','inquiry':'Send Inquiry','view_all':'View All Products','visit':'Visit PERI China'},
    'es': {'learn':'Saber Más','inquiry':'Enviar Consulta','view_all':'Ver Todos','visit':'Visitar PERI China'},
    'de': {'learn':'Mehr erfahren','inquiry':'Anfrage senden','view_all':'Alle Produkte','visit':'PERI China besuchen'},
}

# ---- Shared CSS / JS -------------------------------------------------------
SHARED_HEAD = '''<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--red:#e3000f;--yellow:#f5a800;--dark:#1a1a1a;--grey:#f4f4f4}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Helvetica Neue',Arial,sans-serif;color:var(--dark);background:#fff}
a{color:inherit;text-decoration:none}
/* NAV */
.nav{background:var(--dark);display:flex;align-items:center;padding:0 32px;height:60px;position:sticky;top:0;z-index:100}
.nav-logo{display:flex;align-items:center;gap:10px;margin-right:auto}
.nav-logo img{height:32px}
.nav-logo span{color:#fff;font-size:15px;font-weight:600}
.nav-links{display:flex;gap:28px}
.nav-links a{color:#ccc;font-size:13px;transition:.2s}
.nav-links a:hover{color:#fff}
.lang-bar{display:flex;gap:8px;margin-left:24px}
.lang-bar button{background:none;border:1px solid #555;color:#aaa;padding:2px 8px;border-radius:3px;font-size:11px;cursor:pointer;transition:.2s}
.lang-bar button:hover,.lang-bar button.active{background:var(--red);border-color:var(--red);color:#fff}
/* HERO */
.hero{background:linear-gradient(135deg,var(--dark) 0%,#2d2d2d 100%);color:#fff;padding:48px 32px;text-align:center;border-bottom:4px solid var(--red)}
.hero h1{font-size:2.2rem;margin-bottom:12px}
.hero p{font-size:1rem;color:#ccc;max-width:560px;margin:0 auto}
/* BREADCRUMB */
.breadcrumb{padding:12px 32px;font-size:13px;color:#888;border-bottom:1px solid #eee;background:#fafafa}
.breadcrumb a{color:var(--red)}
.breadcrumb a:hover{text-decoration:underline}
/* CARDS */
.grid{display:grid;gap:24px;padding:32px;max-width:1200px;margin:0 auto}
.grid-3{grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}
.grid-4{grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}
.card{background:#fff;border:1px solid #e8e8e8;border-radius:8px;overflow:hidden;cursor:pointer;transition:transform .2s,box-shadow .2s}
.card:hover{transform:translateY(-4px);box-shadow:0 8px 24px rgba(0,0,0,.12)}
.card-img{width:100%;height:180px;object-fit:cover;background:#f0f0f0;display:block}
.card-img-placeholder{width:100%;height:180px;background:linear-gradient(135deg,#e8e8e8,#d0d0d0);display:flex;align-items:center;justify-content:center;font-size:40px;color:#aaa}
.card-body{padding:16px}
.card-badge{display:inline-block;background:var(--yellow);color:var(--dark);font-size:10px;font-weight:700;padding:2px 8px;border-radius:3px;margin-bottom:8px;text-transform:uppercase}
.card-badge-red{display:inline-block;background:var(--red);color:#fff;font-size:10px;font-weight:700;padding:2px 8px;border-radius:3px;margin-bottom:8px}
.card-title{font-size:15px;font-weight:700;margin-bottom:6px;line-height:1.3}
.card-desc{font-size:12px;color:#666;line-height:1.5;margin-bottom:12px}
.card-count{font-size:11px;color:#999}
/* SUBCATEGORY STRIP */
.subcat-strip{padding:8px 32px;background:#f9f9f9;border-bottom:1px solid #eee;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.subcat-strip span{font-size:12px;color:#888}
.subcat-chip{display:inline-block;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;background:var(--yellow);color:var(--dark);cursor:pointer;transition:.15s}
.subcat-chip:hover{background:var(--red);color:#fff}
/* SECTION TITLE */
.sec{padding:24px 32px 0}
.sec h2{font-size:1.4rem;border-left:4px solid var(--red);padding-left:12px}
.sec p{color:#666;font-size:13px;margin-top:6px}
/* BTN */
.btn{display:inline-block;padding:10px 20px;border-radius:4px;font-size:13px;font-weight:600;cursor:pointer;transition:.2s;border:none}
.btn-red{background:var(--red);color:#fff}
.btn-red:hover{background:#b8000b}
.btn-outline{background:none;border:2px solid var(--red);color:var(--red)}
.btn-outline:hover{background:var(--red);color:#fff}
/* PRODUCT PAGE */
.prod-hero{display:grid;grid-template-columns:1fr 1fr;gap:32px;max-width:1100px;margin:0 auto;padding:32px}
.prod-img{width:100%;max-height:400px;object-fit:contain;border-radius:8px;background:#f5f5f5}
.prod-info h1{font-size:1.8rem;margin-bottom:12px}
.prod-info .badge{background:var(--red);color:#fff;padding:3px 10px;border-radius:3px;font-size:11px;display:inline-block;margin-bottom:12px}
.prod-info .badge-subcat{background:var(--yellow);color:var(--dark);padding:3px 10px;border-radius:3px;font-size:11px;display:inline-block;margin-bottom:12px;margin-left:6px}
.prod-info p{color:#555;line-height:1.7;margin-bottom:20px}
.prod-cta{display:flex;gap:12px;flex-wrap:wrap}
/* INQUIRY FORM */
.inquiry-box{background:var(--grey);border-radius:8px;padding:24px;margin-top:32px}
.inquiry-box h3{margin-bottom:16px;font-size:1rem}
.form-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.form-row input,.form-row select,textarea{width:100%;padding:10px;border:1px solid #ddd;border-radius:4px;font-size:13px}
textarea{width:100%;padding:10px;border:1px solid #ddd;border-radius:4px;font-size:13px;resize:vertical;min-height:80px;margin-bottom:12px}
/* FOOTER */
footer{background:var(--dark);color:#aaa;text-align:center;padding:32px;font-size:12px;margin-top:64px}
footer a{color:var(--yellow)}
/* SEARCH */
.search-bar{display:flex;gap:8px;max-width:500px;margin:20px auto 0}
.search-bar input{flex:1;padding:10px 16px;border:2px solid #555;background:rgba(255,255,255,.1);color:#fff;border-radius:4px;font-size:14px}
.search-bar input::placeholder{color:#999}
.search-bar button{padding:10px 20px;background:var(--red);color:#fff;border:none;border-radius:4px;cursor:pointer}
#search-results{padding:24px 32px;max-width:1200px;margin:0 auto}
/* YOUTUBE */
.yt-section{max-width:1100px;margin:0 auto;padding:0 32px 40px}
.yt-section h3{font-size:1.05rem;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px;border-left:4px solid #ff0000;padding-left:12px}
.yt-embed{position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:10px;background:#000;margin-bottom:16px;box-shadow:0 4px 16px rgba(0,0,0,.15)}
.yt-embed iframe{position:absolute;top:0;left:0;width:100%;height:100%;border:0}
.btn-yt{background:#ff0000;color:#fff;display:inline-flex;align-items:center;gap:8px;padding:10px 20px;border-radius:4px;font-size:13px;font-weight:600;transition:.2s}
.btn-yt:hover{background:#cc0000;color:#fff}
/* CLICKABLE IMAGE HINT */
.prod-img-link{display:block;position:relative}
.prod-img-link::after{content:'↗ cn.peri.com';position:absolute;bottom:8px;right:8px;background:rgba(0,0,0,.6);color:#fff;font-size:11px;padding:3px 8px;border-radius:3px;opacity:0;transition:.2s}
.prod-img-link:hover::after{opacity:1}
@media(max-width:700px){
  .prod-hero{grid-template-columns:1fr}
  .form-row{grid-template-columns:1fr}
  .grid-3,.grid-4{grid-template-columns:1fr 1fr}
  .hero h1{font-size:1.6rem}
}
</style>'''

LANG_JS = '''<script>
const LANG_DATA={};
function setLang(l){
  document.querySelectorAll('[data-'+l+']').forEach(el=>{el.textContent=el.dataset[l]});
  document.querySelectorAll('.lang-bar button').forEach(b=>b.classList.toggle('active',b.dataset.l===l));
  localStorage.setItem('periLang',l);
}
document.addEventListener('DOMContentLoaded',()=>{
  const saved=localStorage.getItem('periLang')||'zh';
  setLang(saved);
});
</script>'''

def nav_html(active='home'):
    return f'''<nav class="nav">
  <div class="nav-logo">
    <svg width="48" height="20" viewBox="0 0 120 50"><rect width="120" height="50" fill="#e3000f"/><text x="10" y="38" font-family="Arial" font-weight="900" font-size="38" fill="white">PERI</text></svg>
    <span>GCB Hub</span>
  </div>
  <div class="nav-links">
    <a href="../index.html" data-zh="首页" data-en="Home" data-es="Inicio" data-de="Startseite">首页</a>
    <a href="https://cn.peri.com" target="_blank" data-zh="中文官网" data-en="PERI China" data-es="PERI China" data-de="PERI China">中文官网</a>
  </div>
  <div class="lang-bar">
    <button data-l="zh" onclick="setLang('zh')">中文</button>
    <button data-l="en" onclick="setLang('en')">EN</button>
    <button data-l="es" onclick="setLang('es')">ES</button>
    <button data-l="de" onclick="setLang('de')">DE</button>
  </div>
</nav>'''

def nav_html_root():
    return '''<nav class="nav">
  <div class="nav-logo">
    <svg width="48" height="20" viewBox="0 0 120 50"><rect width="120" height="50" fill="#e3000f"/><text x="10" y="38" font-family="Arial" font-weight="900" font-size="38" fill="white">PERI</text></svg>
    <span>GCB Hub</span>
  </div>
  <div class="nav-links">
    <a href="https://cn.peri.com" target="_blank" data-zh="中文官网" data-en="PERI China" data-es="PERI China" data-de="PERI China">中文官网</a>
  </div>
  <div class="lang-bar">
    <button data-l="zh" onclick="setLang('zh')">中文</button>
    <button data-l="en" onclick="setLang('en')">EN</button>
    <button data-l="es" onclick="setLang('es')">ES</button>
    <button data-l="de" onclick="setLang('de')">DE</button>
  </div>
</nav>'''

def footer_html():
    return '''<footer>
  <p data-zh="© PERI GCB 产品信息中心 | 南美洲、东欧、非洲地区团队"
     data-en="© PERI GCB Product Information Hub | South America, Eastern Europe, Africa Teams"
     data-es="© PERI GCB Centro de Información de Productos | Equipos de América del Sur, Europa del Este, África"
     data-de="© PERI GCB Produktinformationszentrum | Teams Südamerika, Osteuropa, Afrika">
     © PERI GCB 产品信息中心 | 南美洲、东欧、非洲地区团队</p>
  <p style="margin-top:8px">
    <a href="https://cn.peri.com" target="_blank">cn.peri.com</a>
  </p>
</footer>'''

def img_or_placeholder(url, alt='', cls='card-img'):
    if url:
        return f'<img class="{cls}" src="{url}" alt="{alt}" loading="lazy" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'">\n<div class="card-img-placeholder" style="display:none">🔧</div>'
    return f'<div class="card-img-placeholder">🔧</div>'

# ============================================================
# 1. HOMEPAGE (index.html)
# ============================================================
def build_homepage():
    cat_cards = ''
    for cat_key, cat in DATA.items():
        count = total_products_in_cat(cat)
        display_name = cat_key.replace('_', '/')

        # For subcategorized cats, show a brief subcategory hint
        if 'subcategories' in cat:
            subcat_names = '、'.join(cat['subcategories'].keys())
            extra_desc = f'<div style="font-size:11px;color:#888;margin-top:4px">{subcat_names}</div>'
        else:
            extra_desc = ''

        cat_cards += f'''
    <div class="card" onclick="location.href='categories/{cat['slug']}.html'" style="cursor:pointer">
      {img_or_placeholder(cat.get('img',''), display_name)}
      <div class="card-body">
        <div class="card-badge" data-zh="{display_name}" data-en="{cat['en']}" data-es="{cat['es']}" data-de="{cat['de']}">{display_name}</div>
        <div class="card-title" data-zh="{display_name}" data-en="{cat['en']}" data-es="{cat['es']}" data-de="{cat['de']}">{display_name}</div>
        {extra_desc}
        <div class="card-count" data-zh="{count} 个产品" data-en="{count} products" data-es="{count} productos" data-de="{count} Produkte">{count} 个产品</div>
      </div>
    </div>'''

    html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
  <title>GCB — PERI 产品信息中心</title>
  {SHARED_HEAD}
</head>
<body>
{nav_html_root()}
<div class="hero">
  <h1 data-zh="PERI 产品信息中心" data-en="PERI Product Information Hub" data-es="Centro de Información de Productos PERI" data-de="PERI Produktinformationszentrum">PERI 产品信息中心</h1>
  <p data-zh="面向南美洲、东欧、非洲的GCB团队 — 了解派利完整产品系列" data-en="For GCB Teams in South America, Eastern Europe & Africa — Explore the full PERI product range" data-es="Para equipos GCB en Sudamérica, Europa del Este y África — Explore la gama completa de productos PERI" data-de="Für GCB-Teams in Südamerika, Osteuropa und Afrika — Entdecken Sie das vollständige PERI-Produktprogramm">面向南美洲、东欧、非洲的GCB团队 — 了解派利完整产品系列</p>
  <div class="search-bar">
    <input type="text" id="q" placeholder="搜索产品... / Search products..." onkeydown="if(event.key==='Enter')doSearch()">
    <button onclick="doSearch()" data-zh="搜索" data-en="Search" data-es="Buscar" data-de="Suchen">搜索</button>
  </div>
</div>

<div class="sec">
  <h2 data-zh="产品分类" data-en="Product Categories" data-es="Categorías de Productos" data-de="Produktkategorien">产品分类</h2>
  <p data-zh="点击分类查看所有产品" data-en="Click a category to browse products" data-es="Haga clic en una categoría para ver los productos" data-de="Klicken Sie auf eine Kategorie, um Produkte anzuzeigen">点击分类查看所有产品</p>
</div>
<div class="grid grid-3">
  {cat_cards}
</div>

<div style="text-align:center;padding:32px">
  <a href="https://cn.peri.com/products.html" target="_blank" class="btn btn-red"
     data-zh="访问 cn.peri.com 查看全部产品" data-en="Visit cn.peri.com for full product range"
     data-es="Visitar cn.peri.com para ver todos los productos" data-de="cn.peri.com besuchen für alle Produkte">
     访问 cn.peri.com 查看全部产品
  </a>
</div>

{footer_html()}
{LANG_JS}
<script>
function doSearch(){{
  const q=document.getElementById('q').value.trim();
  if(q) window.location='search.html?q='+encodeURIComponent(q);
}}
</script>
</body></html>'''
    with open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print('✅ index.html')

# ============================================================
# 2. CATEGORY PAGES (with subcategory support)
# ============================================================
def build_category_page(cat_key, cat):
    display_name = cat_key.replace('_', '/')
    count = total_products_in_cat(cat)

    if 'subcategories' in cat:
        # Show subcategory cards instead of products
        subcat_cards = ''
        for sc_key, sc in cat['subcategories'].items():
            sc_count = len(sc['products'])
            subcat_cards += f'''
    <div class="card" onclick="location.href='../categories/{sc['slug']}.html'" style="cursor:pointer">
      {img_or_placeholder(sc.get('img',''), sc_key)}
      <div class="card-body">
        <div class="card-badge-red"
             data-zh="{sc_key}" data-en="{sc['en']}" data-es="{sc['es']}" data-de="{sc['de']}">{sc_key}</div>
        <div class="card-title" data-zh="{sc_key}" data-en="{sc['en']}" data-es="{sc['es']}" data-de="{sc['de']}">{sc_key}</div>
        <div class="card-desc" data-zh="{sc['desc_zh']}" data-en="{sc['en']}" data-es="{sc['es']}" data-de="{sc['de']}">{sc['desc_zh']}</div>
        <div class="card-count" data-zh="{sc_count} 个产品" data-en="{sc_count} products" data-es="{sc_count} productos" data-de="{sc_count} Produkte">{sc_count} 个产品</div>
      </div>
    </div>'''

        content = f'''<div class="sec">
  <h2 data-zh="共 {count} 个产品，按类别浏览" data-en="{count} Products by Subcategory"
      data-es="{count} Productos por Subcategoría" data-de="{count} Produkte nach Kategorie">共 {count} 个产品，按类别浏览</h2>
  <p data-zh="{cat['desc_zh']}" data-en="{cat['en']}" data-es="{cat['es']}" data-de="{cat['de']}">{cat['desc_zh']}</p>
</div>
<div class="grid grid-3">
  {subcat_cards}
</div>'''

    else:
        # Show products directly (non-subcategorized categories)
        product_cards = ''
        for p in cat['products']:
            slug, name_zh, desc_zh, img = p[0], p[1], p[2], p[3]
            product_cards += f'''
    <div class="card" onclick="location.href='../products/{slug}.html'">
      {img_or_placeholder(img, name_zh)}
      <div class="card-body">
        <div class="card-title">{name_zh}</div>
        <div class="card-desc">{desc_zh}</div>
        <span class="btn btn-outline" style="font-size:11px;padding:5px 12px"
              data-zh="了解更多" data-en="Learn More" data-es="Más info" data-de="Mehr">了解更多</span>
      </div>
    </div>'''

        content = f'''<div class="sec">
  <h2 data-zh="共 {count} 个产品" data-en="{count} Products"
      data-es="{count} Productos" data-de="{count} Produkte">共 {count} 个产品</h2>
</div>
<div class="grid grid-4">
  {product_cards}
</div>'''

    html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
  <title>{display_name} — PERI GCB</title>
  {SHARED_HEAD}
</head>
<body>
{nav_html()}
<div class="breadcrumb">
  <a href="../index.html" data-zh="首页" data-en="Home" data-es="Inicio" data-de="Startseite">首页</a> ›
  <span data-zh="{display_name}" data-en="{cat['en']}" data-es="{cat['es']}" data-de="{cat['de']}">{display_name}</span>
</div>
<div class="hero" style="padding:32px">
  <h1 data-zh="{display_name}" data-en="{cat['en']}" data-es="{cat['es']}" data-de="{cat['de']}">{display_name}</h1>
  <p data-zh="{cat['desc_zh']}" data-en="{cat['en']}" data-es="{cat['es']}" data-de="{cat['de']}">{cat['desc_zh']}</p>
</div>
{content}
{footer_html()}
{LANG_JS}
</body></html>'''
    fname = os.path.join(CATS_DIR, f"{cat['slug']}.html")
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  ✅ categories/{cat["slug"]}.html ({count} products, {"subcategorized" if "subcategories" in cat else "flat"})')

# ============================================================
# 2b. SUBCATEGORY PAGES
# ============================================================
def build_subcategory_page(cat_key, cat, sc_key, sc):
    """Build a category page for a subcategory (e.g., categories/wall-formwork.html)"""
    cat_display = cat_key.replace('_', '/')
    sc_count = len(sc['products'])

    product_cards = ''
    for p in sc['products']:
        slug, name_zh, desc_zh, img = p[0], p[1], p[2], p[3]
        product_cards += f'''
    <div class="card" onclick="location.href='../products/{slug}.html'">
      {img_or_placeholder(img, name_zh)}
      <div class="card-body">
        <div class="card-badge-red" data-zh="{sc_key}" data-en="{sc['en']}" data-es="{sc['es']}" data-de="{sc['de']}">{sc_key}</div>
        <div class="card-title">{name_zh}</div>
        <div class="card-desc">{desc_zh}</div>
        <span class="btn btn-outline" style="font-size:11px;padding:5px 12px"
              data-zh="了解更多" data-en="Learn More" data-es="Más info" data-de="Mehr">了解更多</span>
      </div>
    </div>'''

    html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
  <title>{sc_key} — {cat_display} — PERI GCB</title>
  {SHARED_HEAD}
</head>
<body>
{nav_html()}
<div class="breadcrumb">
  <a href="../index.html" data-zh="首页" data-en="Home" data-es="Inicio" data-de="Startseite">首页</a> ›
  <a href="../categories/{cat['slug']}.html" data-zh="{cat_display}" data-en="{cat['en']}" data-es="{cat['es']}" data-de="{cat['de']}">{cat_display}</a> ›
  <span data-zh="{sc_key}" data-en="{sc['en']}" data-es="{sc['es']}" data-de="{sc['de']}">{sc_key}</span>
</div>
<div class="hero" style="padding:32px">
  <h1 data-zh="{sc_key}" data-en="{sc['en']}" data-es="{sc['es']}" data-de="{sc['de']}">{sc_key}</h1>
  <p data-zh="{sc['desc_zh']}" data-en="{sc['en']}" data-es="{sc['es']}" data-de="{sc['de']}">{sc['desc_zh']}</p>
</div>
<div class="sec">
  <h2 data-zh="共 {sc_count} 个产品" data-en="{sc_count} Products"
      data-es="{sc_count} Productos" data-de="{sc_count} Produkte">共 {sc_count} 个产品</h2>
</div>
<div class="grid grid-4">
  {product_cards}
</div>
{footer_html()}
{LANG_JS}
</body></html>'''
    fname = os.path.join(CATS_DIR, f"{sc['slug']}.html")
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'    ✅ categories/{sc["slug"]}.html ({sc_count} products)')

# ============================================================
# 3. PRODUCT PAGES
# ============================================================
def build_product_page(cat_key, cat, p, subcat_key=None, subcat=None):
    slug, name_zh, desc_zh, img = p[0], p[1], p[2], p[3]
    cat_display = cat_key.replace('_', '/')
    cn_url = f'https://cn.peri.com/products/{slug}.html'

    # Determine back-link for breadcrumb
    if subcat:
        back_cat_slug = subcat['slug']
        back_cat_label_zh = subcat_key
        back_cat_label_en = subcat['en']
        back_cat_label_es = subcat['es']
        back_cat_label_de = subcat['de']
        badge_zh = subcat_key
        badge_en = subcat['en']
        badge_es = subcat['es']
        badge_de = subcat['de']
        breadcrumb_extra = f'''
  <a href="../categories/{cat['slug']}.html" data-zh="{cat_display}" data-en="{cat['en']}" data-es="{cat['es']}" data-de="{cat['de']}">{cat_display}</a> ›
  <a href="../categories/{back_cat_slug}.html" data-zh="{back_cat_label_zh}" data-en="{back_cat_label_en}" data-es="{back_cat_label_es}" data-de="{back_cat_label_de}">{back_cat_label_zh}</a> ›'''
    else:
        back_cat_slug = cat['slug']
        badge_zh = cat_display
        badge_en = cat['en']
        badge_es = cat['es']
        badge_de = cat['de']
        breadcrumb_extra = f'''
  <a href="../categories/{cat['slug']}.html" data-zh="{cat_display}" data-en="{cat['en']}" data-es="{cat['es']}" data-de="{cat['de']}">{cat_display}</a> ›'''

    # Image — clickable, links to cn.peri.com
    if img:
        img_inner = (f'<img class="prod-img" src="{img}" alt="{name_zh}" '
                     f'onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'">'
                     f'<div style="display:none;width:100%;height:300px;background:#f0f0f0;'
                     f'align-items:center;justify-content:center;font-size:60px;border-radius:8px">🔧</div>')
    else:
        img_inner = ('<div style="width:100%;height:300px;background:#f0f0f0;display:flex;'
                     'align-items:center;justify-content:center;font-size:60px;border-radius:8px">🔧</div>')
    img_tag = (f'<a href="{cn_url}" target="_blank" class="prod-img-link" '
               f'title="点击前往 cn.peri.com 查看完整产品信息">{img_inner}</a>'
               f'<p style="font-size:11px;color:#999;margin-top:6px;text-align:center">'
               f'↗ <a href="{cn_url}" target="_blank" style="color:var(--red)">在 cn.peri.com 查看完整信息</a></p>')

    # YouTube section
    yt_id = YT_IDS.get(slug, '')
    yt_query = urllib.parse.quote(name_zh)
    yt_search_url = f'https://www.youtube.com/@perigroup/search?query={yt_query}'

    if yt_id:
        yt_embed = f'''  <div class="yt-embed">
    <iframe src="https://www.youtube-nocookie.com/embed/{yt_id}"
            title="{name_zh} — PERI Video"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen></iframe>
  </div>'''
    else:
        yt_embed = ''

    yt_section = f'''<div class="yt-section">
  <h3>▶ <span data-zh="PERI 产品视频" data-en="PERI Product Video"
               data-es="Video del Producto PERI" data-de="PERI Produktvideo">PERI 产品视频</span></h3>
  {yt_embed}
  <a href="{yt_search_url}" target="_blank" class="btn btn-yt"
     data-zh="在 PERI YouTube 频道搜索此产品" data-en="Search this product on PERI YouTube"
     data-es="Buscar en PERI YouTube" data-de="Auf PERI YouTube suchen">
    ▶&nbsp; 在 PERI YouTube 频道搜索
  </a>
</div>'''

    # Badge: show main category + subcategory if applicable
    if subcat:
        badge_html = (f'<span class="badge" data-zh="{cat_display}" data-en="{cat["en"]}" '
                      f'data-es="{cat["es"]}" data-de="{cat["de"]}">{cat_display}</span>'
                      f'<span class="badge-subcat" data-zh="{subcat_key}" data-en="{subcat["en"]}" '
                      f'data-es="{subcat["es"]}" data-de="{subcat["de"]}">{subcat_key}</span>')
    else:
        badge_html = (f'<span class="badge" data-zh="{badge_zh}" data-en="{badge_en}" '
                      f'data-es="{badge_es}" data-de="{badge_de}">{badge_zh}</span>')

    html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
  <title>{name_zh} — PERI GCB</title>
  {SHARED_HEAD}
</head>
<body>
{nav_html()}
<div class="breadcrumb">
  <a href="../index.html" data-zh="首页" data-en="Home" data-es="Inicio" data-de="Startseite">首页</a> ›{breadcrumb_extra}
  <span>{name_zh}</span>
</div>

<div class="prod-hero">
  <div>
    {img_tag}
  </div>
  <div class="prod-info">
    {badge_html}
    <h1>{name_zh}</h1>
    <p style="color:#444;line-height:1.8;margin-bottom:20px;font-size:15px">{desc_zh}</p>
    <div class="prod-cta">
      <a href="{cn_url}" target="_blank" class="btn btn-red"
         data-zh="↗ 前往中文官网查看" data-en="↗ View on PERI China" data-es="↗ Ver en PERI China" data-de="↗ Auf PERI China ansehen">
         ↗ 前往中文官网查看
      </a>
      <button class="btn btn-outline" onclick="document.getElementById('inquiry').scrollIntoView({{behavior:'smooth'}})"
              data-zh="发送询价" data-en="Send Inquiry" data-es="Enviar Consulta" data-de="Anfrage senden">
              发送询价
      </button>
    </div>

    <div class="inquiry-box" id="inquiry" style="margin-top:24px">
      <h3 data-zh="产品询价" data-en="Product Inquiry" data-es="Consulta de Producto" data-de="Produktanfrage">产品询价</h3>
      <div class="form-row">
        <input type="text" placeholder="姓名 / Name" id="fi-name">
        <input type="email" placeholder="邮箱 / Email" id="fi-email">
      </div>
      <div class="form-row">
        <input type="text" placeholder="公司 / Company" id="fi-company">
        <input type="text" placeholder="国家 / Country" id="fi-country">
      </div>
      <textarea placeholder="询价内容 / Inquiry message..." id="fi-msg" rows="3"></textarea>
      <button class="btn btn-red" onclick="sendInquiry('{name_zh}')"
              data-zh="发送" data-en="Send" data-es="Enviar" data-de="Senden">发送</button>
    </div>
  </div>
</div>

{yt_section}

{footer_html()}
{LANG_JS}
<script>
function sendInquiry(product){{
  const name=document.getElementById('fi-name').value;
  const email=document.getElementById('fi-email').value;
  const company=document.getElementById('fi-company').value;
  const country=document.getElementById('fi-country').value;
  const msg=document.getElementById('fi-msg').value;
  const body=`产品询价: ${{product}}\\n姓名: ${{name}}\\n公司: ${{company}}\\n国家: ${{country}}\\n\\n${{msg}}`;
  window.location='mailto:?subject=PERI产品询价: '+encodeURIComponent(product)+'&body='+encodeURIComponent(body);
}}
</script>
</body></html>'''
    fname = os.path.join(PRODS_DIR, f'{slug}.html')
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(html)

# ============================================================
# 4. SEARCH PAGE
# ============================================================
def build_search_page():
    # Build JS product index (handles both subcategorized and flat cats)
    products_js = []
    for cat_key, cat in DATA.items():
        cat_display = cat_key.replace('_', '/')
        if 'subcategories' in cat:
            for sc_key, sc in cat['subcategories'].items():
                for p in sc['products']:
                    products_js.append({
                        'slug': p[0], 'name': p[1], 'desc': p[2],
                        'cat_zh': f'{cat_display} › {sc_key}',
                        'cat_en': f'{cat["en"]} › {sc["en"]}',
                        'url': f'products/{p[0]}.html'
                    })
        else:
            for p in cat['products']:
                products_js.append({
                    'slug': p[0], 'name': p[1], 'desc': p[2],
                    'cat_zh': cat_display, 'cat_en': cat['en'],
                    'url': f'products/{p[0]}.html'
                })
    js_data = json.dumps(products_js, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
  <title>搜索 — PERI GCB</title>
  {SHARED_HEAD}
</head>
<body>
{nav_html_root()}
<div class="hero" style="padding:32px">
  <h1 data-zh="产品搜索" data-en="Product Search" data-es="Búsqueda de Productos" data-de="Produktsuche">产品搜索</h1>
  <div class="search-bar">
    <input type="text" id="q" placeholder="输入产品名称..." oninput="doSearch()">
    <button onclick="doSearch()">搜索</button>
  </div>
</div>
<div id="results" class="grid grid-4" style="min-height:200px"></div>
{footer_html()}
{LANG_JS}
<script>
const PRODUCTS = {js_data};
function doSearch(){{
  const q=(document.getElementById('q').value||'').toLowerCase();
  const res=q.length<1?PRODUCTS:PRODUCTS.filter(p=>
    p.name.toLowerCase().includes(q)||p.desc.toLowerCase().includes(q)||p.cat_zh.toLowerCase().includes(q)
  );
  document.getElementById('results').innerHTML = res.length===0
    ? '<p style="padding:32px;color:#999">未找到相关产品</p>'
    : res.map(p=>`<div class="card" onclick="location.href='${{p.url}}'">
        <div class="card-img-placeholder">🔧</div>
        <div class="card-body">
          <div class="card-badge">${{p.cat_zh}}</div>
          <div class="card-title">${{p.name}}</div>
          <div class="card-desc">${{p.desc.slice(0,60)}}...</div>
        </div></div>`).join('');
}}
window.onload=()=>{{
  const p=new URLSearchParams(location.search);
  if(p.get('q')){{document.getElementById('q').value=p.get('q');doSearch();}}
  else doSearch();
}};
</script>
</body></html>'''
    with open(os.path.join(SITE, 'search.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print('✅ search.html')

# ============================================================
# RUN
# ============================================================
if __name__ == '__main__':
    print('\n🔨 Building PERI GCB website...')
    build_homepage()
    build_search_page()

    total_products = 0
    total_pages = 0

    for cat_key, cat in DATA.items():
        build_category_page(cat_key, cat)
        total_pages += 1

        if 'subcategories' in cat:
            for sc_key, sc in cat['subcategories'].items():
                build_subcategory_page(cat_key, cat, sc_key, sc)
                total_pages += 1
                for p in sc['products']:
                    build_product_page(cat_key, cat, p, subcat_key=sc_key, subcat=sc)
                    total_products += 1
        else:
            for p in cat['products']:
                build_product_page(cat_key, cat, p)
                total_products += 1

    print(f'\n✅ Done! Built:')
    print(f'   - 1 homepage (index.html)')
    print(f'   - 1 search page (search.html)')
    print(f'   - {total_pages} category/subcategory pages (categories/)')
    print(f'   - {total_products} product pages (products/)')
    print(f'\n📁 Site ready at: {SITE}')
    print('🚀 Now double-click deploy-peri-gcb.command to publish!')
