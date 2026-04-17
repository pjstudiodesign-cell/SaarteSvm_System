import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# 1. Configuração da Página
st.set_page_config(page_title="SaarteSvm System", page_icon="⚜️", layout="wide")

# 2. Estilo Visual Luxo
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
        nome_st = str(info[0]) if info else "SaarteSvm"
        pdf.set_font("Arial", 'B', 24); pdf.set_text_color(212, 175, 55)
        pdf.cell(0, 15, nome_st, ln=True, align='C')
        pdf.set_font("Arial", 'I', 10); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 5, str(info[1]), ln=True, align='C')
        pdf.ln(20); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 12)
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
    escolha = st.sidebar.radio("Navegar:", ["Painel", "Novo Job", "Gestão", "Configurações"])

    if escolha == "Painel":
        st.title(f"⚜️ Painel {config_res[0]}")
        df = pd.read_sql_query("SELECT * FROM projetos", conn)
        total = df['valor'].sum() if not df.empty else 0.0
        st.markdown(f"<div class='stMetric'><b>Total em Projetos</b><br><h2>R$ {total:,.2f}</h2></div>", unsafe_allow_html=True)

    elif escolha == "Novo Job":
        st.title("⚜️ Novo Orçamento")
        with st.form("orc_form"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Cliente"); tel = c2.text_input("WhatsApp")
            v = st.number_input("Valor Total", min_value=0.0, step=0.01)
            ser = st.text_area("Serviço")
            obs_input = st.text_input("Observações")
            c3, c4, c5 = st.columns(3)
            prz = c3.text_input("Prazo", "10 dias úteis")
            rev_input = c4.selectbox("Revisões", ["Padrão", "1", "2", "Ilimitadas"])
            pag = c5.text_input("Pagamento", "50% entrada / 50% entrega")
            
            if st.form_submit_button("SALVAR E GERAR PDF"):
                if n and ser:
                    cursor.execute("""INSERT INTO projetos (cliente, servico, valor, status, data_inicio, telefone, 
                        valor_entrada, status_entrada, valor_final, status_final, status_integral, 
                        prazo_salvo, pagamento_salvo, revisao_salva, obs_salva) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (n, ser, v, "Em Produção", datetime.now().strftime("%d/%m/%Y"), tel, v/2, "Pendente", v/2, "Pendente", "Pendente", prz, pag, rev_input, obs_input))
                    conn.commit()
                    st.session_state.pdf_data = gerar_pdf_orcamento(n, ser, v, pag, prz, rev_input, obs_input, config_res)
                    st.success("Orçamento salvo!")
                else: st.error("Preencha os campos obrigatórios.")

        if 'pdf_data' in st.session_state and st.session_state.pdf_data:
            st.download_button("📥 BAIXAR PDF", st.session_state.pdf_data, "Orcamento.pdf", "application/pdf")

    elif escolha == "Gestão":
        st.title("⚜️ Gestão de Projetos")
        df = pd.read_sql_query("SELECT * FROM projetos ORDER BY id DESC", conn)
        if not df.empty:
            for _, r in df.iterrows():
                with st.expander(f"📌 {r['cliente']} - R$ {r['valor']:.2f}"):
                    st.write(f"**Serviço:** {r['servico']}")
                    st.write(f"**Obs:** {r['obs_salva']}")
                    if st.button("Excluir", key=f"del{r['id']}"):
                        cursor.execute("DELETE FROM projetos WHERE id=?", (r['id'],)); conn.commit(); st.rerun()
        else: st.info("Nenhum projeto encontrado.")

    elif escolha == "Configurações":
        st.title("⚙️ Configurações")
        with st.form("cfg"):
            n_s = st.text_input("Nome", config_res[0]); sub_s = st.text_input("Slogan", config_res[1])
            t_s = st.text_input("WhatsApp", config_res[2]); e_s = st.text_input("Email", config_res[3])
            if st.form_submit_button("Salvar"):
                cursor.execute("UPDATE config SET nome_studio=?, sub_titulo=?, contato=?, email=? WHERE id=1", (n_s, sub_s, t_s, e_s))
                conn.commit(); st.rerun()
    conn.close()

if __name__ == "__main__":
    main()
