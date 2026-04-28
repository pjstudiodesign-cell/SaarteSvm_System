import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os
from supabase import create_client, Client

# 1. Configuração da Página
st.set_page_config(page_title="SaarteSvm System", page_icon="⚜️", layout="wide")

# 2. Conexão Blindada com Supabase (Puxando do Render)
@st.cache_resource
def iniciar_conexao():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        st.error("Erro: Chaves de conexão não encontradas no Render.")
        return None
    return create_client(url, key)

supabase = iniciar_conexao()

# 3. Estilo Visual Premium (Mantido exatamente como o original)
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
        .st-emotion-cache-1835771 { background-color: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #333; }
        [data-testid="stMetricLabel"] { color: #ffffff !important; font-size: 1.2em !important; }
        [data-testid="stMetricValue"] { color: #D4AF37 !important; }
        </style>
    """, unsafe_allow_html=True)

# 4. Busca de Dados da Empresa (Agora via Supabase)
def buscar_dados_empresa():
    try:
        res = supabase.table("config").select("*").eq("id", 1).execute()
        if res.data:
            d = res.data[0]
            return (d['nome_studio'], d['sub_titulo'], d['contato'], d['email'], d['endereco'])
    except:
        pass
    return ("SaarteSvm", "Studio Criativo", "", "", "")

# 5. Geração de PDF (Lógica Original Mantida)
def gerar_pdf_orcamento(cliente, servico, valor, pgto, prazo, rev, obs):
    try:
        info = buscar_dados_empresa()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(20, 20, 20)
        pdf.rect(0, 0, 210, 65, 'F')
        pdf.set_y(12)
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(212, 175, 55)
        pdf.cell(0, 12, "SaarteSvm", ln=True, align='C')
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 6, str(info[1]), ln=True, align='C')
        pdf.set_font("Arial", '', 9)
        pdf.set_text_color(200, 200, 200)
        pdf.cell(0, 6, f"WhatsApp: {info[2]} | Email: {info[3]}", ln=True, align='C')
        if info[4]: pdf.multi_cell(0, 5, f"Endereço: {info[4]}", align='C')
        pdf.set_y(75)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(100, 10, f"CLIENTE: {str(cliente).upper()}", ln=0)
        pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
        pdf.ln(10); pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "1. DESCRICAO DO SERVICO", ln=True)
        pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}")
        if obs:
            pdf.ln(2); pdf.set_font("Arial", 'B', 11); pdf.cell(10, 7, "Obs: ")
            pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{obs}")
        pdf.ln(5); pdf.set_font("Arial", 'B', 14); pdf.cell(0, 10, "2. CONDICOES", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, f"- Prazo: {prazo} | Revisões: {rev}", ln=True)
        pdf.cell(0, 8, f"- Forma de Pagamento: {pgto}", ln=True)
        pdf.set_y(-40); pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 15, f"INVESTIMENTO TOTAL: R$ {valor:,.2f}", ln=True, align='R')
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except: return None

def gerar_pdf_recibo(cliente, servico, valor):
    try:
        pdf = FPDF()
        pdf.add_page(); pdf.set_draw_color(212, 175, 55); pdf.rect(5, 5, 200, 120)
        pdf.set_font("Arial", 'B', 18); pdf.set_y(15)
        pdf.cell(0, 15, "RECIBO DE PAGAMENTO", ln=True, align='C')
        pdf.ln(10); pdf.set_font("Arial", '', 12)
        texto = f"Recebemos de {str(cliente).upper()}, a importância de R$ {valor:,.2f} referente ao serviço de: {servico}."
        pdf.multi_cell(0, 10, texto, align='L')
        pdf.ln(10); pdf.cell(0, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align='R')
        pdf.ln(15); pdf.cell(0, 10, "__________________________________________________", ln=True, align='C')
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 5, "SaarteSvm", ln=True, align='C')
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except: return None

# 6. Interface Principal
def main():
    aplicar_estilo()
    info_sidebar = buscar_dados_empresa()
    st.sidebar.title(f"⚜️ {info_sidebar[0]}")
    menu = ["Painel", "Novo Job", "Gestão de Projetos", "Configurações"]
    escolha = st.sidebar.radio("Navegar:", menu)

    if escolha == "Painel":
        st.title(f"⚜️ Painel {info_sidebar[0]}")
        res = supabase.table("projetos_saartesvm").select("*").execute()
        df = pd.DataFrame(res.data)
        total_rec = 0.0; total_pend = 0.0
        if not df.empty:
            for _, r in df.iterrows():
                v_total = float(r['valor_total']) if r['valor_total'] else 0.0
                if r['status'] == 'Pago': total_rec += v_total
                else: total_pend += v_total
        col1, col2 = st.columns(2)
        with col1: st.metric("Total em Caixa", f"R$ {total_rec:,.2f}")
        with col2: st.metric("A Receber", f"R$ {total_pend:,.2f}")

    elif escolha == "Novo Job":
        st.title("⚜️ Novo Orçamento")
        with st.form("orc_form"):
            c1, c2 = st.columns(2); n = c1.text_input("Cliente"); tel = c2.text_input("WhatsApp")
            v = st.number_input("Valor Total", min_value=0.0, step=0.01)
            ser = st.text_area("Serviço"); obs_in = st.text_input("Observações")
            c3, c4, c5 = st.columns(3); prz = c3.text_input("Prazo", "10 dias úteis")
            rev = c4.selectbox("Revisões", ["Padrão", "1", "2", "3", "Ilimitadas"])
            pag = c5.text_input("Pagamento", "50% entrada / 50% entrega")
            if st.form_submit_button("SALVAR"):
                if n and ser:
                    dados = {
                        "cliente": n, "nome_projeto": ser, "valor_total": v, 
                        "status": "Pendente"
                    }
                    supabase.table("projetos_saartesvm").insert(dados).execute()
                    st.success("Orçamento Salvo na Nuvem!")
                else: st.error("Preencha os campos obrigatórios.")

    elif escolha == "Gestão de Projetos":
        st.title("⚜️ Gestão e Financeiro")
        res = supabase.table("projetos_saartesvm").select("*").order("id", desc=True).execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            for _, r in df.iterrows():
                with st.expander(f"📌 {r['cliente']} | R$ {float(r['valor_total']):.2f}"):
                    st.write(f"**Serviço:** {r['nome_projeto']}")
                    col1, col2, col3, col4 = st.columns(4)
                    status_atual = col1.selectbox("Status", ["Pendente", "Pago"], index=0 if r['status'] == "Pendente" else 1, key=f"st{r['id']}")
                    if col2.button("Atualizar", key=f"up{r['id']}"):
                        supabase.table("projetos_saartesvm").update({"status": status_atual}).eq("id", r['id']).execute()
                        st.rerun()
                    if col3.button("Recibo", key=f"rec{r['id']}"):
                        pdf_r = gerar_pdf_recibo(r['cliente'], r['nome_projeto'], float(r['valor_total']))
                        if pdf_r: st.download_button("Baixar Recibo", pdf_r, f"Recibo_{r['cliente']}.pdf", key=f"dlr{r['id']}")
                    if col4.button("Excluir", key=f"del{r['id']}"):
                        supabase.table("projetos_saartesvm").delete().eq("id", r['id']).execute()
                        st.rerun()
        else: st.info("Nenhum projeto encontrado.")

    elif escolha == "Configurações":
        st.title("⚙️ Configurações da Empresa")
        info_form = buscar_dados_empresa()
        with st.form("form_config"):
            nome_emp = st.text_input("Nome do Studio/Empresa", info_form[0])
            slogan_emp = st.text_input("Slogan ou Subtítulo", info_form[1])
            whats_emp = st.text_input("WhatsApp de Contato", info_form[2])
            email_emp = st.text_input("E-mail", info_form[3])
            end_emp = st.text_area("Endereço Completo", info_form[4])
            if st.form_submit_button("SALVAR"):
                dados_config = {"nome_studio": nome_emp, "sub_titulo": slogan_emp, "contato": whats_emp, "email": email_emp, "endereco": end_emp}
                supabase.table("config").update(dados_config).eq("id", 1).execute()
                st.success("Configurações Salvas!"); st.rerun()

if __name__ == "__main__":
    main()
