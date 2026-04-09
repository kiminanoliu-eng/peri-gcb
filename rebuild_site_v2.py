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
from source_rules import (
    is_direct_pdf_like,
    is_official_peri_host,
    pdf_matches_slug,
)

# YouTube video IDs for key products (from @perigroup channel)
YT_IDS = {
    'handset-alpha':                      'c3FOoHAjQEs',
    'trio-rahmenschalung':                'ypBa9srkqy8',
    'trio-schalungssystem':               'ypBa9srkqy8',
    'skydeck-slab-formwork':              'CgOEI3YtG_E',
    'multiflex-girder-slab-formwork':     'kHOmVl6O5us',
    'gridflex-deckenschalung':            'd1SUjg7Cc8A',
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
    'quattro-column-formwork':            'OWpNmrq4qEc',
}

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = BASE  # 直接输出到根目录，无需手动复制
CATS_DIR = os.path.join(SITE, 'categories')
PRODS_DIR = os.path.join(SITE, 'products')

os.makedirs(CATS_DIR, exist_ok=True)
os.makedirs(PRODS_DIR, exist_ok=True)

with open(os.path.join(BASE, 'products_v2.json'), encoding='utf-8') as f:
    DATA = json.load(f)

# Load China projects
try:
    with open(os.path.join(BASE, 'china_projects.json'), encoding='utf-8') as f:
        CHINA_PROJECTS = json.load(f)['projects']
except:
    CHINA_PROJECTS = []

# Load PDF links
try:
    with open(os.path.join(BASE, 'product_pdf_links.json'), encoding='utf-8') as f:
        PDF_LINKS = json.load(f)
except:
    PDF_LINKS = {}

try:
    with open(os.path.join(BASE, 'pdf_overrides.json'), encoding='utf-8') as f:
        PDF_OVERRIDES = json.load(f)
except:
    PDF_OVERRIDES = {}

TRUSTED_PDF_LINKS = {}
TRUSTED_PDF_LINKS.update(PDF_LINKS)
TRUSTED_PDF_LINKS.update(PDF_OVERRIDES)

def sanitize_pdf_url(url, slug):
    if not isinstance(url, str):
        return ''
    url = url.strip()
    if not url:
        return ''

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ('http', 'https') or not is_official_peri_host(parsed.netloc):
        return ''

    if not is_direct_pdf_like(url):
        return ''

    trusted_url = TRUSTED_PDF_LINKS.get(slug, '')
    if trusted_url and url == trusted_url:
        return url

    if not pdf_matches_slug(url, slug):
        return ''

    return url


def normalize_project_key(value):
    value = (value or '').strip().lower()
    value = re.sub(r'\s+', ' ', value)
    return value


