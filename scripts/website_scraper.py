"""
Website Scraper - Extrai TODO conteudo de um site:
HTML, CSS, animacoes, textos, paleta de cores, fontes, assets
Bypass Cloudflare via: cloudscraper -> Playwright browser
"""
import re, json
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser

class SiteScraper:
    def __init__(self, url):
        self.url = url
        self.domain = urlparse(url).netloc
        self.html = ""
        self.stylesheets = []
        self.inline_styles = []
        self.animations = {}
        self.texts = []
        self.images = []
        self.colors = set()
        self.fonts = set()
        self.sections = []
        self.title = ""
        self.blocked = False
        self.method_used = ""

    def _is_blocked(self, html):
        if len(html) < 500:
            return True
        lower = html.lower()
        hard_block = ["please complete the security check", "checking your browser",
                      "you have been blocked", "attention required", "just a moment"]
        score = sum(1 for k in hard_block if k in lower)
        return score >= 2 and len(html) < 50000

    def fetch(self):
        self.blocked = False

        # Try 1: cloudscraper (bypass TLS fingerprint)
        if self._try_fetch_http():
            if not self._is_blocked(self.html):
                self.method_used = "cloudscraper"
                return True
            print(f"[SCRAPER] cloudscraper bloqueado ({len(self.html)} bytes).")
        else:
            print(f"[SCRAPER] cloudscraper falhou.")

        # Try 2: Playwright (browser real)
        print(f"[SCRAPER] Tentando Playwright (Chromium)...")
        if self._fetch_with_playwright():
            if not self._is_blocked(self.html):
                self.method_used = "playwright"
                return True
            print(f"[SCRAPER] Playwright tambem bloqueado ({len(self.html)} bytes).")

        # All methods failed
        self.blocked = True
        print(f"\n[SCRAPER] ERRO: Site {self.url} esta bloqueando todas as tentativas.")
        print(f"[SCRAPER] Possiveis causas: Cloudflare WAF agressivo, IP bloqueado, ou site fora do ar.")
        print(f"[SCRAPER] Solucao: use o modo --from-brain com um briefing manual do cliente.\n")
        return True

    def _try_fetch_http(self):
        try:
            import cloudscraper
            scraper = cloudscraper.create_scraper(
                browser={"browser": "chrome", "platform": "windows", "mobile": False, "desktop": True},
                delay=5
            )
            r = scraper.get(self.url, timeout=60)
        except ImportError:
            import requests
            r = requests.get(self.url, timeout=30, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            })
        try:
            r.encoding = r.apparent_encoding or "utf-8"
            self.html = r.text
            self.title = self._extract_title(self.html)
            return True
        except Exception as e:
            print(f"[SCRAPER] HTTP error: {e}")
            return False

    def _fetch_with_playwright(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("[SCRAPER] Playwright nao instalado. pip install playwright && playwright install chromium")
            return False

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox", "--disable-dev-shm-usage",
                ])
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800},
                    locale="pt-BR",
                )
                # Stealth: remove webdriver痕迹
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en']});
                """)
                page = context.new_page()
                page.goto(self.url, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(5000)
                self.html = page.content()
                self.title = page.title()
                browser.close()
                print(f"[SCRAPER] Playwright OK: {len(self.html)} bytes")
                return True
        except Exception as e:
            print(f"[SCRAPER] Playwright error: {e}")
            return False

    def _extract_title(self, html):
        m = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else ""

    def extract_css(self):
        for m in re.finditer(r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\'](.*?)["\']', self.html, re.IGNORECASE):
            css_url = urljoin(self.url, m.group(1))
            self._fetch_stylesheet(css_url)
        for m in re.finditer(r'<style[^>]*>(.*?)</style>', self.html, re.IGNORECASE | re.DOTALL):
            css = m.group(1).strip()
            if css:
                self.inline_styles.append(css)
                self._parse_css(css)

    def _fetch_stylesheet(self, url):
        try:
            import cloudscraper
            s = cloudscraper.create_scraper(delay=3)
            r = s.get(url, timeout=30)
        except ImportError:
            import requests
            r = requests.get(url, timeout=15)
        try:
            r.encoding = "utf-8"
            css = r.text
            self.stylesheets.append({"url": url, "content": css})
            self._parse_css(css)
        except:
            pass

    def _parse_css(self, css):
        for m in re.finditer(r'@keyframes\s+([^{\s]+)\s*\{([^}]+)\}', css, re.IGNORECASE | re.DOTALL):
            name = m.group(1).strip()
            body = m.group(2).strip()
            if name not in self.animations:
                self.animations[name] = []
            self.animations[name].append(body)
        for c in re.findall(r'#[0-9a-fA-F]{3,8}', css):
            self.colors.add(c.lower())
        for c in re.findall(r'rgba?\([^)]+\)', css, re.IGNORECASE):
            self.colors.add(c)
        for c in re.findall(r'hsla?\([^)]+\)', css, re.IGNORECASE):
            self.colors.add(c)
        for f in re.findall(r'font-family:\s*[\'"]([^\'"]+)[\'"]', css, re.IGNORECASE):
            self.fonts.add(f)
        for m in re.finditer(r'@import\s+url\([\'"]?(https?://[^)>\'"]+)[\'"]?\)', css, re.IGNORECASE):
            font_url = m.group(1)
            if 'fonts' in font_url or 'font' in font_url:
                self.fonts.add(font_url)
        for m in re.finditer(r'--([^:\s]+)\s*:\s*([^;]+);', css):
            var_val = m.group(2).strip()
            if re.match(r'#[0-9a-fA-F]', var_val) or 'rgb' in var_val or 'hsl' in var_val:
                self.colors.add(var_val)

    def extract_texts(self):
        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.texts = []
                self.skip = False
                self.skip_tags = {'script', 'style', 'noscript', 'svg', 'path'}
                self.tag_stack = []
            def handle_starttag(self, tag, attrs):
                tag = tag.lower()
                self.tag_stack.append(tag)
                if tag in self.skip_tags:
                    self.skip = True
            def handle_endtag(self, tag):
                tag = tag.lower()
                if self.tag_stack and self.tag_stack[-1] == tag:
                    self.tag_stack.pop()
                if tag in self.skip_tags:
                    self.skip = False
            def handle_data(self, data):
                if not self.skip:
                    text = data.strip()
                    if text and len(text) > 2:
                        self.texts.append(text)
        parser = TextExtractor()
        parser.feed(self.html)
        self.texts = list(set(t.strip() for t in parser.texts if t.strip()))

    def extract_sections(self):
        section_re = re.compile(
            r'<(section|header|footer|article|nav|main|div)\b[^>]*class=["\'][^"\']*?\b(hero|banner|services?|planos?|precos?|pricing|about|sobre|contato?|contact|footer|header|features?|depoimentos?|testimonials?|faq|cta|banner|portfolio|equipe?|team|diferenciais?|benefits?|statistics?|numeros?|steps?|como-funciona|process)\b[^>]*>',
            re.IGNORECASE | re.DOTALL)
        self.sections = []
        for m in section_re.finditer(self.html):
            tag = m.group(1)
            cls_match = re.search(r'class=["\']([^"\']*?)["\']', m.group(0))
            cls = cls_match.group(1) if cls_match else ""
            self.sections.append({"tag": tag, "class": cls, "html": m.group(0)[:500]})

    def extract_struct(self):
        struct = {
            "title": self.title, "url": self.url, "domain": self.domain,
            "blocked": self.blocked, "method": self.method_used,
            "text_count": len(self.texts), "section_count": len(self.sections),
            "animation_count": len(self.animations), "color_count": len(self.colors),
            "font_count": len(self.fonts), "css_files": len(self.stylesheets),
            "html_bytes": len(self.html),
        }
        md = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', self.html, re.IGNORECASE)
        if md:
            struct["meta_description"] = md.group(1)
        return struct

    def to_spec(self):
        texts = self.texts[:200] if not self.blocked else []
        return {
            "url": self.url, "domain": self.domain,
            "title": self.title,
            "project_name": f"WebsiteApp {self.title}" if self.title else "WebsiteApp",
            "goal": f"WebsiteApp baseado em {self.url}",
            "client": self.title or self.domain,
            "blocked": self.blocked,
            "extracted": {
                "texts": texts,
                "colors": sorted(self.colors)[:50],
                "fonts": sorted(self.fonts)[:20],
                "animations": list(self.animations.keys()),
                "animations_raw": self.animations,
                "sections": self.sections[:30],
            },
            "struct": self.extract_struct(),
            "nav_items": [
                {"icon": "Home", "label": "Inicio"},
                {"icon": "Briefcase", "label": "Servicos"},
                {"icon": "CreditCard", "label": "Planos"},
                {"icon": "Headphones", "label": "Suporte"},
                {"icon": "User", "label": "Conta"},
            ],
        }

    def scrape_all(self):
        if not self.fetch():
            return None
        print(f"[SCRAPER] Baixado: {len(self.html)} bytes via {self.method_used or 'N/A'}")
        self.extract_css()
        self.extract_texts()
        self.extract_sections()
        print(f"[SCRAPER] Textos: {len(self.texts)} | Cores: {len(self.colors)} | Animacoes: {len(self.animations)} | Secoes: {len(self.sections)}")
        return self.to_spec()


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://acessosvipclientes.com.br/"
    s = SiteScraper(url)
    spec = s.scrape_all()
    if spec:
        print(json.dumps(spec, indent=2, ensure_ascii=False)[:3000])
        print("...")
