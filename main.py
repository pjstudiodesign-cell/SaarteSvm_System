import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os
from supabase import create_client, Client

# 1. Configuração da Página
st.set_page_config(page_title="SaarteSvm System", page_icon="⚜️", layout="wide")

# 2. Conexão Blindada
@st.cache_resource
def iniciar_conexao():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key: return None
    return create_client(url, key)

supabase = iniciar_conexao()

# 3. Estilo Visual Premium (INTOCADO)
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
            color: #000000 !important; font-weight: bold !important;
            border-radius: 8px !important; width: 100% !important; border: none !important;
        }
        section[data-testid="stSidebar"] { background-color: #111111; border-right: 2px solid #D4AF37; }
        .st-emotion-cache-1835771 { background-color: #1a1a1a; padding: 20px; border-radius: 12px; border: 1px solid #333; }
        </style>
    """, unsafe_allow_html=True)

def buscar_dados_empresa():
    try:
        res = supabase.table("config").select("*").eq("id", 1).execute()
        if res.data:
            d = res.data[0]
            return (d['nome_studio'], d['sub_titulo'], d['contato'], d['email'], d['endereco'])
    except: pass
    return ("SaarteSvm", "Studio Criativo", "", "", "")

# 4. Motor de PDF CORRIGIDO (Foco em 1 Única Folha)
def gerar_documento_pdf(tipo, cliente, servico, valor, doc_id="", prazo=""):
    try:
        info = buscar_dados_empresa()
        pdf = FPDF()
        pdf.set_auto_page_break(auto=False) # IMPEDE A SEGUNDA FOLHA AUTOMÁTICA
        pdf.add_page()
        
        # Cabeçalho Dourado
        pdf.set_fill_color(20, 20, 20); pdf.rect(0, 0, 210, 65, 'F')
        pdf.set_y(12); pdf.set_font("Arial", 'B', 20); pdf.set_text_color(212, 175, 55)
        pdf.cell(0, 12, info[0], ln=True, align='C')
        pdf.set_font("Arial", 'I', 10); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 6, str(info[1]), ln=True, align='C')
        pdf.set_font("Arial", '', 9); pdf.set_text_color(200, 200, 200)
        pdf.cell(0, 6, f"{info[2]} | {info[3]}", ln=True, align='C')
        
        # Corpo do Documento
        pdf.set_y(75); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"{tipo.upper()}", ln=True, align='C')
        pdf.ln(5); pdf.set_font("Arial", 'B', 11)
        pdf.cell(100, 10, f"CLIENTE: {str(cliente).upper()}", ln=0)
        pdf.cell(0, 10, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align='R')
        pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "DESCRICAO DO SERVICO", ln=True)
        pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 7, f"{servico}")
        
        if prazo:
            pdf.ln(2); pdf.set_font("Arial", 'B', 11); pdf.cell(0, 10, f"PRAZO DE EXECUCAO: {prazo}", ln=True)
        
        pdf.ln(10); pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 15, f"VALOR: R$ {float(valor):,.2f}", ln=True, align='R')
        
        # Rodapé Ajustado (Mais alto para não pular folha)
        pdf.set_y(275) # POSIÇÃO SEGURA NA PRIMEIRA FOLHA
        pdf.set_font("Arial", 'I', 8); pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, f"Autenticado via SaarteSvm System - ID: {doc_id}", align='C')
        
        return pdf.output(dest='S').encode('latin-1', 'ignore')
    except: return None

# 5. Interface e Lógica de Gestão (INTOCADA E FUNCIONAL)
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
            c1, c2, c3 = st.columns(3)
            n = c1.text_input("Cliente"); tel = c2.text_input("WhatsApp"); doc = c3.text_input("CPF/CNPJ")
            end_cli = st.text_input("Endereço Completo")
            prz_exec = st.text_input("Prazo de Execução")
            ser = st.text_area("Serviço")
            c4, c5, c6 = st.columns(3)
            v_total = c4.number_input("Valor Total", min_value=0.0, step=0.01)
            v_ent = c5.number_input("Entrada (50%)", value=v_total/2)
            v_fin = c6.number_input("Final (50%)", value=v_total/2)
            
            if st.form_submit_button("GERAR E SALVAR"):
                if n and ser:
                    dados = {
                        "cliente": n, "nome_projeto": ser, "valor_total": v_total,
                        "valor_entrada": v_ent, "valor_final": v_fin, "prazo_execucao": prz_exec,
                        "status": "Pendente", "whatsapp": tel, "cpf_cnpj": doc, "endereco_cliente": end_cli
                    }
                    supabase.table("projetos_saartesvm").insert(dados).execute()
                    st.success("Projeto Registrado!")
                else: st.error("Campos obrigatórios.")

    elif escolha == "Gestão de Projetos":
        st.title("⚜️ Gestão e Documentação")
        res = supabase.table("projetos_saartesvm").select("*").order("id", desc=True).execute()
        for r in res.data:
            with st.expander(f"📝 EDITAR: {r['cliente']} | ID: {r['id']}"):
                with st.form(f"edit_{r['id']}"):
                    ec1, ec2, ec3 = st.columns(3)
                    en = ec1.text_input("Cliente", value=r['cliente'])
                    et = ec2.text_input("WhatsApp", value=r.get('whatsapp', ''))
                    edoc = ec3.text_input("CPF/CNPJ", value=r.get('cpf_cnpj', ''))
                    eend = st.text_input("Endereço", value=r.get('endereco_cliente', ''))
                    eprz = st.text_input("Prazo", value=r.get('prazo_execucao', ''))
                    eser = st.text_area("Serviço", value=r['nome_projeto'])
                    ec4, ec5, ec6 = st.columns(3)
                    ev_t = ec4.number_input("Valor Total", value=float(r['valor_total']))
                    ev_e = ec5.number_input("Entrada", value=float(r.get('valor_entrada', ev_t/2)))
                    ev_f = ec6.number_input("Final", value=float(r.get('valor_final', ev_t/2)))
                    estatus = st.selectbox("Status", ["Pendente", "Pago"], index=0 if r['status'] == "Pendente" else 1)
                    
                    if st.form_submit_button("ATUALIZAR DADOS"):
                        up = {"cliente": en, "whatsapp": et, "cpf_cnpj": edoc, "endereco_cliente": eend, "nome_projeto": eser, 
                              "valor_total": ev_t, "valor_entrada": ev_e, "valor_final": ev_f, "status": estatus, "prazo_execucao": eprz}
                        supabase.table("projetos_saartesvm").update(up).eq("id", r['id']).execute()
                        st.success("Atualizado!")
                        st.rerun()

                st.write("---")
                doc1, doc2, doc3, doc4 = st.columns(4)
                pdf_orc = gerar_documento_pdf("Orcamento", r['cliente'], r['nome_projeto'], r['valor_total'], r['id'], r.get('prazo_execucao', ''))
                doc1.download_button("📄 Orçamento", pdf_orc, f"Orcamento_{r['cliente']}.pdf", key=f"orc_{r['id']}")
                pdf_ent = gerar_documento_pdf("Recibo Entrada", r['cliente'], r['nome_projeto'], r.get('valor_entrada', ev_t/2), r['id'], r.get('prazo_execucao', ''))
                doc2.download_button("💰 Recibo Entrada", pdf_ent, f"Recibo_Entrada_{r['cliente']}.pdf", key=f"ent_{r['id']}")
                pdf_fin = gerar_documento_pdf("Recibo Final", r['cliente'], r['nome_projeto'], r.get('valor_final', ev_t/2), r['id'], r.get('prazo_execucao', ''))
                doc3.download_button("✅ Recibo Final", pdf_fin, f"Recibo_Final_{r['cliente']}.pdf", key=f"fin_{r['id']}")
                pdf_tot = gerar_documento_pdf("Recibo Total", r['cliente'], r['nome_projeto'], r['valor_total'], r['id'], r.get('prazo_execucao', ''))
                doc4.download_button("💎 Recibo Total", pdf_tot, f"Recibo_Total_{r['cliente']}.pdf", key=f"tot_{r['id']}")

    elif escolha == "Configurações":
        st.title("⚙️ Configurações")
        info = buscar_dados_empresa()
        with st.form("conf"):
            n = st.text_input("Nome Studio", info[0]); s = st.text_input("Slogan", info[1])
            c = st.text_input("Contato", info[2]); e = st.text_input("Email", info[3])
            end = st.text_area("Endereço", info[4])
            if st.form_submit_button("SALVAR"):
                supabase.table("config").update({"nome_studio": n, "sub_titulo": s, "contato": c, "email": e, "endereco": end}).eq("id", 1).execute()
                st.rerun()

if __name__ == "__main__":
    main()
