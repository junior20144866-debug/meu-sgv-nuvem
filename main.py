import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide", page_icon="📈")

# --- 2. MOTOR DE SINCRONIA E TRATAMENTO DE DADOS ---
def carregar_dados(tabela):
    try:
        res = supabase.table(tabela).select("*").order("id", desc=True).execute()
        return res.data if res.data else []
    except: return []

# --- 3. ESTILO WINDOWS ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F5; }
    .win-card {
        background: white; padding: 20px; border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-top: 4px solid #0078D4;
    }
    .metric-title { font-size: 0.9rem; color: #666; font-weight: bold; text-transform: uppercase; }
    .metric-value { font-size: 1.8rem; font-weight: bold; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR MOTORES 🚀", use_container_width=True):
            if senha == "Naksu@6026":
                st.session_state.auth = True
                st.rerun()
else:
    # CARREGAMENTO GLOBAL
    config_db = carregar_dados("config")
    emp = config_db[0] if config_db else {}
    estoque = carregar_dados("produtos")
    clientes = carregar_dados("Clientes")

    with st.sidebar:
        if emp.get('logo_base64'):
            st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'SISTEMA SGV'))
        st.write("---")
        menu = st.radio("MÓDULOS", ["🏠 Dashboard", "🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Ajustes"])

    # --- MÓDULO: VENDAS (NOVO) ---
    if menu == "🛒 Vendas":
        st.header("🛒 Ponto de Venda (PDV)")
        col_v, col_r = st.columns([2, 1])
        
        with col_v:
            st.subheader("Carrinho de Venda")
            cliente_v = st.selectbox("Selecione o Cliente", [c['nome_completo'] for c in clientes] if clientes else ["Consumidor Final"])
            produto_v = st.selectbox("Adicionar Produto", [f"{p['id']} - {p['descricao']} (R$ {p['preco_venda']})" for p in estoque] if estoque else ["Nenhum produto"])
            qtd = st.number_input("Quantidade", min_value=1, value=1)
            if st.button("➕ Adicionar ao Carrinho"):
                st.toast("Produto adicionado!")
        
        with col_r:
            st.subheader("Resumo")
            st.markdown('<div class="win-card">Total: <span class="metric-value">R$ 0,00</span></div>', unsafe_allow_html=True)
            vias = st.radio("Impressão", ["1 Via", "2 Vias"], index=0)
            if st.button("✅ FINALIZAR E IMPRIMIR"):
                st.success(f"Venda finalizada! Imprimindo {vias}...")

    # --- MÓDULO: ESTOQUE (FIXED) ---
    elif menu == "📦 Estoque":
        st.header("📦 Controle de Estoque")
        col_l, col_e = st.columns([2, 1])
        
        with col_l:
            if estoque:
                df_est = pd.DataFrame(estoque)
                # Tratamento para evitar erro NoneType na visualização
                df_est['preco_venda'] = df_est['preco_venda'].fillna(0.0)
                st.dataframe(df_est, use_container_width=True, hide_index=True)
            else:
                st.info("Estoque vazio.")

        with col_e:
            st.subheader("Editar/Novo")
            opcoes_p = ["Novo Registro"] + [f"{p['id']} - {p['descricao']}" for p in estoque]
            sel_p = st.selectbox("Selecione Produto", opcoes_p)
            p_edit = next((p for p in estoque if str(p['id']) in sel_p), None)
            
            with st.form("form_p"):
                desc = st.text_input("Descrição", value=p_edit['descricao'] if p_edit else "")
                ean = st.text_input("EAN13", value=p_edit['ean13'] if p_edit else "")
                pr = st.number_input("Preço", value=float(p_edit['preco_venda'] or 0.0) if p_edit else 0.0)
                if st.form_submit_button("SALVAR"):
                    pld = {"descricao": desc, "ean13": ean, "preco_venda": pr}
                    if p_edit: supabase.table("produtos").update(pld).eq("id", p_edit['id']).execute()
                    else: supabase.table("produtos").insert(pld).execute()
                    st.rerun()

    # --- MÓDULO: CLIENTES (CONSOLIDADE) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        col_cl, col_ce = st.columns([2, 1])
        with col_cl:
            if clientes: st.dataframe(pd.DataFrame(clientes), use_container_width=True, hide_index=True)
        with col_ce:
            opcoes_c = ["Novo"] + [f"{c['id']} - {c['nome_completo']}" for c in clientes]
            sel_c = st.selectbox("Editar Cliente", opcoes_c)
            c_edit = next((c for c in clientes if str(c['id']) in sel_c), None)
            with st.form("form_c"):
                nome = st.text_input("Nome", value=c_edit['nome_completo'] if c_edit else "")
                doc = st.text_input("CPF/CNPJ", value=c_edit['cpf_cnpj'] if c_edit else "")
                if st.form_submit_button("SALVAR CLIENTE"):
                    pld = {"nome_completo": nome, "cpf_cnpj": doc}
                    if c_edit: supabase.table("Clientes").update(pld).eq("id", c_edit['id']).execute()
                    else: supabase.table("Clientes").insert(pld).execute()
                    st.rerun()

    # --- AJUSTES (IDIOMA E IDENTIDADE) ---
    elif menu == "⚙️ Ajustes":
        st.header("⚙️ Configurações Globais")
        with st.form("ajustes_f"):
            c1, c2 = st.columns(2)
            nome_e = c1.text_input("Empresa", value=emp.get('nome', ''))
            logo_e = c2.text_input("URL Logo", value=emp.get('logo_base64', ''))
            idioma = st.selectbox("Idioma do Sistema", ["Português", "English"])
            if st.form_submit_button("APLICAR MUDANÇAS"):
                supabase.table("config").upsert({"id":1, "nome": nome_e, "logo_base64": logo_e}).execute()
                st.success("Configurações salvas!")
                st.rerun()

    # --- DASHBOARD ---
    elif menu == "🏠 Dashboard":
        st.header("Dashboard Operacional")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-card"><p class="metric-title">Produtos</p><p class="metric-value">{len(estoque)}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-card"><p class="metric-title">Clientes</p><p class="metric-value">{len(clientes)}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-card"><p class="metric-title">Vendas Hoje</p><p class="metric-value">0</p></div>', unsafe_allow_html=True)
