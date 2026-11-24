# Собирает публичную версию сайта для GitHub Pages из site/index.html:
# SEO-заголовок и описание, Schema.org (услуга + частые вопросы), без заглушек прототипа.
import sys, re, json, html as H

src, dst_dir = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
URL = "https://88mayak88.github.io/mayak-site/"

# --- убрать то, что не должно попасть в поиск ---
s = re.sub(r'<span class="proto">[^<]*</span>', '', s)                       # пометки «Прототип»
s = re.sub(r'  <section class="g"><div class="in sec">\s*<div class="sec-h"><span class="label">// Отзывы</span>[\s\S]*?</div></section>\n\n?', '', s)  # отзывы-заглушки
s = s.replace('<span>ИП [ФИО] · ИНН [номер]</span>', '')

# --- частые вопросы -> FAQPage ---
faq = []
for q, a in re.findall(r'<details[^>]*><summary>(.*?)</summary><div class="a">(.*?)</div></details>', s):
    faq.append({"@type": "Question", "name": H.unescape(re.sub('<[^>]+>', '', q)),
                "acceptedAnswer": {"@type": "Answer", "text": H.unescape(re.sub('<[^>]+>', '', a)).strip()}})
assert len(faq) >= 5, len(faq)

service = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "name": "Евгений Маяк — свадебный ведущий",
    "description": "Ведущий на свадьбу в Омске. Ведущий и диджей одним пакетом, «Шоу под ключ» со светом, тяжёлым дымом, фонтанами и шоу-балетом.",
    "url": URL,
    "image": URL + "img/og.jpg",
    "priceRange": "25 000–150 000 ₽",
    "address": {"@type": "PostalAddress", "addressLocality": "Омск", "addressCountry": "RU"},
    "areaServed": {"@type": "City", "name": "Омск"},
    "founder": {"@type": "Person", "name": "Евгений Маяк", "jobTitle": "Свадебный ведущий"},
    "sameAs": ["https://instagram.com/evgeny_mayak"],
    "makesOffer": [
        {"@type": "Offer", "name": "Камерная свадьба: ведущий + диджей, 3 часа", "price": "25000", "priceCurrency": "RUB"},
        {"@type": "Offer", "name": "Стандарт: ведущий + диджей, 5 часов", "price": "55000", "priceCurrency": "RUB"},
        {"@type": "Offer", "name": "Шоу под ключ", "price": "150000", "priceCurrency": "RUB"},
    ],
}
faqpage = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq}
ld = lambda o: '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + '</script>'

TITLE = "Ведущий на свадьбу в Омске — Евгений Маяк, свадебный ведущий и диджей"
DESC = ("Свадебный ведущий в Омске Евгений Маяк. Ведущий и диджей одним пакетом от 25 000 ₽, "
        "«Шоу под ключ» со светом, дымом и шоу-балетом. Без пошлых конкурсов. Проверьте, свободна ли ваша дата.")
head = f'''<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{URL}">
<meta name="geo.region" content="RU-OMS">
<meta name="geo.placename" content="Омск">
<meta property="og:type" content="website">
<meta property="og:locale" content="ru_RU">
<meta property="og:site_name" content="Евгений Маяк">
<meta property="og:title" content="Евгений Маяк — свадебный ведущий, Омск">
<meta property="og:description" content="Интеллигентный ведущий. Держу вечер под контролем, чтобы вы в свой день отдыхали.">
<meta property="og:image" content="{URL}img/og.jpg">
<meta property="og:url" content="{URL}">
<meta name="theme-color" content="#060607">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%23a8281e'/%3E%3Ctext x='16' y='23' font-family='Arial Narrow,Arial' font-weight='700' font-size='18' text-anchor='middle' fill='white'%3EМ%3C/text%3E%3C/svg%3E">
<link rel="preload" as="image" href="img/hero.webp">
{ld(service)}
{ld(faqpage)}'''
assert '<title>Евгений Маяк</title>' in s
s = s.replace('<title>Евгений Маяк</title>', head, 1)
s = s.replace('*{box-sizing:border-box}', '*{box-sizing:border-box}\nbody{margin:0}', 1)
s = '<!doctype html>\n<html lang="ru">\n' + s + '\n</html>\n'
# метка версии к каждой картинке: при замене файла браузер сразу берёт новый, а не копию из кэша
import hashlib, os
def bust(m):
    path = m.group(1)
    f = os.path.join(dst_dir, path)
    if not os.path.exists(f): return m.group(0)
    h = hashlib.md5(open(f, "rb").read()).hexdigest()[:8]
    return m.group(0).replace(path, path + "?v=" + h)
s = re.sub(r'(?:src|href|content)="(?:' + re.escape(URL) + r')?(img/[A-Za-z0-9_.-]+)"', bust, s)
open(dst_dir + "/index.html", "w", encoding="utf-8").write(s)

open(dst_dir + "/sitemap.xml", "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f'  <url><loc>{URL}</loc><changefreq>monthly</changefreq><priority>1.0</priority></url>\n</urlset>\n')
open(dst_dir + "/robots.txt", "w", encoding="utf-8").write(f"User-agent: *\nAllow: /\n\nSitemap: {URL}sitemap.xml\n")
print("built:", len(faq), "FAQ,", "noindex" in s and "NOINDEX!" or "indexable")
