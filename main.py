import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

# --- 2. CSS: INTERFACE DINÂMICA (MODO CLARO) ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .win-tile {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 5px solid #0078D4;
        text-align: center; cursor: pointer; transition: 0.3s;
    }
    .win-tile:hover { transform: scale(1.02); box-shadow: 0 6px 15px rgba(0,0,0,0.1); }
    .tile-num { font-size: 2.2rem; font-weight: 800; color: #0078D4; }
    .tile-txt { font-weight: bold; color: #555; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CÉREBRO DE DADOS (ANTI-SANFONA) ---
def get_count(table):
    try:
        res = supabase.table(table).select("id", count="exact").execute()
        return res.count if res.count else 0
    except: return 0

def carregar_empresa():
    res = supabase.table("config").select("*").eq("id", 1).execute()
    return res.data[0] if res.data else {}

# --- 4. CONTROLE DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.text_input("Senha Mestra", type="password") == "Naksu@6026":
            if st.button("LIGAR MOTORES", use_container_width=True): 
                st.session_state.auth = True
                st.rerun()
else:
    # Sidebar com Logomarca e Identidade Fixa
    emp = carregar_empresa()
    with st.sidebar:
        st.title(emp.get('nome', 'JMQJ SGV'))
        menu = st.radio("SISTEMAS", ["🏠 Dashboard", "🛒 Vendas (PDV)", "📦 Estoque", "👥 Clientes", "📑 Importação", "📊 Relatórios", "⚙️ Configurações"])

    # --- ABA: DASHBOARD (JANELAS COM DADOS REAIS) ---
    if menu == "🏠 Dashboard":
        st.header(f"Bem-vindo à {emp.get('nome', 'sua Central de Gestão')}")
        c1, c2, c3, c4 = st.columns(4)
        
        c1.markdown(f'<div class="win-tile"><p class="tile-txt">📦 Produtos</p><p class="tile-num">{get_count("produtos")}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile"><p class="tile-txt">👥 Clientes</p><p class="tile-num">{get_count("Clientes")}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile"><p class="tile-txt">💰 Vendas/Hoje</p><p class="tile-num">R$ 0</p></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="win-tile"><p class="tile-txt">📈 Status</p><p class="tile-num" style="color:green">ON</p></div>', unsafe_allow_html=True)

    # --- ABA: VENDAS (PDV COM CONTROLE TOTAL) ---
    elif menu == "🛒 Vendas (PDV)":
        st.header("🛒 Ponto de Venda")
        col_p1, col_p2 = st.columns([2, 1])
        with col_p1:
            busca = st.text_input("🔍 Buscar Produto por Descrição ou EAN")
            if busca:
                prods = supabase.table("produtos").select("*").ilike("descricao", f"%{busca}%").execute().data
                if prods:
                    for p in prods:
                        cp1, cp2, cp3 = st.columns([3, 1, 1])
                        cp1.write(f"**{p['descricao']}**")
                        cp2.write(f"R$ {p['preco_venda']}")
                        if cp3.button("➕", key=f"add_{p['id']}"): st.toast("No carrinho!")
                else: st.warning("Produto não encontrado.")
        with col_p2:
            st.subheader("Checkout Carrinho")
            st.divider()
            st.markdown("## Total: R$ 0,00")
            st.button("FINALIZAR VENDA", type="primary", use_container_width=True)

    # --- ABA: CONFIGURAÇÕES (O CORAÇÃO DA PERSISTÊNCIA) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Ajustes do Sistema")
        with st.form("perfil_empresa"):
            st.subheader("🏢 Identidade da JMQJ SGV")
            n_f = st.text_input("Razão Social/Nome", value=emp.get('nome', ''))
            c_f = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            e_f = st.text_input("Endereço Completo", value=emp.get('end', ''))
            if st.form_submit_button("💾 SALVAR E TRAVAR DADOS"):
                supabase.table("config").upsert({"id": 1, "nome": n_f, "cnpj": c_f, "end": e_f}).execute()
                st.success("Dados salvos no banco de dados!"); time.sleep(1); st.rerun()
        
        st.divider()
        st.subheader("🧹 Central de Limpeza (Zerar Dados)")
        cz1, cz2, cz3 = st.columns(3)
        if cz1.button("🗑️ Zerar Clientes"): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if cz2.button("🗑️ Zerar Estoque"): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if cz3.button("🔥 ZERAR TUDO"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.rerun()

    # --- ABA: IMPORTAÇÃO (MOTOR INTELIGENTE) ---
    elif menu == "📑 Importação":
        st.header("📑 Carga de Dados Inteligente")
        target = st.selectbox("Para qual tabela?", ["produtos", "Clientes"])
        file = st.file_uploader("Suba sua planilha (XLSX)", type=["xlsx"])
        if file:
            df = pd.read_excel(file)
            st.write("Detectamos estas colunas:", df.columns.tolist())
            if st.button("🚀 PROCESSAR E INSERIR"):
                # Mapeamento automático inteligente
                for _, row in df.iterrows():
                    d = row.to_dict()
                    # Tradução automática simples
                    map_cli = {"NOM": "nome_completo", "CGC": "cpf_cnpj", "RUA": "endereco", "BAI": "bairro", "CID": "cidade"}
                    map_prod = {"DESCRICAO": "descricao", "CODIGO": "ean13", "P_VENDA": "preco_venda", "UNIDADE": "unidade"}
                    final_data = {}
                    mapping = map_cli if target == "Clientes" else map_prod
                    for k, v in mapping.items():
                        if k in d: final_data[v] = d[k]
                    if final_data: supabase.table(target).insert(final_data).execute()
                st.success("Importação concluída com sucesso!"); st.rerun()
