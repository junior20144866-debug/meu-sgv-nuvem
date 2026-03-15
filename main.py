import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO DIRETA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

# --- 2. ESTILO WINDOWS (CLARO E DIRETO) ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F5; }
    .tile {
        background: white; border-radius: 10px; padding: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 8px solid #0078D4;
        text-align: center; margin-bottom: 20px;
    }
    .tile-h { font-size: 1rem; color: #555; font-weight: bold; margin-bottom: 5px; }
    .tile-v { font-size: 2.5rem; font-weight: 800; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES DE OPERAÇÃO BRUTA ---
def db_query(table):
    try:
        return supabase.table(table).select("*").execute().data
    except:
        return []

def carregar_config():
    try:
        res = supabase.table("config").select("*").eq("id", 1).execute()
        return res.data[0] if res.data else {}
    except:
        return {}

# --- 4. SISTEMA DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        pin = st.text_input("Senha do Sistema", type="password")
        if st.button("LIGAR MOTORES", use_container_width=True):
            if pin == "Naksu@6026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Chave incorreta")
else:
    # Sidebar com Nome da Empresa (Persistente)
    empresa = carregar_config()
    st.sidebar.title(empresa.get('nome', 'JMQJ SGV'))
    menu = st.sidebar.radio("Navegação", ["🏠 Janelas", "🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Configurações"])

    # --- PÁGINA: JANELAS (DASHBOARD) ---
    if menu == "🏠 Janelas":
        st.header(f"Painel Operacional - {empresa.get('nome', 'SGV')}")
        
        # Sincronização em Tempo Real
        p_count = len(db_query("produtos"))
        c_count = len(db_query("Clientes"))
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="tile"><p class="tile-h">ESTOQUE</p><p class="tile-v">{p_count}</p></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="tile"><p class="tile-h">CLIENTES</p><p class="tile-v">{c_count}</p></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="tile"><p class="tile-h">VENDAS/MÊS</p><p class="tile-v">0</p></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="tile"><p class="tile-h">SISTEMA</p><p class="tile-v" style="color:#28a745">OK</p></div>', unsafe_allow_html=True)

    # --- PÁGINA: ESTOQUE (CONTROLE TOTAL) ---
    elif menu == "📦 Estoque":
        st.header("📦 Gestão de Produtos")
        
        # Cadastro Manual Completo
        with st.expander("➕ Novo Produto"):
            with st.form("add_p"):
                f1, f2, f3 = st.columns([3, 1, 1])
                d = f1.text_input("Descrição")
                e = f2.text_input("EAN/Código")
                u = f3.text_input("Unidade (UN/KG)")
                p = st.number_input("Preço de Venda", min_value=0.0)
                if st.form_submit_button("CADASTRAR"):
                    supabase.table("produtos").insert({"descricao": d, "ean13": e, "unidade": u, "preco_venda": p}).execute()
                    st.rerun()
        
        # Tabela de Visualização e Controle
        prods = db_query("produtos")
        if prods:
            df = pd.DataFrame(prods)
            st.dataframe(df, use_container_width=True)
            if st.button("🗑️ ZERAR ESTOQUE TOTAL"):
                supabase.table("produtos").delete().neq("id", -1).execute()
                st.rerun()
        else: st.info("Estoque vazio.")

    # --- PÁGINA: CLIENTES (CONTROLE TOTAL) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        with st.expander("➕ Inserir Cliente Manual"):
            with st.form("add_c"):
                n = st.text_input("Nome Completo")
                doc = st.text_input("CPF/CNPJ")
                end = st.text_input("Endereço/Bairro/Cidade")
                if st.form_submit_button("SALVAR"):
                    supabase.table("Clientes").insert({"nome_completo": n, "cpf_cnpj": doc, "endereco": end}).execute()
                    st.rerun()
        
        clis = db_query("Clientes")
        if clis:
            st.dataframe(pd.DataFrame(clis), use_container_width=True)
            if st.button("🗑️ ZERAR BASE DE CLIENTES"):
                supabase.table("Clientes").delete().neq("id", -1).execute()
                st.rerun()

    # --- PÁGINA: CONFIGURAÇÕES (BLINDAGEM) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Dados da Empresa")
        with st.form("cfg"):
            n_emp = st.text_input("Nome Fantasia", value=empresa.get('nome', ''))
            c_emp = st.text_input("CNPJ", value=empresa.get('cnpj', ''))
            e_emp = st.text_input("Endereço", value=empresa.get('end', ''))
            if st.form_submit_button("💾 FIXAR DADOS NO BANCO"):
                supabase.table("config").upsert({"id": 1, "nome": n_emp, "cnpj": c_emp, "end": e_emp}).execute()
                st.success("Configurações salvas permanentemente!")
                st.rerun()

    # --- PÁGINA: IMPORTAÇÃO (CONQUISTA REPOSTA) ---
    elif menu == "📑 Importação":
        st.header("📑 Importação em Massa")
        target = st.selectbox("Importar para:", ["produtos", "Clientes"])
        file = st.file_uploader("Selecione o arquivo Excel", type=["xlsx"])
        if file and st.button("🚀 PROCESSAR"):
            df = pd.read_excel(file)
            for _, row in df.iterrows():
                d = row.to_dict()
                # Tradução inteligente de colunas
                if target == "produtos":
                    ready = {"descricao": d.get('DESCRICAO'), "preco_venda": d.get('P_VENDA'), "ean13": d.get('CODIGO')}
                else:
                    ready = {"nome_completo": d.get('NOM'), "cpf_cnpj": d.get('CGC'), "endereco": d.get('RUA')}
                
                if any(ready.values()):
                    supabase.table(target).insert(ready).execute()
            st.success("Dados inseridos com sucesso!")
            st.rerun()
