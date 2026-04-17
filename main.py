import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# 1. Configuração da Página
st.set_page_config(page_title="SaarteSvm System", page_icon="⚜️", layout="wide")

# 2. Estilo Visual
def aplicar_estilo():
    st.markdown("""
        <style>
        .stApp { background-color: #0d0d0d; }
        h1, h2, h3, label, p { color: #D4AF37 !important; }
        .stButton>button {
            background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%);
            color: #000 !important; font-weight: bold; border-radius: 8px; width: 100%; border: none;
        }
        section[data-testid="stSidebar"] { background-color: #111111; border-right: 2px solid #D4AF37; }
        .stMetric { background-color: #1a1a1a; padding: 15px; border-radius: 10px; border: 1px solid #333; }
        </style>
    """, unsafe_allow_html=True)

# 3. Funções de PDF
def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo, rev, obs, info):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(20, 20, 20)
        pdf.rect(0, 0, 210, 55, 'F')
        nome = str(info[0]) if info else "SaarteSvm"
        pdf.set_font("Arial", 'B', 24); pdf.set_text_color(212, 175, 55)
        pdf.cell(0, 15, nome, ln=True, align='C')
        pdf.set_font("Arial", 'I', 10); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 5, str(info[1]), ln=True, align='C')
        pdf.ln(20); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12)
        pdf.cell(100, 10, f"CLIENTE: {str(cliente).upper()}", ln=0)
        pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
        pdf.ln(10); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "1. DESCRICAO DO SERVICO", ln=True)
        pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}")
        pdf.set_y(-40); pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 15, f"INVESTIMENTO TOTAL: R$ {valor:,.2f}", ln=True, align='R')
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except: return None

# 4. Lógica de Banco de Dados
def iniciar_db():
    conn = sqlite3.connect('saartesvm_data.db', check_same_thread=False)
    cursor = conn.cursor()
    # Tabela de Projetos
    cursor.execute("CREATE TABLE IF NOT EXISTS projetos (id INTEGER PRIMARY KEY AUTOINCREMENT, cliente TEXT, servico TEXT, valor REAL, status TEXT, data_inicio TEXT, telefone TEXT, valor_entrada REAL, status_entrada TEXT, valor_final REAL, status_final TEXT, status_integral TEXT, prazo_salvo TEXT, pagamento_salvo TEXT, revisao_salva TEXT, obs_salva TEXT)")
    # Tabela de Configuração
    cursor.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, nome_studio TEXT, sub_titulo TEXT, contato TEXT, email TEXT, endereco TEXT)")
    # Dados Iniciais
    cursor.execute("SELECT COUNT(*) FROM config")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO config VALUES (1, 'SaarteSvm', 'Studio Criativo', '', '', '')")
    conn.commit()
    return conn

# 5. Interface
def main():
    aplicar_estilo()
    conn = iniciar_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT nome_studio, sub_titulo, contato, email, endereco FROM config WHERE id=1")
    config_res = cursor.fetchone()
    
    st.sidebar.title(f"⚜️ {config_res[0]}")
    escolha = st.sidebar.radio("Navegar:", ["Painel", "Novo Job", "Gestão", "Configurações"])

    if escolha == "Painel":
        st.title(f"⚜️ Painel {config_res[0]}")
        st.info("Bem-vindo ao sistema de gestão SaarteSvm.")

    elif escolha == "Novo Job":
        st.title("⚜️ Novo Orçamento")
        with st.form("orc_form"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Cliente"); tel = c2.text_input("WhatsApp")
            v = st.number_input("Valor Total", min_value=0.0)
            ser = st.text_area("Serviço")
            prz = st.text_input("Prazo", "10 dias")
            pag = st.text_input("Pagamento", "50% entrada / 50% entrega")
            if st.form_submit_button("SALVAR"):
                if n and ser:
                    cursor.execute("INSERT INTO projetos (cliente, servico, valor, status, data_inicio, telefone, valor_entrada, status_entrada, valor_final, status_final, status_integral, prazo_salvo, pagamento_salvo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (n, ser, v, "Em Produção", datetime.now().strftime("%d/%m/%Y"), tel, v/2, "Pendente", v/2, "Pendente", "Pendente", prz, pag))
                    conn.commit()
                    st.success("Salvo!")
                else: st.error("Preencha os campos.")

    elif escolha == "Gestão":
        st.title("⚜️ Gestão")
        df = pd.read_sql_query("SELECT * FROM projetos", conn)
        st.dataframe(df)

    elif escolha == "Configurações":
        st.title("⚙️ Configurações")
        with st.form("cfg"):
            novo_nome = st.text_input("Nome", config_res[0])
            if st.form_submit_button("Salvar"):
                cursor.execute("UPDATE config SET nome_studio=? WHERE id=1", (novo_nome,))
                conn.commit(); st.rerun()
    conn.close()

if __name__ == "__main__":
    main()
