import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# 1. Configuração da Página
st.set_page_config(page_title="SaarteSvm System", page_icon="⚜️", layout="wide")

# 2. Estilo Visual Premium
def aplicar_estilo():
    st.markdown("""
        <style>
        .stApp { background-color: #0d0d0d; }
        h1, h2, h3 { color: #D4AF37 !important; }
        [data-testid="stSidebarNav"] span { color: #ffffff !important; font-weight: bold !important; }
        .st-emotion-cache-p5msec, .st-emotion-cache-1h9usn2, p { color: #ffffff !important; }
        label { color: #D4AF37 !important; font-weight: bold !important; }

        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%) !important;
            color: #000000 !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            width: 100% !important;
            border: none !important;
            height: 3em !important;
        }
        .stDownloadButton>button p { color: #000000 !important; }
        section[data-testid="stSidebar"] { background-color: #111111; border-right: 2px solid #D4AF37; }
        .stMetric { background-color: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #333; }
        [data-testid="stMetricLabel"] { color: #ffffff !important; font-size: 1.2em !important; }
        [data-testid="stMetricValue"] { color: #D4AF37 !important; }
        </style>
    """, unsafe_allow_html=True)

# 3. Funções de Busca Segura no Banco
def buscar_dados_empresa():
    conn = sqlite3.connect('saartesvm_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nome_studio, sub_titulo, contato, email, endereco FROM config WHERE id=1")
    res = cursor.fetchone()
    conn.close()
    if not res:
        return ("SaarteSvm", "Studio Criativo", "", "", "")
    return res

# 4. Funções de PDF (Orçamento e Recibo)
def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo, rev, obs):
    try:
        info = buscar_dados_empresa()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(20, 20, 20); pdf.rect(0, 0, 210, 65, 'F')
        pdf.set_y(15); pdf.set_font("Arial", 'B', 26); pdf.set_text_color(212, 175, 55)
        pdf.cell(0, 15, str(info[0]).upper(), ln=True, align='C')
        pdf.set_font("Arial", 'I', 12); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 8, str(info[1]), ln=True, align='C')
        pdf.set_y(75); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12)
        pdf.cell(100, 10, f"CLIENTE: {str(cliente).upper()}", ln=0)
        pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
        pdf.ln(10); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "1. DESCRICAO DO SERVICO", ln=True)
        pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}")
        if obs:
            pdf.ln(2); pdf.set_font("Arial", 'B', 11); pdf.cell(10, 7, "Obs: "); pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{obs}")
        pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "2. CONDICOES", ln=True)
        pdf.set_font("Arial", '', 11); pdf.cell(0, 8, f"- Prazo: {prazo} | Revisoes: {rev}", ln=True)
        pdf.cell(0, 8, f"- Pagamento: {pgto}", ln=True)
        pdf.set_y(-40); pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 15, f"INVESTIMENTO TOTAL: R$ {valor:,.2f}", ln=True, align='R')
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except: return None

def gerar_pdf_recibo(cliente, servico, valor):
    try:
        info = buscar_dados_empresa()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_draw_color(212, 175, 55); pdf.rect(5, 5, 200, 120)
        pdf.set_font("Arial", 'B', 18); pdf.set_y(15); pdf.cell(0, 15, "RECIBO DE PAGAMENTO", ln=True, align='C')
        pdf.ln(10); pdf.set_font("Arial", '', 12)
        texto = f"Recebemos de {str(cliente).upper()}, a importancia de R$ {valor:,.2f} referente ao servico de: {servico}."
        pdf.multi_cell(0, 10, texto, align='L')
        pdf.ln(10); pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='R')
        if info and info[4]:
            pdf.ln(5); pdf.set_font("Arial", 'I', 9); pdf.cell(0, 5, f"Endereco: {info[4]}", ln=True, align='C')
        pdf.ln(15); pdf.cell(0, 10, "__________________________________________________", ln=True, align='C')
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 5, str(info[0]), ln=True, align='C')
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except: return None

# 5. Banco de Dados
def iniciar_db():
    conn = sqlite3.connect('saartesvm_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS projetos 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, servico TEXT, valor REAL, status TEXT, 
        data_inicio TEXT, telefone TEXT, valor_entrada REAL, status_entrada TEXT, valor_final REAL, 
        status_final TEXT, status_integral TEXT, prazo_salvo TEXT, pagamento_salvo TEXT, 
        revisao_salva TEXT, obs_salva TEXT)""")
    cursor.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, nome_studio TEXT, sub_titulo TEXT, contato TEXT, email TEXT, endereco TEXT)")
    cursor.execute("SELECT COUNT(*) FROM config")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO config (id, nome_studio, sub_titulo, contato, email, endereco) VALUES (1, 'SaarteSvm', 'Studio Criativo', '', '', '')")
        conn.commit()
    return conn

# 6. Interface Principal
def main():
    aplicar
