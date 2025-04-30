from bs4 import BeautifulSoup
from collections import defaultdict
import re
import unicodedata
import webbrowser
import os

ARQUIVO_HTML_ENTRADA = "static/pedigree.html"

# Função de normalização robusta para nomes
def normalizar_nome(nome):
    nome = nome.upper()
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    nome = re.sub(r"-\s*[A-Z\*]{0,3}\d{3,}", "", nome)  # remove registros
    nome = re.sub(r"/\s*[^/]*$", "", nome)  # remove pelagem
    nome = re.sub(r"\s+", " ", nome)  # remove espaços extras
    nome = nome.replace("\xa0", " ").strip()
    return nome

# Carregar o HTML de entrada
try:
    with open(ARQUIVO_HTML_ENTRADA, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
except FileNotFoundError:
    print(f"Erro: Arquivo HTML não encontrado em: {ARQUIVO_HTML_ENTRADA}")
    exit()
except Exception as e:
    print(f"Erro ao abrir ou analisar o arquivo HTML: {e}")
    exit()

# Agrupar nomes normalizados para identificar duplicados
nome_para_tds = defaultdict(list)

for td in soup.find_all("td"):
    texto_completo = td.get_text(separator=" ", strip=True)
    nome_base = texto_completo.split("-")[0].strip()
    chave = normalizar_nome(nome_base)
    if chave and chave != "NAO INFORMADO" and chave != "-":
        nome_para_tds[chave].append(td)

# Paleta de cores variadas
cores_distintas = [
    "#FF0000", "#0000FF", "#008000", "#FFA500", "#800080",
    "#00CED1", "#DC143C", "#FFFF00", "#FF1493", "#20B2AA",
    "#A52A2A", "#4B0082", "#1E90FF", "#8B0000", "#008080",
    "#B8860B", "#00FF00", "#FF4500", "#2F4F4F", "#00FA9A"
]

# Aplicar coloração mesmo que o nome esteja em lados diferentes da árvore
grupo_idx = 0
cores_usadas = {}

for chave, tds in sorted(nome_para_tds.items()):
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
try:
    nome1_element = soup.find('td', class_='xl9532535')
    nome2_element = soup.find('td', class_='xl10432535')
    if nome1_element and nome2_element:
        nome1 = normalizar_nome(nome1_element.get_text(separator=" ", strip=True))
        nome2 = normalizar_nome(nome2_element.get_text(separator=" ", strip=True))
        nome_arquivo = f"{nome1}_e_{nome2}.html"
    else:
        print("Aviso: Não foi possível encontrar as células com os nomes dos animais. Usando nome padrão.")
        nome_arquivo = "static/pedigree_colorido.html"  # Nome padrão
except Exception as e:
    print(f"Erro ao encontrar células para nomear arquivo: {e}. Usando nome padrão.")
    nome_arquivo = "static/pedigree_colorido.html"  # Nome padrão em caso de erro

# Salvar HTML final
try:
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(str(soup))
    print(f"✅ HTML colorido salvo como: {nome_arquivo}")
except Exception as e:
    print(f"Erro ao salvar o arquivo HTML: {e}")
    exit()

# Abrir automaticamente no navegador (funciona localmente)
try:
    caminho_completo = os.path.abspath(nome_arquivo)
    webbrowser.open(f"file://{caminho_completo}")
except Exception as e:
    print(f"Erro ao abrir o arquivo no navegador: {e}")

