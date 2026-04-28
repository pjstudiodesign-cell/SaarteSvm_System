import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÕES DE CONEXÃO (LACRADAS) ---
SUPABASE_URL = "https://emrjgeukqueyyxzhbpro.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtcmpnZXVrcXVleXl4emhicHJvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0ODEzODAsImV4cCI6MjA5MjA1NzM4MH0.zEk_qYIvErts5aO9fJ6EL6ZU--Pm7woqugCfW3i0yyY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CONFIGURAÇÃO DA PÁGINA (ESTILO PREMIUM MANUTENÇÃO ZERO) ---
st.set_page_config(page_title="SaarteSvm - Gestão", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #1f2937; color: white; border: 1px solid #374151; }
    .stButton>button:hover { border-color: #00d4ff; color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("🚀 SaarteSvm | Controle de Projetos")
    
    # --- FORMULÁRIO: ADIÇÃO DOS NOVOS CAMPOS (CPF, ENDEREÇO, FINANCEIRO) ---
    with st.expander("📝 Cadastrar Novo Projeto / Orçamento", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nome = st.text_input("Nome do Cliente")
            zap = st.text_input("WhatsApp")
            doc = st.text_input("CPF/CNPJ")
        
        with col2:
            end = st.text_area("Endereço", height=68)
            servico = st.text_area("Descrição do Serviço", height=68)
        
        with col3:
            exige = st.text_area("Exigências", height=68)
            prazo = st.text_input("Prazo de Entrega")

        st.markdown("---")
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            v_total = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
        with f2:
            # Lógica 50/50 automática conforme solicitado
            v_ent = st.number_input("Entrada (50%)", value=v_total/2, format="%.2f")
        with f3:
            v_fin = st.number_input("Final (50%)", value=v_total - v_ent, format="%.2f")
        with f4:
            data_p = st.date_input("Data", datetime.now())

        if st.button("💾 SALVAR PROJETO NO MOTOR"):
            if nome and v_total > 0:
                payload = {
                    "cliente": nome, "whatsapp": zap, "cpf_cnpj": doc,
                    "endereco_cliente": end, "descricao_servico": servico,
                    "exigencias": exige, "prazo_entrega": prazo,
                    "valor_total": v_total, "valor_entrada": v_ent, "valor_final": v_fin,
                    "data": data_p.strftime("%Y-%m-%d"),
                    "status_entrada": "Pendente", "status_final": "Pendente"
                }
                try:
                    supabase.table("projetos_saartesvm").insert(payload).execute()
                    st.success("✅ Gravado com sucesso na gaveta do cliente!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro de Gravação: {e}")

    # --- LISTAGEM: VISUALIZAÇÃO E AÇÕES ---
    st.markdown("### 📋 Painel de Projetos Ativos")
    try:
        res = supabase.table("projetos_saartesvm").select("*").order("id", desc=True).execute()
        dados = res.data
        
        if dados:
            for item in dados:
                with st.expander(f"📌 {item['cliente']} | R$ {item['valor_total']:.2f}"):
                    c1, c2, c3 = st.columns([1, 1, 1])
                    with c1:
                        st.write(f"**WhatsApp:** {item.get('whatsapp')}")
                        st.write(f"**Doc:** {item.get('cpf_cnpj')}")
                    with c2:
                        st.write(f"**Serviço:** {item.get('descricao_servico')}")
                        st.write(f"**Prazo:** {item.get('prazo_entrega')}")
                    with c3:
                        st.write(f"**Entrada:** R$ {item.get('valor_entrada')} ({item.get('status_entrada')})")
                        st.write(f"**Final:** R$ {item.get('valor_final')} ({item.get('status_final')})")
                    
                    st.markdown("---")
                    # Botões conforme layouts image_332a6b, image_332a11, image_32c0d2
                    b1, b2, b3, b4 = st.columns(4)
                    with b1: st.button("🔄 Atualizar", key=f"up_{item['id']}")
                    with b2: st.button("📄 Orçamento", key=f"or_{item['id']}")
                    with b3: st.button("🧾 Recibo", key=f"re_{item['id']}")
                    with b4:
                        if st.button("🗑️ Excluir", key=f"ex_{item['id']}"):
                            supabase.table("projetos_saartesvm").delete().eq("id", item['id']).execute()
                            st.rerun()
        else:
            st.info("Aguardando o primeiro registro na base SaarteSvm.")
    except Exception as e:
        st.error(f"Erro ao ler motor: {e}")

if __name__ == "__main__":
    main()
