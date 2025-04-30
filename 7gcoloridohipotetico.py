from bs4 import BeautifulSoup
from collections import defaultdict
import re
import os
import webbrowser

ARQUIVO_HTML = "7ghipoteticocolorido.html"
PASTA_SAIDA = "pedigreeshipoteticos"

# Criar a pasta se não existir
os.makedirs(PASTA_SAIDA, exist_ok=True)

# Carregar o HTML
with open(ARQUIVO_HTML, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Inicializar nomes
nome_macho = None
nome_femea = None

# Procurar todas as células <td>
for td in soup.find_all("td"):
    style = td.get("style", "")
    if "#cccccc" in style:  # Fundo cinza (pai)
        span = td.find("span")
        if span and span.find("strong"):
            nome_macho = span.find("strong").get_text(strip=True)
    if "#ffff99" in style:  # Fundo amarelo (mãe)
        span = td.find("span")
        if span and span.find("strong"):
            nome_femea = span.find("strong").get_text(strip=True)

# Preparar nome seguro
if nome_macho and nome_femea:
    nome_macho_limpo = re.sub(r"[^\w]", "_", nome_macho)
    nome_femea_limpo = re.sub(r"[^\w]", "_", nome_femea)
    nome_arquivo = f"{nome_macho_limpo}x{nome_femea_limpo}.html"
else:
    nome_arquivo = "pedigree_fallback_colorido.html"

caminho_completo = os.path.join(PASTA_SAIDA, nome_arquivo)

# Colorir duplicados
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

# Paleta de cores
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

# Salvar novo HTML
with open(caminho_completo, "w", encoding="utf-8") as f:
    f.write(str(soup))

print(f"✅ HTML colorido salvo como: {caminho_completo}")

# Abrir
webbrowser.open(caminho_completo)