def dedupe_homepage_projects(projects):
    """Keep homepage China projects stable and remove obvious duplicate variants."""
    unique = []
    seen = set()

    for project in projects:
        primary_key = normalize_project_key(project.get('name_en'))
        fallback_keys = [
            normalize_project_key(project.get('link')),
            normalize_project_key(project.get('name_zh')),
        ]

        dedupe_key = None
        if primary_key:
            dedupe_key = f"name_en:{primary_key}"
        else:
            for key in fallback_keys:
                if key:
                    dedupe_key = f"fallback:{key}"
                    break

        if not dedupe_key or dedupe_key in seen:
            continue

        seen.add(dedupe_key)
        unique.append(project)

    return unique

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
    'pt': {k: DATA[k].get('pt', DATA[k]['en']) for k in DATA},
    'sr': {k: DATA[k].get('sr', DATA[k]['en']) for k in DATA},
    'hu': {k: DATA[k].get('hu', DATA[k]['en']) for k in DATA},
}
NAV_ITEMS = {
    'zh': {'home':'首页','products':'产品目录','contact':'联系我们','search':'搜索产品'},
    'en': {'home':'Home','products':'Products','contact':'Contact','search':'Search'},
    'es': {'home':'Inicio','products':'Productos','contact':'Contacto','search':'Buscar'},
    'de': {'home':'Startseite','products':'Produkte','contact':'Kontakt','search':'Suche'},
    'pt': {'home':'Início','products':'Produtos','contact':'Contato','search':'Pesquisar'},
    'sr': {'home':'Početna','products':'Proizvodi','contact':'Kontakt','search':'Pretraga'},
    'hu': {'home':'Kezdőlap','products':'Termékek','contact':'Kapcsolat','search':'Keresés'},
}
BTN = {
    'zh': {'learn':'了解更多','inquiry':'发送询价','view_all':'查看全部产品','visit':'访问中文官网'},
    'en': {'learn':'Learn More','inquiry':'Send Inquiry','view_all':'View All Products','visit':'Visit PERI China'},
    'es': {'learn':'Saber Más','inquiry':'Enviar Consulta','view_all':'Ver Todos','visit':'Visitar PERI China'},
    'de': {'learn':'Mehr erfahren','inquiry':'Anfrage senden','view_all':'Alle Produkte','visit':'PERI China besuchen'},
    'pt': {'learn':'Saiba Mais','inquiry':'Enviar Consulta','view_all':'Ver Todos os Produtos','visit':'Visitar PERI China'},
    'sr': {'learn':'Saznaj Više','inquiry':'Pošalji Upit','view_all':'Pogledaj Sve Proizvode','visit':'Posetite PERI China'},
    'hu': {'learn':'Tudjon Meg Többet','inquiry':'Ajánlatkérés','view_all':'Összes Termék','visit':'PERI China Látogatása'},
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
.nav{background:#fff;display:flex;align-items:center;padding:0 32px;height:70px;position:sticky;top:0;z-index:100;border-bottom:1px solid #e0e0e0;box-shadow:0 2px 4px rgba(0,0,0,.05)}
.nav-logo{display:flex;align-items:center;gap:10px;margin-right:auto}
.nav-logo img{height:40px}
.nav-logo span{color:var(--dark);font-size:15px;font-weight:600}
.nav-links{display:flex;gap:28px}
.nav-links a{color:#666;font-size:13px;transition:.2s;font-weight:500}
.nav-links a:hover{color:var(--red)}
.lang-bar{display:flex;gap:8px;margin-left:24px}
.lang-bar button{background:none;border:1px solid #ddd;color:#666;padding:4px 10px;border-radius:4px;font-size:11px;cursor:pointer;transition:.2s;font-weight:500}
.lang-bar button:hover,.lang-bar button.active{background:var(--red);border-color:var(--red);color:#fff}
/* HERO */
.hero{background:#fff;color:var(--dark);padding:60px 32px;text-align:center;border-bottom:3px solid var(--red)}
.hero h1{font-size:2.2rem;margin-bottom:12px;color:var(--dark)}
.hero p{font-size:1rem;color:#666;max-width:560px;margin:0 auto}
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
.search-bar input{flex:1;padding:10px 16px;border:2px solid #ddd;background:#fff;color:var(--dark);border-radius:4px;font-size:14px}
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
    <img src="../peri-logo.webp" alt="PERI">
    <span data-zh="GCB 派利产品中文介绍HUB" data-en="GCB PERI Product Hub" data-es="GCB Centro de Productos PERI" data-de="GCB PERI Produktzentrum" data-pt="GCB Centro de Produtos PERI" data-sr="GCB PERI Centar Proizvoda" data-hu="GCB PERI Termékközpont">GCB 派利产品中文介绍HUB</span>
  </div>
  <div class="nav-links">
    <a href="../index.html" data-zh="首页" data-en="Home" data-es="Inicio" data-de="Startseite" data-pt="Início" data-sr="Početna" data-hu="Kezdőlap">首页</a>
    <a href="https://cn.peri.com" target="_blank" data-zh="中文官网" data-en="PERI China" data-es="PERI China" data-de="PERI China" data-pt="PERI China" data-sr="PERI China" data-hu="PERI China">中文官网</a>
  </div>
  <div class="lang-bar">
    <button data-l="zh" onclick="setLang('zh')">中文</button>
    <button data-l="en" onclick="setLang('en')">EN</button>
    <button data-l="pt" onclick="setLang('pt')">PT</button>
    <button data-l="sr" onclick="setLang('sr')">SR</button>
    <button data-l="es" onclick="setLang('es')">ES</button>
    <button data-l="hu" onclick="setLang('hu')">HU</button>
  </div>
</nav>'''

def nav_html_root():
    return '''<nav class="nav">
  <div class="nav-logo">
    <img src="peri-logo.webp" alt="PERI">
    <span data-zh="GCB 派利产品中文介绍HUB" data-en="GCB PERI Product Hub" data-es="GCB Centro de Productos PERI" data-de="GCB PERI Produktzentrum" data-pt="GCB Centro de Produtos PERI" data-sr="GCB PERI Centar Proizvoda" data-hu="GCB PERI Termékközpont">GCB 派利产品中文介绍HUB</span>
  </div>
  <div class="nav-links">
    <a href="https://cn.peri.com" target="_blank" data-zh="中文官网" data-en="PERI China" data-es="PERI China" data-de="PERI China" data-pt="PERI China" data-sr="PERI China" data-hu="PERI China">中文官网</a>
  </div>
  <div class="lang-bar">
    <button data-l="zh" onclick="setLang('zh')">中文</button>
    <button data-l="en" onclick="setLang('en')">EN</button>
    <button data-l="pt" onclick="setLang('pt')">PT</button>
    <button data-l="sr" onclick="setLang('sr')">SR</button>
    <button data-l="es" onclick="setLang('es')">ES</button>
    <button data-l="hu" onclick="setLang('hu')">HU</button>
  </div>
</nav>'''

def footer_html():
    return '''<footer>
  <p data-zh="© PERI GCB 产品信息中心"
     data-en="© PERI GCB Product Information Hub"
     data-es="© PERI GCB Centro de Información de Productos"
     data-de="© PERI GCB Produktinformationszentrum"
     data-pt="© PERI GCB Centro de Informações de Produtos"
     data-sr="© PERI GCB Centar za Informacije o Proizvodima"
     data-hu="© PERI GCB Termékinformációs Központ">
     © PERI GCB 产品信息中心</p>
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
        <div class="card-badge" data-zh="{display_name}" data-en="{cat['en']}" data-es="{cat['es']}" data-de="{cat['de']}" data-pt="{cat.get('pt', cat['en'])}" data-sr="{cat.get('sr', cat['en'])}" data-hu="{cat.get('hu', cat['en'])}">{display_name}</div>
        <div class="card-title" data-zh="{display_name}" data-en="{cat['en']}" data-es="{cat['es']}" data-de="{cat['de']}" data-pt="{cat.get('pt', cat['en'])}" data-sr="{cat.get('sr', cat['en'])}" data-hu="{cat.get('hu', cat['en'])}">{display_name}</div>
        {extra_desc}
        <div class="card-count" data-zh="{count} 个产品" data-en="{count} products" data-es="{count} productos" data-de="{count} Produkte" data-pt="{count} produtos" data-sr="{count} proizvoda" data-hu="{count} termék">{count} 个产品</div>
      </div>
    </div>'''

    # Generate China projects cards
    homepage_projects = dedupe_homepage_projects(CHINA_PROJECTS)
    china_projects_html = ''
    for proj in homepage_projects:
        china_projects_html += f'''
    <div class="card" onclick="window.open('{proj['link']}', '_blank')" style="cursor:pointer">
      <img class="card-img" src="{proj['image']}" alt="{proj['name_zh']}" loading="lazy">
      <div class="card-body">
        <div class="card-badge-red" data-zh="参建项目" data-en="Project" data-es="Proyecto" data-de="Projekt" data-pt="Projeto" data-sr="Projekat" data-hu="Projekt">参建项目</div>
        <div class="card-title" data-zh="{proj['name_zh']}" data-en="{proj['name_en']}" data-pt="{proj['name_en']}" data-sr="{proj['name_en']}" data-es="{proj['name_en']}" data-hu="{proj['name_en']}">{proj['name_zh']}</div>
        <div class="card-desc">{proj['description']}</div>
        <div style="font-size:11px;color:#999;margin-top:8px">📍 {proj['location']}</div>
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
  <h1 data-zh="PERI 产品信息中心" data-en="PERI Product Information Hub" data-es="Centro de Información de Productos PERI" data-de="PERI Produktinformationszentrum" data-pt="Centro de Informações de Produtos PERI" data-sr="PERI Centar za Informacije o Proizvodima" data-hu="PERI Termékinformációs Központ">PERI 产品信息中心</h1>
  <p data-zh="了解派利完整产品系列" data-en="Explore the full PERI product range" data-es="Explore la gama completa de productos PERI" data-de="Entdecken Sie das vollständige PERI-Produktprogramm" data-pt="Explore a gama completa de produtos PERI" data-sr="Istražite kompletan PERI asortiman proizvoda" data-hu="Fedezze fel a teljes PERI termékpalettát">了解派利完整产品系列</p>
  <div class="search-bar">
    <input type="text" id="q" placeholder="搜索产品... / Search products..." onkeydown="if(event.key==='Enter')doSearch()">
    <button onclick="doSearch()" data-zh="搜索" data-en="Search" data-es="Buscar" data-de="Suchen" data-pt="Pesquisar" data-sr="Pretraga" data-hu="Keresés">搜索</button>
  </div>
</div>

<div class="sec">
  <h2 data-zh="产品分类" data-en="Product Categories" data-es="Categorías de Productos" data-de="Produktkategorien" data-pt="Categorias de Produtos" data-sr="Kategorije Proizvoda" data-hu="Termékkategóriák">产品分类</h2>
  <p data-zh="点击分类查看所有产品" data-en="Click a category to browse products" data-es="Haga clic en una categoría para ver los productos" data-de="Klicken Sie auf eine Kategorie, um Produkte anzuzeigen" data-pt="Clique em uma categoria para navegar pelos produtos" data-sr="Kliknite na kategoriju da pregledate proizvode" data-hu="Kattintson egy kategóriára a termékek böngészéséhez">点击分类查看所有产品</p>
</div>
<div class="grid grid-3">
  {cat_cards}
</div>

<div style="text-align:center;padding:32px">
  <a href="https://cn.peri.com/products.html" target="_blank" class="btn btn-red"
     data-zh="访问 cn.peri.com 查看全部产品" data-en="Visit cn.peri.com for full product range"
     data-es="Visitar cn.peri.com para ver todos los productos" data-de="cn.peri.com besuchen für alle Produkte" data-pt="Visite cn.peri.com para ver todos os produtos" data-sr="Posetite cn.peri.com za sve proizvode" data-hu="Látogassa meg a cn.peri.com oldalt az összes termékért">
     访问 cn.peri.com 查看全部产品
  </a>
</div>

<!-- China Projects Section -->
<div style="background:#f5f5f5;padding:60px 0;margin-top:40px">
  <div class="sec">
    <h2 data-zh="中国参建项目" data-en="Projects in China" data-es="Proyectos en China" data-de="Projekte in China" data-pt="Projetos na China" data-sr="Projekti u Kini" data-hu="Projektek Kínában">中国参建项目</h2>
    <p data-zh="PERI 在中国的标志性工程项目" data-en="PERI's landmark projects in China" data-es="Proyectos emblemáticos de PERI en China" data-de="PERIs Leuchtturmprojekte in China" data-pt="Projetos emblemáticos da PERI na China" data-sr="PERI-jevi značajni projekti u Kini" data-hu="PERI mérföldkő projektjei Kínában">PERI 在中国的标志性工程项目</p>
  </div>

  <div style="max-width:1200px;margin:0 auto;padding:0 32px">
    <div class="grid grid-3" style="padding-left:0;padding-right:0">
      {china_projects_html}
    </div>
  </div>

  <div style="text-align:center;padding:32px">
    <a href="https://cn.peri.com/projects/projects-overview/chinesecustomerprojects.html" target="_blank" class="btn btn-outline"
       data-zh="查看更多项目" data-en="View More Projects" data-es="Ver Más Proyectos" data-de="Mehr Projekte ansehen" data-pt="Ver Mais Projetos" data-sr="Pogledaj Više Projekata" data-hu="További Projektek">
       查看更多项目
    </a>
  </div>
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
def build_project_cards(product_projects=None):
    """Generate project cards HTML from product-specific projects or china_projects.json (random 3 projects)"""
    import random

    # Use product-specific projects if provided
    if product_projects and len(product_projects) > 0:
        cards = ''
        for proj in product_projects:
            cards += f'''
      <div class="card" onclick="window.open('{proj['link']}', '_blank')" style="cursor:pointer">
        <img src="{proj['image']}" alt="{proj['name']}" style="width:100%;height:200px;object-fit:cover;border-radius:8px 8px 0 0">
        <div class="card-body">
          <div class="card-title" style="font-size:14px;font-weight:600;margin-bottom:8px">{proj['name']}</div>
          <div class="card-desc" style="font-size:12px;color:#666;margin-bottom:8px">{proj['description']}</div>
          <div style="font-size:11px;color:#999">📍 {proj['location']}</div>
        </div>
      </div>'''
        return cards

    # Fallback to random projects from china_projects.json
    if not CHINA_PROJECTS or len(CHINA_PROJECTS) == 0:
        return '<p style="color:#999;text-align:center">暂无项目示例</p>'

    # Select 3 random projects
    selected = random.sample(CHINA_PROJECTS, min(3, len(CHINA_PROJECTS)))
    cards = ''
    for proj in selected:
        cards += f'''
      <div class="card" onclick="window.open('{proj['link']}', '_blank')" style="cursor:pointer">
        <img src="{proj['image']}" alt="{proj['name_zh']}" style="width:100%;height:200px;object-fit:cover;border-radius:8px 8px 0 0">
        <div class="card-body">
          <div class="card-title" style="font-size:14px;font-weight:600;margin-bottom:8px">{proj['name_zh']}</div>
          <div class="card-desc" style="font-size:12px;color:#666;margin-bottom:8px">{proj['description']}</div>
          <div style="font-size:11px;color:#999">📍 {proj['location']}</div>
        </div>
      </div>'''
    return cards

def build_product_page(cat_key, cat, p, subcat_key=None, subcat=None):
    slug, name_zh, desc_zh, img = p[0], p[1], p[2], p[3]
    cat_display = cat_key.replace('_', '/')
    cn_url = f'https://cn.peri.com/products/{slug}.html'

    # Load product-specific data from *_complete.json if exists
    product_projects = []
    pdf_url = None
    yt_id_from_json = None
    desc_from_json = None
    desc_en = desc_zh  # Default to Chinese if no translation
    desc_es = desc_zh
    desc_de = desc_zh
    desc_fr = desc_zh
    desc_pt = desc_zh
    desc_sr = desc_zh
    desc_hu = desc_zh
    desc_ar = desc_zh
    complete_json_path = os.path.join(BASE, f'{slug}_complete.json')
    if os.path.exists(complete_json_path):
        try:
            with open(complete_json_path, 'r', encoding='utf-8') as f:
                product_data = json.load(f)
                product_projects = product_data.get('projects', [])
                pdf_url = product_data.get('pdf_link')  # Get direct PDF URL
                yt_id_from_json = product_data.get('youtube_video_id')  # Get YouTube video ID
                # Extract all language descriptions from complete JSON if available
                if 'description' in product_data:
                    descriptions = product_data['description']
                    desc_from_json = descriptions.get('zh', '')
                    desc_en = descriptions.get('en', '')
                    desc_es = descriptions.get('es', '')
                    desc_de = descriptions.get('de', '')
                    desc_fr = descriptions.get('fr', '')
                    desc_pt = descriptions.get('pt', '')
                    desc_sr = descriptions.get('sr', '')
                    desc_hu = descriptions.get('hu', '')
                    desc_ar = descriptions.get('ar', '')
        except:
            pass

    # Use description from complete JSON if available, otherwise use products_v2.json description
    if desc_from_json:
        desc_zh = desc_from_json

    if pdf_url is not None:
        raw_pdf_url = pdf_url
        pdf_url = sanitize_pdf_url(pdf_url, slug)
        if raw_pdf_url and not pdf_url:
            print(f'  ⚠️ Ignoring non-verified PDF for {slug}: {raw_pdf_url}')

    # Fallback only to verified direct PDF links.
    # If complete JSON intentionally uses "", keep it hidden.
    if pdf_url is None:
        pdf_url = sanitize_pdf_url(TRUSTED_PDF_LINKS.get(slug, ''), slug)

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
    # Priority: 1. *_complete.json, 2. YT_IDS dictionary
    yt_id = yt_id_from_json if yt_id_from_json else YT_IDS.get(slug, '')
    yt_query = urllib.parse.quote(name_zh)
    yt_search_url = f'https://www.youtube.com/@perigroup/search?query={yt_query}'

    if yt_id:
        yt_embed = f'''  <div class="yt-embed">
    <iframe src="https://www.youtube-nocookie.com/embed/{yt_id}"
            title="{name_zh} — PERI Video"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen></iframe>
  </div>'''
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
    else:
        yt_section = ''

    # Badge: show main category + subcategory if applicable
    if subcat:
        badge_html = (f'<span class="badge" data-zh="{cat_display}" data-en="{cat["en"]}" '
                      f'data-es="{cat["es"]}" data-de="{cat["de"]}">{cat_display}</span>'
                      f'<span class="badge-subcat" data-zh="{subcat_key}" data-en="{subcat["en"]}" '
                      f'data-es="{subcat["es"]}" data-de="{subcat["de"]}">{subcat_key}</span>')
    else:
        badge_html = (f'<span class="badge" data-zh="{badge_zh}" data-en="{badge_en}" '
                      f'data-es="{badge_es}" data-de="{badge_de}">{badge_zh}</span>')

    # PDF button - only show if pdf_url exists
    if pdf_url:
        pdf_button = f'''<a href="{pdf_url}" target="_blank" class="btn btn-yellow"
         data-zh="📄 产品手册 PDF" data-en="📄 Product Brochure PDF" data-es="📄 Folleto PDF" data-de="📄 Produktbroschüre PDF"
         data-pt="📄 Folheto PDF" data-sr="📄 Brošura PDF" data-hu="📄 Termékismertető PDF">
         📄 产品手册 PDF
      </a>'''
    else:
        pdf_button = ''

    # Projects section - only show if there are projects
    if product_projects:
        projects_section = f'''<!-- Project Examples Section -->
<div style="background:#f5f5f5;padding:60px 32px;margin-top:40px">
  <div style="max-width:1100px;margin:0 auto">
    <h3 style="font-size:1.4rem;margin-bottom:24px;border-left:4px solid var(--red);padding-left:12px"
        data-zh="应用项目示例" data-en="Project Examples" data-es="Ejemplos de Proyectos" data-de="Projektbeispiele"
        data-pt="Exemplos de Projetos" data-sr="Primeri Projekata" data-hu="Projekt Példák">
        应用项目示例
    </h3>
    <p style="color:#666;margin-bottom:32px;font-size:14px"
       data-zh="查看派利产品在实际工程中的应用案例" data-en="See PERI products in real construction projects"
       data-es="Ver productos PERI en proyectos reales" data-de="Sehen Sie PERI-Produkte in echten Projekten"
       data-pt="Veja produtos PERI em projetos reais" data-sr="Pogledajte PERI proizvode u stvarnim projektima"
       data-hu="Tekintse meg a PERI termékeket valós projektekben">
       查看派利产品在实际工程中的应用案例
    </p>
    <div class="grid grid-3" style="gap:24px">
      {build_project_cards(product_projects)}
    </div>
    <div style="text-align:center;margin-top:32px">
      <a href="https://cn.peri.com/projects/projects-overview/chinesecustomerprojects.html" target="_blank" class="btn btn-outline"
         data-zh="查看更多项目案例 ↗" data-en="View More Projects ↗" data-es="Ver Más Proyectos ↗" data-de="Mehr Projekte ansehen ↗"
         data-pt="Ver Mais Projetos ↗" data-sr="Pogledaj Više Projekata ↗" data-hu="További Projektek ↗">
         查看更多项目案例 ↗
      </a>
    </div>
  </div>
</div>'''
    else:
        projects_section = ''

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
    <p style="color:#444;line-height:1.8;margin-bottom:20px;font-size:15px"
       data-zh="{desc_zh}" data-en="{desc_en}" data-es="{desc_es}" data-de="{desc_de}"
       data-pt="{desc_pt}" data-sr="{desc_sr}" data-hu="{desc_hu}" data-fr="{desc_fr}" data-ar="{desc_ar}">{desc_zh}</p>
    <div class="prod-cta">
      <a href="{cn_url}" target="_blank" class="btn btn-red"
         data-zh="↗ 前往中文官网查看" data-en="↗ View on PERI China" data-es="↗ Ver en PERI China" data-de="↗ Auf PERI China ansehen"
         data-pt="↗ Ver no PERI China" data-sr="↗ Pogledaj na PERI China" data-hu="↗ Megtekintés a PERI China oldalon">
         ↗ 前往中文官网查看
      </a>
      {pdf_button}
      <button class="btn btn-outline" onclick="document.getElementById('inquiry').scrollIntoView({{behavior:'smooth'}})"
              data-zh="发表留言" data-en="Post Comment" data-es="Publicar Comentario" data-de="Kommentar posten"
              data-pt="Publicar Comentário" data-sr="Objavi Komentar" data-hu="Hozzászólás Közzététele">
              发表留言
      </button>
    </div>
  </div>
</div>

{yt_section}

{projects_section}

<!-- Comment Board Section -->
<div style="background:#fff;padding:60px 32px">
  <div style="max-width:1100px;margin:0 auto">
    <div class="inquiry-box" id="inquiry">
      <h3 data-zh="产品留言板" data-en="Product Comments" data-es="Comentarios del Producto" data-de="Produktkommentare">产品留言板</h3>
      <p style="font-size:13px;color:#666;margin-bottom:16px"
         data-zh="分享您对此产品的看法、使用经验或提出问题"
         data-en="Share your thoughts, experience or questions about this product"
         data-es="Comparte tus opiniones, experiencia o preguntas sobre este producto"
         data-de="Teilen Sie Ihre Gedanken, Erfahrungen oder Fragen zu diesem Produkt">
         分享您对此产品的看法、使用经验或提出问题
      </p>
      <form action="https://api.web3forms.com/submit" method="POST" id="comment-form">
        <input type="hidden" name="access_key" value="bb073dfc-3b76-4263-897d-365fe7b6762a">
        <input type="hidden" name="subject" value="PERI产品留言: {name_zh}">
        <input type="hidden" name="from_name" value="PERI GCB 留言板">
        <input type="hidden" name="product" value="{name_zh}">
        <input type="hidden" name="product_url" value="{cn_url}">
        <input type="hidden" name="redirect" value="https://kiminanoliu-eng.github.io/peri-gcb/products/{slug}.html?submitted=true">
        <div class="form-row">
          <input type="text" name="name" placeholder="姓名 / Name *" required>
          <input type="text" name="company" placeholder="公司 / Company *" required>
        </div>
        <div class="form-row">
          <input type="text" name="project" placeholder="项目名称 / Project Name">
          <input type="email" name="email" placeholder="邮箱 / Email (可选)">
        </div>
        <textarea name="message" placeholder="留言内容 / Message *" rows="4" required></textarea>
        <button type="submit" class="btn btn-red"
                data-zh="发布留言" data-en="Post Comment" data-es="Publicar Comentario" data-de="Kommentar posten">发布留言</button>
        <p style="font-size:11px;color:#999;margin-top:8px"
           data-zh="提交后，您的留言将发送到我们的邮箱进行审核"
           data-en="Your comment will be sent to our email for review"
           data-es="Su comentario será enviado a nuestro correo para revisión"
           data-de="Ihr Kommentar wird zur Überprüfung an unsere E-Mail gesendet">
           提交后，您的留言将发送到我们的邮箱进行审核
        </p>
      </form>
    </div>
  </div>
</div>

{footer_html()}
{LANG_JS}
<script>
// Form submission success handling
document.getElementById('comment-form')?.addEventListener('submit', function(e) {{
  const btn = this.querySelector('button[type="submit"]');
  btn.textContent = '发送中...';
  btn.disabled = true;
}});
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
                        'image': p[3] if len(p) > 3 else '',
                        'cat_zh': f'{cat_display} › {sc_key}',
                        'cat_en': f'{cat["en"]} › {sc["en"]}',
                        'url': f'products/{p[0]}.html'
                    })
        else:
            for p in cat['products']:
                products_js.append({
                    'slug': p[0], 'name': p[1], 'desc': p[2],
                    'image': p[3] if len(p) > 3 else '',
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
        ${{p.image
          ? `<img class="card-img" src="${{p.image}}" alt="${{p.name}}" loading="lazy">`
          : '<div class="card-img-placeholder">🔧</div>'}}
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
