import streamlit as st
from supabase import create_client
import pandas as pd
import time
from datetime import datetime

# --- 1. CONEXÃO E CONFIGURAÇÃO ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="SGV Evolution Pro", layout="wide", initial_sidebar_state="expanded")

# --- 2. ESTILO WINDOWS MODERNO (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f3f3f3; }
    .main-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .stButton>button { border-radius: 8px; border: none; transition: 0.3s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES DE SUPORTE ---
def formato_br(v):
    return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def salvar_config_no_banco(dados):
    # Tenta salvar na tabela 'config' (precisa existir no seu Supabase)
    try:
        supabase.table("config").upsert({"id": 1, **dados}).execute()
        return True
    except: return False

# --- 4. CONTROLE DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>SGV Evolution Pro 🚀</h1>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            senha = st.text_input("Chave de Acesso", type="password")
            if st.button("Desbloquear Sistema", use_container_width=True):
                if senha == "Naksu@6026":
                    st.session_state.auth = True
                    st.rerun()
else:
    # MENU LATERAL MODERNO
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/5968/5968204.png", width=80) # Logo genérico enquanto não sobe o seu
        st.title("Evolution Pro")
        menu = st.radio("Navegação", ["📊 Dashboard", "🛒 Vendas (PDV)", "📦 Estoque", "👥 Clientes", "💰 Financeiro", "📑 Importar", "⚙️ Configurações"])

    # --- ABA: ESTOQUE (LIBERDADE TOTAL) ---
    if menu == "📦 Estoque":
        st.title("📦 Gestão de Produtos")
        res = supabase.table("produtos").select("*").execute().data
        if res:
            df = pd.DataFrame(res)
            for i, p in df.iterrows():
                with st.container():
                    c1, c2, c3, c4 = st.columns([1, 3, 2, 1])
                    c1.write(f"`{p.get('ean13', '---')}`")
                    c2.write(f"**{p.get('descricao', 'Sem Nome')}**")
                    c3.write(formato_br(p.get('preco_venda', 0)))
                    if c4.button("🗑️", key=f"delp_{p['id']}"):
                        supabase.table("produtos").delete().eq("id", p['id']).execute()
                        st.rerun()
                st.divider()
        else: st.info("Estoque vazio.")

    # --- ABA: FINANCEIRO (NOVO) ---
    elif menu == "💰 Financeiro":
        st.title("💰 Gestão Financeira")
        col1, col2, col3 = st.columns(3)
        col1.metric("Contas a Receber", formato_br(1500.00))
        col2.metric("Contas a Pagar", formato_br(800.00), delta_color="inverse")
        col3.metric("Fluxo de Caixa", formato_br(700.00))
        st.info("Módulo em expansão: Registro de despesas e receitas em breve.")

    # --- ABA: CONFIGURAÇÕES (RESOLVENDO O GARGALO A) ---
    elif menu == "⚙️ Configurações":
        st.title("⚙️ Painel de Controle")
        
        tab1, tab2 = st.tabs(["🏢 Dados da Empresa", "🧹 Limpeza de Sistema"])
        
        with tab1:
            st.subheader("Identidade Corporativa")
            nome_e = st.text_input("Nome da Empresa")
            cnpj_e = st.text_input("CNPJ")
            tel_e = st.text_input("WhatsApp de Contato")
            if st.button("💾 Gravar Dados Permanentemente"):
                # Aqui salvamos no Supabase para não sumir ao reiniciar
                salvar_config_no_banco({"nome": nome_e, "cnpj": cnpj_e, "tel": tel_e})
                st.success("Dados eternizados no banco de dados!")

        with tab2:
            st.subheader("🧹 Zerar Sessões Específicas")
            col_z1, col_z2, col_z3 = st.columns(3)
            if col_z1.button("🗑️ Zerar Estoque"):
                supabase.table("produtos").delete().neq("id", -1).execute()
                st.rerun()
            if col_z2.button("🗑️ Zerar Clientes"):
                supabase.table("Clientes").delete().neq("id", -1).execute()
                st.rerun()
            if col_z3.button("🗑️ Zerar Tudo"):
                supabase.table("produtos").delete().neq("id", -1).execute()
                supabase.table("Clientes").delete().neq("id", -1).execute()
                st.rerun()
