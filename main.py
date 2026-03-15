import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. NÚCLEO DE CONEXÃO E PERSISTÊNCIA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide", initial_sidebar_state="expanded")

# --- 2. ESTILO WINDOWS MODERNO (POLIMENTO PREMIUM) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FB; }
    .main-header { color: #0078D4; font-weight: 800; text-align: center; padding: 10px; }
    .win-tile {
        background: white; border-radius: 12px; padding: 25px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05); border-top: 5px solid #0078D4;
        text-align: center; transition: 0.3s;
    }
    .win-tile:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
    .tile-val { font-size: 2.2rem; font-weight: 900; color: #0078D4; margin: 0; }
    .tile-lab { font-size: 0.9rem; font-weight: bold; color: #666; text-transform: uppercase; }
    /* Botões Padrão Windows */
    .stButton>button { width: 100%; border-radius: 6px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES OPERACIONAIS (ANTI-FALHAS) ---
def carregar_dados(tabela):
    try:
        res = supabase.table(tabela).select("*").execute()
        return res.data if res.data else []
    except: return []

def salvar_config(dados):
    try:
        supabase.table("config").upsert({"id": 1, **dados}).execute()
        st.cache_data.clear()
        return True
    except: return False

# --- 4. MOTOR DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 class='main-header'>JMQJ SGV SISTEMAS</h1>", unsafe_allow_html=True)
    with st.container():
        _, col2, _ = st.columns([1,1,1])
        with col2:
            st.markdown("<div style='background:white; padding:30px; border-radius:15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1)'>", unsafe_allow_html=True)
            senha = st.text_input("Chave Mestra de Ativação", type="password")
            if st.button("LIGAR MOTORES 🚀"):
                if senha == "Naksu@6026":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Chave inválida.")
            st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- SISTEMA LIGADO - INTERFACE POLIDA ---
    conf = carregar_dados("config")
    dados_empresa = conf[0] if conf else {}
    
    with st.sidebar:
        st.title(dados_empresa.get('nome', 'JMQJ SGV'))
        st.write("---")
        menu = st.radio("SISTEMAS", 
            ["🏠 Janelas (Dashboard)", "🛒 Vendas (PDV)", "📦 Estoque", "👥 Clientes", "📑 Importação em Massa", "💰 Financeiro", "⚙️ Configurações"])

    # --- SESSÃO: JANELAS (DASHBOARD) ---
    if menu == "🏠 Janelas (Dashboard)":
        st.header("Centro de Comando JMQJ")
        prods = carregar_dados("produtos")
        clis = carregar_dados("Clientes")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="win-tile"><p class="tile-lab">📦 Estoque</p><p class="tile-val">{len(prods)}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile"><p class="tile-lab">👥 Clientes</p><p class="tile-val">{len(clis)}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile"><p class="tile-lab">💰 Vendas</p><p class="tile-val">0</p></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="win-tile"><p class="tile-lab">📉 Financeiro</p><p class="tile-val">R$ 0</p></div>', unsafe_allow_html=True)

    # --- SESSÃO: VENDAS (PDV POLIDO) ---
    elif menu == "🛒 Vendas (PDV)":
        st.header("🛒 Ponto de Venda")
        col1, col2 = st.columns([2,1])
        with col1:
            busca = st.text_input("🔍 Buscar Produto por Nome, EAN ou Código")
            if busca:
                estoque = carregar_dados("produtos")
                filtrados = [p for p in estoque if busca.lower() in str(p.get('descricao', '')).lower() or busca in str(p.get('ean13', ''))]
                for p in filtrados:
                    with st.container():
                        st.markdown(f"**{p['descricao']}** | {p['unidade']} | R$ {p['preco_venda']}")
                        if st.button(f"Adicionar", key=f"add_{p['id']}"): st.toast("Item adicionado!")
        with col2:
            st.markdown("<div style='background:#fff; padding:15px; border-radius:10px'><h3>Carrinho</h3><hr><b>Total: R$ 0,00</b></div>", unsafe_allow_html=True)
            st.button("FINALIZAR VENDA", type="primary")

    # --- SESSÃO: ESTOQUE & CLIENTES (CONTROLE TOTAL) ---
    elif menu in ["📦 Estoque", "👥 Clientes"]:
        tab = "produtos" if menu == "📦 Estoque" else "Clientes"
        st.header(f"{menu} - Controle Total")
        
        with st.expander("➕ Inclusão Manual"):
            with st.form("manual_form"):
                if tab == "produtos":
                    d, e, u = st.text_input("Descrição"), st.text_input("EAN"), st.text_input("Unidade")
                    pv = st.number_input("Preço de Venda")
                    payload = {"descricao": d, "ean13": e, "unidade": u, "preco_venda": pv}
                else:
                    n, doc, end = st.text_input("Nome"), st.text_input("CPF/CNPJ"), st.text_input("Endereço Completo")
                    payload = {"nome_completo": n, "cpf_cnpj": doc, "endereco": end}
                
                if st.form_submit_button("SALVAR DADOS"):
                    supabase.table(tab).insert(payload).execute()
                    st.rerun()

        dados = carregar_dados(tab)
        if dados:
            st.dataframe(pd.DataFrame(dados), use_container_width=True)
            if st.button(f"🗑️ ZERAR {menu.upper()}"):
                supabase.table(tab).delete().neq("id", -1).execute()
                st.rerun()

    # --- SESSÃO: CONFIGURAÇÕES (PRESERVAÇÃO) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Configurações de Identidade")
        with st.form("config_form"):
            n = st.text_input("Nome da Empresa", value=dados_empresa.get('nome', ''))
            c = st.text_input("CNPJ", value=dados_empresa.get('cnpj', ''))
            e = st.text_input("Endereço", value=dados_empresa.get('end', ''))
            if st.form_submit_button("💾 SALVAR E FIXAR"):
                salvar_config({"nome": n, "cnpj": c, "end": e})
                st.success("Dados fixados no banco de dados!")
                st.rerun()

    # --- SESSÃO: IMPORTAÇÃO (MOTOR INTELIGENTE) ---
    elif menu == "📑 Importação em Massa":
        st.header("📑 Importação de Planilhas Bagunçadas")
        dest = st.selectbox("Destino", ["produtos", "Clientes"])
        file = st.file_uploader("Suba o arquivo XLSX", type=["xlsx"])
        if file and st.button("🚀 PROCESSAR CARGA"):
            df = pd.read_excel(file)
            for _, row in df.iterrows():
                d = row.to_dict()
                ready = {"descricao": d.get('DESCRICAO'), "preco_venda": d.get('P_VENDA'), "ean13": d.get('CODIGO')} if dest == "produtos" else {"nome_completo": d.get('NOM'), "cpf_cnpj": d.get('CGC'), "endereco": d.get('RUA')}
                if any(ready.values()): supabase.table(dest).insert(ready).execute()
            st.success("Importação concluída!")
            st.rerun()
