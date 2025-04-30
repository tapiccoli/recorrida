from bs4 import BeautifulSoup
from collections import defaultdict
import re
import os

ARQUIVO_HTML_ENTRADA = "static/pedigree.html"
ARQUIVO_HTML_SAIDA = "static/pedigree_colorido.html"

# Carregar o HTML de entrada
with open(ARQUIVO_HTML_ENTRADA, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Identificar nome do animal principal (opcional, pode ser melhorado)
nome_animal = None
celula_principal = soup.find("td", bgcolor=re.compile(r"(?i)^f4b183$"))
if celula_principal:
    strong = celula_principal.find("strong")
    if strong and strong.get_text(strip=True):
        nome_animal = strong.get_text(strip=True)

# Agrupar nomes para identificar duplicados
nome_para_tds = defaultdict(list)
for td in soup.find_all("td"):
    nome = None

    strong = td.find("strong")
    if strong and strong.string:
        nome = strong.string.strip()

    if not nome:
        a = td.find("a")
        if a and a.text:
            nome = a.text.strip()

    if not nome:
        texto_puro = td.get_text(strip=True)
        if texto_puro:
            nome = texto_puro

    if nome and nome.upper() != "NÃO INFORMADO" and nome != "-":
        nome_para_tds[nome].append(td)

# Paleta de cores variadas
cores_distintas = [
    "#FF0000", "#0000FF", "#008000", "#FFA500", "#800080",
    "#00CED1", "#DC143C", "#FFFF00", "#FF1493", "#20B2AA",
    "#A52A2A", "#4B0082", "#1E90FF", "#8B0000", "#008080",
    "#B8860B", "#00FF00", "#FF4500", "#2F4F4F", "#00FA9A",
    "#FF69B4", "#00BFFF", "#7CFC00", "#FF8C00", "#8A2BE2",
    "#00FF7F", "#FF6347", "#4682B4", "#D2691E", "#32CD32",
    "#DA70D6", "#40E0D0", "#CD5C5C", "#9932CC", "#F08080",
    "#ADFF2F", "#6495ED", "#FF00FF", "#66CDAA", "#BA55D3",
    "#FFD700", "#7B68EE", "#3CB371", "#FFB6C1", "#6A5ACD"
]

# Aplicar coloração
grupo_idx = 0
cores_usadas = {}

for nome, tds in sorted(nome_para_tds.items()):
    if len(tds) < 2:
        continue

    if nome not in cores_usadas:
        cor = cores_distintas[grupo_idx % len(cores_distintas)]
        cores_usadas[nome] = cor
        grupo_idx += 1
    else:
        cor = cores_usadas[nome]

    for td in tds:
        estilo_atual = td.get("style", "")
        td["style"] = f"{estilo_atual}; border-left: 8px solid {cor};"

# Salvar HTML final na pasta static
with open(ARQUIVO_HTML_SAIDA, "w", encoding="utf-8") as f:
    f.write(str(soup))

print(f"✅ HTML colorido salvo como: {ARQUIVO_HTML_SAIDA}")
