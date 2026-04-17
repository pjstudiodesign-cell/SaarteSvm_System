import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# 1. Configuração da Página
st.set_page_config(page_title="SaarteSvm System", page_icon="⚜️", layout="wide")

# 2. Estilo Visual Premium (Correção Total de Contraste)
def aplicar_estilo():
    st.markdown("""
        <style>
        .stApp { background-color: #0d0d0d; }
        
        /* Títulos e textos gerais em Dourado */
        h1, h2, h3, label { color: #D4AF37 !important; }
        
        /* BOTÕES GERAIS E DE DOWNLOAD: Fundo Dourado com Texto PRETO */
        /* Forçando o estilo para os botões de download que estavam brancos */
        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%) !important;
            color: #000000 !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            width: 100% !important;
            border: none !important;
            height: 3em !important;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        }
        
        /* Efeito ao passar o mouse */
        .stButton>button:hover, .stDownloadButton>button:hover {
            border: 1px solid #ffffff !important;
            color: #000000 !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] { 
            background-color: #111111; 
            border-right: 2px solid #D4AF37; 
        }
        
        /* Cards do Painel */
        .stMetric {
            background-color: #1a1a1a;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #333;
            text-align: center;
        }
        .metric-label {
            color: #ffffff !important; 
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 10px;
            display: block;
        }
        .metric-value {
            color: #D4AF37 !important;
            font-size: 2.2em;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

# 3. Funções de Geração de Documentos (PDF)
def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo, rev, obs, info):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(20, 20, 20); pdf.rect(0, 0, 210, 65, 'F')
        nome_st = str(info[0]) if info else "SaarteSvm"
        slogan_st = str(info[1]) if info else ""
        pdf.set_y(15)
        pdf.set_font("Arial", 'B', 24); pdf.set_text_color(212, 175, 55)
        pdf.cell(0, 15, nome_st, ln=True, align='C')
        pdf.set_font("Arial", 'I', 10); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 5, slogan_st, ln=True, align='C')
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

def gerar_pdf_recibo(cliente, servico, valor, info):
    try:
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
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 5, str(info[0]) if info else "SaarteSvm", ln=True, align='C')
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except: return None

# 4. Banco de Dados
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
        cursor.execute("INSERT INTO config VALUES (1, 'SaarteSvm', 'Studio Criativo', '', '', '')")
    conn.commit()
    return conn

# 5. Interface Principal
def main():
    aplicar_estilo()
    conn = iniciar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nome_studio, sub_titulo, contato, email, endereco FROM config WHERE id=1")
    config_res = cursor.fetchone()
    
    st.sidebar.title(f"⚜️ {config_res[0]}")
    menu = ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"]
    escolha = st.sidebar.radio("Navegar:", menu)

    if escolha == "Painel":
        st.title(f"⚜️ Painel {config_res[0]}")
        df = pd.read_sql_query("SELECT * FROM projetos", conn)
        total_rec = 0.0; total_pend = 0.0
        
        if not df.empty:
            for _, r in df.iterrows():
                v_total = r['valor'] or 0; v_ent = r['valor_entrada'] or 0; v_fin = r['valor_final'] or 0
                if r['status_integral'] == 'Recebido': total_rec += v_total
                else:
                    total_rec += (v_ent if r['status_entrada'] == 'Recebido' else 0)
                    total_rec += (v_fin if r['status_final'] == 'Recebido' else 0)
            total_pend = (df['valor'].sum() or 0) - total_rec
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='stMetric'><span class='metric-label'>Total em Caixa</span><span class='metric-value'>R$ {total_rec:,.2f}</span></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='stMetric'><span class='metric-label'>A Receber</span><span class='metric-value'>R$ {total_pend:,.2f}</span></div>", unsafe_allow_html=True)

    elif escolha ==
