import cloudscraper
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import time

URL = "https://www.leparisien.fr/paris-75/"

print("Descarregant la pagina...")
scraper = cloudscraper.create_scraper()
resposta = scraper.get(URL)

if resposta.status_code != 200:
    print(f"Error: codi {resposta.status_code}")
    exit()

print("Pagina descarregada correctament")
sopa = BeautifulSoup(resposta.text, "html.parser")

fg = FeedGenerator()
fg.title("Le Parisien - Paris")
fg.link(href=URL)
fg.description("Articles de Le Parisien Paris")

articles = sopa.find_all("article")

if not articles:
    print("No s'han trobat articles.")
else:
    print(f"Trobats {len(articles)} articles")

for article in articles:
    titol_tag = article.find("h2") or article.find("h3") or article.find("h1")
    link_tag = article.find("a", href=True)

    if titol_tag and link_tag:
        titol = titol_tag.get_text(strip=True)
        link = link_tag["href"]

        if link.startswith("/"):
            link = "https://www.leparisien.fr" + link

        subtitol = ""
        imatge = ""
        try:
            resposta_article = scraper.get(link)
            sopa_article = BeautifulSoup(resposta_article.text, "html.parser")

            subtitol_tag = sopa_article.find("p", class_="col subheadline lp-mb-04")
            if subtitol_tag:
                subtitol = subtitol_tag.get_text(strip=True)

            og_image = sopa_article.find("meta", property="og:image")
            if og_image:
                imatge = og_image.get("content", "")

            time.sleep(1)
        except Exception:
            pass

        if imatge:
            descripcio = f'<img src="{imatge}"/><br/>{subtitol}'
        elif subtitol:
            descripcio = subtitol
        else:
            descripcio = titol

        fe = fg.add_entry()
        fe.title(titol)
        fe.link(href=link)
        fe.content(descripcio, type="html")
        print(f"  -> {titol[:60]}...")

fg.rss_file("parisien.rss")
print("Feed guardat com a parisien.rss")