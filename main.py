import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# ==========================================
# CONFIGURAÇÃO VISUAL - PADRÃO LUXO SAARTESVM
# ==========================================
st.set_page_config(page_title="SaarteSvm System", page_icon="⚜️", layout="wide")

def aplicar_estilo_saartesvm():
    st.markdown("""
        <style>
        .stApp { background-color: #0d0d0d; }
        h1, h2, h3, label, p { color: #D4AF37 !important; }
        .stButton>button {
            background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%);
            color: #000 !important;
            font-weight: bold;
            border-radius: 8px;
            width: 100%;
            border: none;
        }
        section[data-testid="stSidebar"] { 
            background-color: #111111; 
            border-right: 2px solid #D4AF37; 
        }
        .stMetric {
            background-color: #1a1a1a;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #333;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# FUNÇÕES DE PDF (ORÇAMENTO E RECIBO)
# ==========================================
def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo, rev, obs, info):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(20, 20, 20)
        pdf.rect(0, 0, 210, 55, 'F')
        
        nome_empresa = str(info[0]) if info else "SaarteSvm"
        slogan = str(info[1]) if info else "Studio Criativo"
        contato = str(info[2]) if info else ""
        email = str(info[3]) if info else ""
        endereco = str(info[4]) if info else ""

        pdf.set_font("Arial", 'B', 24)
        pdf.set_text_color(212, 175, 55)
        pdf.cell(0, 15, nome_empresa, ln=True, align='C')
        pdf.set_font("Arial", 'I', 10); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 5, slogan, ln=True, align='C')
        pdf.set_font("Arial", '', 9)
        pdf.cell(0, 5, f"WhatsApp: {contato} | Email: {email}", ln=True, align='C')
        pdf.cell(0, 5, f"Endereco: {endereco}", ln=True, align='C')
        
        pdf.ln(20); pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(100, 10, f"CLIENTE: {str(cliente).upper()}", ln=0)
        pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
        
        pdf.ln(10); pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "1. DESCRICAO DO SERVICO", ln=True)
        pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}")
        
        if obs:
            pdf.ln(2)
            pdf.set_font("Arial", 'B', 11); pdf.cell(10, 7, "Obs: "); pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{obs}")
        
        pdf.ln(5); pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "2. CONDICOES E ENTREGA", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, f"- Prazo: {prazo} | Revisoes: {rev}", ln=True)
        pdf.cell(0, 8, f"- Pagamento: {pgto}", ln=True)
        
        pdf.set_y(-40); pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 15, f"INVESTIMENTO TOTAL: R$ {valor:,.2f}", ln=True, align='R')
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {e}")
        return None

def gerar_pdf_recibo(cliente, servico, valor, info):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_draw_color(212, 175, 55); pdf.rect(5, 5, 200, 100)
    pdf.set_font("Arial", 'B', 18); pdf.cell(0, 15, "RECIBO DE PAGAMENTO", ln=True, align='C')
    pdf.ln(5); pdf.set_font("Arial", '', 12)
    texto = f"Recebemos de {str(cliente).upper()}, a importancia de R$ {valor:,.2f} referente ao servico de: {servico}."
    pdf.multi_cell(0, 10, texto, align='L')
    pdf.ln(10); pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='R')
    pdf.ln(10); pdf.cell(0, 10, "__________________________________________________", ln=True, align='C')
    pdf.set_font("Arial", 'B', 10); pdf.cell(0, 5, str(info[0]) if info else "SaarteSvm", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# ==========================================
# LOGICA PRINCIPAL
# ==========================================
def main():
    aplicar_estilo_saartesvm()
    # Banco de dados específico para o cliente
    conn = sqlite3.connect('saartesvm_data.db', check_same_thread=False); cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS projetos 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, servico TEXT, valor REAL, status TEXT, 
                       data_inicio TEXT,
