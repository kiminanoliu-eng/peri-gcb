#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为单个产品生成完整的产品页面（测试版本）
"""

import json
import os
import sys
import random

BASE = os.path.dirname(os.path.abspath(__file__))

# 加载产品数据 - 支持命令行参数
product_file = sys.argv[1] if len(sys.argv) > 1 else 'handset_alpha_complete.json'
with open(os.path.join(BASE, product_file), encoding='utf-8') as f:
    product = json.load(f)

# 使用产品自己的项目示例
selected_projects = product.get('projects', [])

# 生成HTML
html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{product['name_zh']} - PERI GCB 派利产品中文介绍HUB</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
  <nav>
    <div class="container">
      <a href="../index.html" class="logo">
        <span data-zh="GCB 派利产品中文介绍HUB" data-en="GCB PERI Product Hub" data-es="GCB Centro de Productos PERI"
              data-de="GCB PERI Produktzentrum" data-pt="GCB Centro de Produtos PERI" data-sr="GCB PERI Centar Proizvoda"
              data-hu="GCB PERI Termékközpont">GCB 派利产品中文介绍HUB</span>
      </a>
      <div class="nav-right">
        <select id="lang-switcher" onchange="switchLanguage(this.value)">
          <option value="zh">中文</option>
          <option value="en">English</option>
          <option value="es">Español</option>
          <option value="de">Deutsch</option>
          <option value="pt">Português</option>
          <option value="sr">Српски</option>
          <option value="hu">Magyar</option>
        </select>
        <a href="../search.html" class="btn btn-outline">
          <span data-zh="🔍 搜索" data-en="🔍 Search" data-es="🔍 Buscar" data-de="🔍 Suchen"
                data-pt="🔍 Pesquisar" data-sr="🔍 Претрага" data-hu="🔍 Keresés">🔍 搜索</span>
        </a>
      </div>
    </div>
  </nav>

  <div class="container" style="margin-top:80px">
    <div class="breadcrumb">
      <a href="../index.html" data-zh="首页" data-en="Home" data-es="Inicio" data-de="Startseite"
         data-pt="Início" data-sr="Почетна" data-hu="Kezdőlap">首页</a> ›
      <a href="../categories/building-formwork.html" data-zh="{product['category']}" data-en="Building Formwork Systems"
         data-es="Sistemas de Encofrado" data-de="Schalungssysteme" data-pt="Sistemas de Cofragem"
         data-sr="Sistemi Oplate" data-hu="Zsaluzási Rendszerek">{product['category']}</a> ›
      <a href="../categories/wall-formwork.html" data-zh="{product['subcategory']}" data-en="Wall Formwork"
         data-es="Encofrado de Muros" data-de="Wandschalung" data-pt="Cofragem de Paredes"
         data-sr="Oplata Zidova" data-hu="Falzsaluzat">{product['subcategory']}</a> ›
      <span>{product['name_zh']}</span>
    </div>

    <div class="product-hero">
      <img src="{product['image']}" alt="{product['name_zh']}" class="product-img">
      <div class="product-info">
        <h1>{product['name_zh']}</h1>
        <p class="product-desc"
           data-zh="{product['description']['zh']}"
           data-en="{product['description']['en']}"
           data-es="{product['description']['es']}"
           data-de="{product['description']['de']}"
           data-pt="{product['description']['pt']}"
           data-sr="{product['description']['sr']}"
           data-hu="{product['description']['hu']}">{product['description']['zh']}</p>

        <div class="product-actions">
          <a href="{product['cn_url']}" target="_blank" class="btn btn-red"
             data-zh="↗ 前往中文官网查看" data-en="↗ View on PERI China" data-es="↗ Ver en PERI China"
             data-de="↗ Auf PERI China ansehen" data-pt="↗ Ver no PERI China" data-sr="↗ Pogledaj na PERI China"
             data-hu="↗ Megtekintés a PERI China oldalon">↗ 前往中文官网查看</a>

          <a href="{product['pdf_link']}" target="_blank" class="btn btn-yellow"
             data-zh="📄 产品手册 PDF" data-en="📄 Product Brochure PDF" data-es="📄 Folleto PDF"
             data-de="📄 Produktbroschüre PDF" data-pt="📄 Folheto PDF" data-sr="📄 Brošura PDF"
             data-hu="📄 Termékismertető PDF">📄 产品手册 PDF</a>

          <button class="btn btn-outline" onclick="document.getElementById('inquiry').scrollIntoView({{behavior:'smooth'}})"
                  data-zh="发表留言" data-en="Post Comment" data-es="Publicar Comentario" data-de="Kommentar posten"
                  data-pt="Publicar Comentário" data-sr="Objavi Komentar" data-hu="Hozzászólás Közzététele">发表留言</button>
        </div>
      </div>
    </div>

    <h3 style="margin-top:64px;margin-bottom:16px;font-size:24px"
        data-zh="应用项目示例" data-en="Reference Projects" data-es="Proyectos de Referencia" data-de="Referenzprojekte"
        data-pt="Projetos de Referência" data-sr="Referentni Projekti" data-hu="Referencia Projektek">应用项目示例</h3>
    <p style="color:#666;margin-bottom:32px;font-size:14px"
       data-zh="查看派利产品在实际工程中的应用案例" data-en="See PERI products in real construction projects"
       data-es="Ver productos PERI en proyectos reales" data-de="Sehen Sie PERI-Produkte in echten Projekten"
       data-pt="Veja produtos PERI em projetos reais" data-sr="Pogledajte PERI proizvode u stvarnim projektima"
       data-hu="Tekintse meg a PERI termékeket valós projektekben">查看派利产品在实际工程中的应用案例</p>

    <div class="grid grid-3" style="gap:24px">
'''

# 添加项目卡片
for proj in selected_projects:
    html += f'''
      <div class="card" onclick="window.open('{proj['link']}', '_blank')" style="cursor:pointer">
        <img src="{proj['image']}" alt="{proj['name']}" style="width:100%;height:200px;object-fit:cover;border-radius:8px 8px 0 0">
        <div class="card-body">
          <div class="card-title" style="font-size:14px;font-weight:600;margin-bottom:8px">{proj['name']}</div>
          <div class="card-desc" style="font-size:12px;color:#666;margin-bottom:8px">{proj['description']}</div>
          <div style="font-size:11px;color:#999">📍 {proj['location']}</div>
        </div>
      </div>'''

html += f'''
    </div>
'''

# 只有当youtube_video_id存在且不为空时才显示视频部分
if product.get('youtube_video_id'):
    html += f'''
    <div style="margin-top:64px;margin-bottom:64px">
      <h3 style="margin-bottom:16px;font-size:24px;display:flex;align-items:center;gap:8px"
          data-zh="📺 产品视频介绍" data-en="📺 Product Video" data-es="📺 Video del Producto" data-de="📺 Produktvideo"
          data-pt="📺 Vídeo do Produto" data-sr="📺 Видео Производа" data-hu="📺 Termék Videó">📺 产品视频介绍</h3>
      <div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:10px;background:#000;margin-bottom:16px;box-shadow:0 4px 16px rgba(0,0,0,.15)">
        <iframe style="position:absolute;top:0;left:0;width:100%;height:100%;border:0"
                src="https://www.youtube.com/embed/{product['youtube_video_id']}"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen></iframe>
      </div>
    </div>
'''

html += '''
    <div id="inquiry" style="margin-top:80px;margin-bottom:80px">
      <h3 style="margin-bottom:24px;font-size:24px"
          data-zh="发表留言" data-en="Post a Comment" data-es="Publicar Comentario" data-de="Kommentar posten"
          data-pt="Publicar Comentário" data-sr="Objavi Komentar" data-hu="Hozzászólás Közzététele">发表留言</h3>

      <form action="https://api.web3forms.com/submit" method="POST" id="comment-form">
        <input type="hidden" name="access_key" value="bb073dfc-3b76-4263-897d-365fe7b6762a">
        <input type="hidden" name="subject" value="HANDSET Alpha 产品留言">

        <div class="form-group">
          <label data-zh="姓名" data-en="Name" data-es="Nombre" data-de="Name" data-pt="Nome" data-sr="Име" data-hu="Név">姓名</label>
          <input type="text" name="name" required>
        </div>

        <div class="form-group">
          <label data-zh="公司" data-en="Company" data-es="Empresa" data-de="Firma" data-pt="Empresa" data-sr="Компанија" data-hu="Cég">公司</label>
          <input type="text" name="company">
        </div>

        <div class="form-group">
          <label data-zh="项目" data-en="Project" data-es="Proyecto" data-de="Projekt" data-pt="Projeto" data-sr="Пројекат" data-hu="Projekt">项目</label>
          <input type="text" name="project">
        </div>

        <div class="form-group">
          <label data-zh="邮箱" data-en="Email" data-es="Correo" data-de="E-Mail" data-pt="E-mail" data-sr="Е-пошта" data-hu="E-mail">邮箱</label>
          <input type="email" name="email" required>
        </div>

        <div class="form-group">
          <label data-zh="留言内容" data-en="Message" data-es="Mensaje" data-de="Nachricht" data-pt="Mensagem" data-sr="Порука" data-hu="Üzenet">留言内容</label>
          <textarea name="message" rows="5" required></textarea>
        </div>

        <button type="submit" class="btn btn-red"
                data-zh="提交留言" data-en="Submit Comment" data-es="Enviar Comentario" data-de="Kommentar senden"
                data-pt="Enviar Comentário" data-sr="Пошаљи Коментар" data-hu="Hozzászólás Küldése">提交留言</button>
      </form>
    </div>
  </div>

  <footer>
    <div class="container">
      <p data-zh="© 2024 PERI GCB 派利产品中文介绍HUB - 非官方产品展示平台"
         data-en="© 2024 PERI GCB Product Hub - Unofficial Product Showcase"
         data-es="© 2024 PERI GCB Centro de Productos - Plataforma No Oficial"
         data-de="© 2024 PERI GCB Produktzentrum - Inoffizielle Produktplattform"
         data-pt="© 2024 PERI GCB Centro de Produtos - Plataforma Não Oficial"
         data-sr="© 2024 PERI GCB Centar Proizvoda - Nezvanična Platforma"
         data-hu="© 2024 PERI GCB Termékközpont - Nem Hivatalos Platform">© 2024 PERI GCB 派利产品中文介绍HUB - 非官方产品展示平台</p>
    </div>
  </footer>

  <script src="../script.js"></script>
</body>
</html>
'''

# 保存文件
output_dir = os.path.join(BASE, 'mnt/创建产品网站/products')
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, f"{product['slug']}-test.html")

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ 测试产品页面已生成: {output_file}")
print(f"\n包含的功能:")
print(f"  ✓ 产品名称: {product['name_zh']}")
print(f"  ✓ 正确的产品图片: {product['image']}")
print(f"  ✓ 正确的类别归属: {product['category']} > {product['subcategory']}")
print(f"  ✓ 7种语言的产品描述")
print(f"  ✓ PDF下载链接: {product.get('pdf_link', '无')}")
print(f"  ✓ YouTube视频: {product.get('youtube_video_id', '无')}")
print(f"  ✓ {len(selected_projects)}个项目示例")
print(f"  ✓ Web3Forms留言板")
print(f"\n请在浏览器中打开查看: file://{output_file}")
