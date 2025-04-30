import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import os
from collections import defaultdict
from urllib.parse import urljoin

ARQUIVO_PLANILHA = "listaanimais_editado.xlsx"
ARQUIVO_HTML = "static/pedigree.html"
ARQUIVO_HTML_COLORIDO = "static/pedigree_colorido.html"
ARQUIVO_HTML_BASE = "7gbasehipotetico.html"

st.set_page_config(page_title="Pedigree por Macho e Fêmea", layout="centered")
st.title("🏏️ Gerador de Pedigree (Macho + Fêmea)")

try:
    planilhas = pd.read_excel(ARQUIVO_PLANILHA, sheet_name=None, dtype=str)
    df_machos = planilhas.get("Machos")
    df_femeas = planilhas.get("Femeas")

    if df_machos is not None:
        df_machos.columns = df_machos.columns.str.strip()
        df_machos = df_machos.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    if df_femeas is not None:
        df_femeas.columns = df_femeas.columns.str.strip()
        df_femeas = df_femeas.applymap(lambda x: x.strip() if isinstance(x, str) else x)

except FileNotFoundError:
    st.error(f"❌ Arquivo '{ARQUIVO_PLANILHA}' não encontrado.")
    st.stop()

if df_machos is None or df_femeas is None:
    st.error("❌ A planilha precisa conter as abas 'Machos' e 'Femeas'.")
    st.stop()

if "ANIMAIS" not in df_machos.columns or "ANIMAIS1" not in df_femeas.columns:
    st.error("❌ A aba 'Machos' precisa conter a coluna 'ANIMAIS' e a aba 'Femeas' a coluna 'ANIMAIS1'.")
    st.stop()

animal_macho = st.selectbox("Selecione o Macho:", df_machos["ANIMAIS"].dropna().unique())
animal_femea = st.selectbox("Selecione a Fêmea:", df_femeas["ANIMAIS1"].dropna().unique())

with st.form("formulario"):
    gerar = st.form_submit_button("OK")

if gerar and animal_macho and animal_femea:
    st.session_state["animal_macho"] = animal_macho
    st.session_state["animal_femea"] = animal_femea

if "animal_macho" in st.session_state and "animal_femea" in st.session_state:
    animal_macho = st.session_state["animal_macho"]
    animal_femea = st.session_state["animal_femea"]

    macho = df_machos[df_machos["ANIMAIS"] == animal_macho].iloc[0]
    femea = df_femeas[df_femeas["ANIMAIS1"] == animal_femea].iloc[0]

    st.write(f"📅 Macho selecionado: {animal_macho}")
    st.write(f"📅 Fêmea selecionada: {animal_femea}")

    try:
        with open(ARQUIVO_HTML_BASE, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
    except FileNotFoundError:
        st.error(f"❌ Arquivo '{ARQUIVO_HTML_BASE}' não encontrado.")
        st.stop()

    dados = {}
    for col in macho.index:
        if pd.notna(macho[col]):
            dados[str(col).strip()] = macho[col].strip()
    for col in femea.index:
        if pd.notna(femea[col]):
            dados[str(col).strip()] = femea[col].strip()

    for td in soup.find_all("td"):
        texto = td.get_text(strip=True)
        if texto in dados:
            td.clear()
            span = soup.new_tag("span")
            span['style'] = 'display: block; font-size: 9px; font-family: Arial;'
            if texto.startswith("7"):
                span.string = dados[texto]
            else:
                negrito = soup.new_tag("strong")
                negrito.string = dados[texto]
                span.append(negrito)
            td.append(span)

    style_tag = soup.new_tag("style")
    style_tag.string = """
    body, table, td, th, span, p, div {
        font-size: 9px !important;
        line-height: 1.2em !important;
        font-family: Arial, sans-serif !important;
    }
    tr {
        height: auto !important;
    }
    """
    if soup.head:
        soup.head.append(style_tag)

    with open(ARQUIVO_HTML, "w", encoding="utf-8") as f:
        f.write(str(soup))

    with open(ARQUIVO_HTML, "r", encoding="utf-8") as f:
        html_resultado = f.read()

    st.components.v1.html(html_resultado, height=600, scrolling=True)

    if st.button("🔎 Abrir Pedigree em Nova Aba"):
        try:
            ctx = st.runtime.scriptrunner.get_script_run_context()
            if ctx and ctx.request:
                url_base = ctx.request.url.split("/_")[0]
                url_final = urljoin(url_base, ARQUIVO_HTML)
                js = f"window.open('{url_final}', '_blank').focus();"
                st.components.v1.html(f"<script>{js}</script>", height=0, width=0)
        except Exception as e:
            st.error(f"❌ Erro ao abrir nova aba: {e}")

    st.markdown("---")
    st.subheader("🎨 Coloração de Duplicados")

    if st.button("COLORIR DUPLICAÇÕES"):
        try:
            subprocess.run(["python", "7gcoloridohipotetico.py"], check=True)
            ctx = st.runtime.scriptrunner.get_script_run_context()
            if ctx and ctx.request:
                url_base = ctx.request.url.split("/_")[0]
                url_final = urljoin(url_base, ARQUIVO_HTML_COLORIDO)
                js = f"window.open('{url_final}', '_blank').focus();"
                st.components.v1.html(f"<script>{js}</script>", height=0, width=0)
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Erro ao aplicar coloração: {e}")
