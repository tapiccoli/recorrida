from bs4 import BeautifulSoup
from collections import defaultdict
import re
import unicodedata
import webbrowser
import os

ARQUIVO_HTML_ENTRADA = "static/pedigree.html"

# Função de normalização
def normalizar_nome(nome):
    nome = nome.upper()
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    nome = re.sub(r"-\s*[A-Z\*]{0,3}\d{3,}", "", nome)  # remove - B123456, - *000333, - UD000059
    nome = re.sub(r"/\s*[^/]*$", "", nome)                # remove / pelagem
    return nome.strip()

# Carregar o HTML de entrada
with open(ARQUIVO_HTML_ENTRADA, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Agrupar nomes normalizados para identificar duplicados
nome_para_tds = defaultdict(list)
for td in soup.find_all("td"):
    nome = td.get_text(strip=True)
    chave = normalizar_nome(nome)
    if chave and chave.upper() != "NAO INFORMADO" and chave != "-":
        nome_para_tds[chave].append(td)

# Paleta de cores variadas
cores_distintas = [
    "#FF0000", "#0000FF", "#008000", "#FFA500", "#800080",
    "#00CED1", "#DC143C", "#FFFF00", "#FF1493", "#20B2AA",
    "#A52A2A", "#4B0082", "#1E90FF", "#8B0000", "#008080",
    "#B8860B", "#00FF00", "#FF4500", "#2F4F4F", "#00FA9A"
]

# Aplicar coloração
grupo_idx = 0
cores_usadas = {}

for chave, tds in sorted(nome_para_tds.items()):
    if len(tds) < 2:
        continue
    if chave not in cores_usadas:
        cor = cores_distintas[grupo_idx % len(cores_distintas)]
        cores_usadas[chave] = cor
        grupo_idx += 1
    else:
        cor = cores_usadas[chave]

    for td in tds:
        estilo_atual = td.get("style", "")
        td["style"] = f"{estilo_atual}; border-left: 8px solid {cor};"

# Detectar os nomes da célula azul (pai) e amarela (mãe) para nome do arquivo
azul = soup.find("td", style=lambda v: v and "#cccccc" in v.lower())
amarelo = soup.find("td", style=lambda v: v and "#ffff99" in v.lower())
nome_azul = azul.get_text(strip=True).split("-")[0].strip().replace("\n", " ") if azul else "azul"
nome_amarelo = amarelo.get_text(strip=True).split("-")[0].strip().replace("\n", " ") if amarelo else "amarelo"
nome_base = f"{nome_azul}_x_{nome_amarelo}"
nome_arquivo = f"static/{nome_base}.html"

# Salvar HTML final
with open(nome_arquivo, "w", encoding="utf-8") as f:
    f.write(str(soup))

print(f"✅ HTML colorido salvo como: {nome_arquivo}")

# Abrir automaticamente no navegador (funciona localmente)
webbrowser.open(f"file://{os.path.abspath(nome_arquivo)}")
