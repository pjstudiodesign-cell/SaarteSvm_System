import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÕES DE CONEXÃO (MANTENHA AS SUAS CHAVES AQUI) ---
SUPABASE_URL = "SUA_URL_AQUI"
SUPABASE_KEY = "SUA_CHAVE_AQUI"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão SaarteSvm", layout="wide")

# Estilização CSS para o Modo Premium (Fundo Escuro e Cards)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { color: #00d4ff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1f2937; color: white; border: 1px solid #374151; }
    .stButton>button:hover { background-color: #374151; border-color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("🚀 Gestão de Projetos - SaarteSvm")
    
    # --- FORMULÁRIO DE CADASTRO ---
    with st.expander("📝 Novo Projeto / Orçamento", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nome_cliente = st.text_input("Nome do Cliente")
            whatsapp = st.text_input("WhatsApp")
            cpf_cnpj = st.text_input("CPF/CNPJ")
        
        with col2:
            endereco = st.text_area("Endereço Completo", height=68)
            descricao = st.text_area("Descrição do Serviço", height=68)
        
        with col3:
            exigencias = st.text_area("Exigências/Detalhes", height=68)
            prazo = st.text_input("Prazo de Entrega (ex: 15 dias)")

        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            valor_total = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
        with c2:
            # Lógica 50/50 automática para facilitar para o cliente
            valor_ent_sugerido = valor_total / 2
            valor_entrada = st.number_input("Valor Entrada (50%)", value=valor_ent_sugerido, format="%.2f")
        with c3:
            valor_final = st.number_input("Valor Final (50%)", value=(valor_total - valor_entrada), format="%.2f")
        with c4:
            data_projeto = st.date_input("Data do Pedido", datetime.now())

        if st.button("Salvar Novo Projeto"):
            if nome_cliente and valor_total > 0:
                dados = {
                    "cliente": nome_cliente,
                    "whatsapp": whatsapp,
                    "cpf_cnpj": cpf_cnpj,
                    "endereco_cliente": endereco,
                    "descricao_servico": descricao,
                    "exigencias": exigencias,
                    "prazo_entrega": prazo,
                    "valor_total": valor_total,
                    "valor_entrada": valor_entrada,
                    "valor_final": valor_final,
                    "data": data_projeto.strftime("%Y-%m-%d"),
                    "status_entrada": "Pendente",
                    "status_final": "Pendente"
                }
                try:
                    supabase.table("terceiros_saartesvm").insert(dados).execute()
                    st.success("✅ Projeto salvo com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
            else:
                st.warning("Preencha o Nome e o Valor Total.")

    # --- LISTAGEM E GESTÃO ---
    st.markdown("### 📋 Projetos Ativos")
    
    try:
        response = supabase.table("terceiros_saartesvm").select("*").order("id", desc=True).execute()
        df = pd.DataFrame(response.data)
        
        if not df.empty:
            for index, row in df.iterrows():
                with st.container():
                    # Card de Visualização Estilo Premium
                    with st.expander(f"🔹 {row['cliente']} - R$ {row['valor_total']:.2f} ({row['data']})"):
                        c1, c2, c3 = st.columns([2, 2, 1])
                        
                        with c1:
                            st.write(f"**WhatsApp:** {row['whatsapp']}")
                            st.write(f"**CPF/CNPJ:** {row['cpf_cnpj']}")
                            st.write(f"**Endereço:** {row['endereco_cliente']}")
                        
                        with c2:
                            st.write(f"**Serviço:** {row['descricao_servico']}")
                            st.write(f"**Prazo:** {row['prazo_entrega']}")
                            st.write(f"**Status Pagamento:** {row['status_entrada']} / {row['status_final']}")

                        # --- BOTÕES DE AÇÃO ---
                        st.markdown("---")
                        b1, b2, b3, b4 = st.columns(4)
                        
                        with b1:
                            if st.button(f"🔄 Atualizar", key=f"upd_{row['id']}"):
                                # Aqui você pode adicionar a lógica de edição depois
                                st.info("Recurso de edição rápida em breve.")
                        
                        with b2:
                            st.button(f"📄 Orçamento", key=f"orc_{row['id']}")
                        
                        with b3:
                            st.button(f"🧾 Recibo", key=f"rec_{row['id']}")
                            
                        with b4:
                            if st.button(f"🗑️ Excluir", key=f"del_{row['id']}"):
                                supabase.table("terceiros_saartesvm").delete().eq("id", row['id']).execute()
                                st.warning("Projeto excluído.")
                                st.rerun()
        else:
            st.info("Nenhum projeto encontrado.")
            
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")

if __name__ == "__main__":
    main()
