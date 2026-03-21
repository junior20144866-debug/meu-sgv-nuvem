import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
import re

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v41", layout="wide", page_icon="💼")

# --- 2. TRATAMENTO DE DADOS (DNA SISCOM) ---
def limpar_preco(valor):
    try:
        if pd.isna(valor): return 0.0
        s = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(re.sub(r'[^0-9.]', '', s))
    except: return 0.0

def buscar_dados():
    try:
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        cl = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'ean13', 'preco_venda'])
        df_p['preco_venda'] = pd.to_numeric(df_p['preco_venda'], errors='coerce').fillna(0.0)
        
        df_cl = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'endereco'])
        return (c[0] if c else {}), df_p, df_cl
    except: return {}, pd.DataFrame(), pd.DataFrame()

# --- 3. INTERFACE ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .win-tile { background: white; padding: 20px; border-radius: 8px; border-top: 4px solid #0078D4; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = buscar_dados()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'SGV'))
        menu = st.radio("MÓDULOS", ["🏠 Dashboard", "🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Ajustes"])

    # --- IMPORTAÇÃO (MAPEADA PELO SEU DBF) ---
    if menu == "📑 Importação":
        st.header("📑 Importação Inteligente (Padrão Siscom)")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Suba o ficheiro XLSX", type=["xlsx"])
        
        if arq and st.button("🚀 EXECUTAR CARGA"):
            df_in = pd.read_excel(arq)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        # Usa os nomes de colunas que vimos no seu ficheiro original
                        pld = {
                            "descricao": str(r.get('DESCRICAO', r.get('NOME', ''))),
                            "preco_venda": limpar_preco(r.get('P_VENDA', 0)),
                            "ean13": str(r.get('CODIGO', r.get('BARRA', '')))
                        }
                    else:
                        pld = {
                            "nome_completo": str(r.get('NOM', r.get('NOME', ''))),
                            "cpf_cnpj": str(r.get('CGC', r.get('CPF', ''))),
                            "endereco": f"{r.get('RUA', '')}, {r.get('BAI', '')} - {r.get('CID', '')}"
                        }
                    supabase.table(alvo).insert(pld).execute()
                except: pass
            st.success("Carga finalizada com sucesso!"); time.sleep(1); st.rerun()

    # --- ESTOQUE E CLIENTES (VISUALIZAÇÃO BLINDADA) ---
    elif menu in ["📦 Estoque", "👥 Clientes"]:
        tab = menu.replace("📦 ", "").replace("👥 ", "")
        st.header(f"Relação de {tab}")
        df_show = df_e if tab == "Estoque" else df_c
        if not df_show.empty:
            st.dataframe(df_show, use_container_width=True, hide_index=True)
        else:
            st.info(f"A tabela de {tab} está vazia no banco de dados.")

    # --- AJUSTES (CONTROLES REPOSTOS) ---
    elif menu == "⚙️ Ajustes":
        st.header("⚙️ Configurações")
        with st.form("f"):
            n = st.text_input("Empresa", value=emp.get('nome', ''))
            e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logo", type=["png"])
            if st.form_submit_button("💾 SALVAR"):
                l_b64 = emp.get('logo_base64', '')
                if logo: l_b64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n, "end": e, "logo_base64": l_b64}).execute(); st.rerun()
        
        st.divider()
        if st.button("🔥 ZERAR TUDO (HARD RESET)"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute()
            st.rerun()
