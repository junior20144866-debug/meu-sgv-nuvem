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

st.set_page_config(page_title="JMQJ SGV v43", layout="wide", page_icon="💼")

# --- 2. MOTOR DE TRATAMENTO (DNA SISCOM) ---
def limpar_valor(v):
    try:
        if pd.isna(v) or v == "": return 0.0
        # Remove R$, pontos de milhar e ajusta vírgula
        s = str(v).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.').strip()
        return float(re.sub(r'[^0-9.]', '', s))
    except: return 0.0

def carregar_dados():
    try:
        conf = supabase.table("config").select("*").eq("id", 1).execute().data
        prod = supabase.table("produtos").select("*").order("descricao").execute().data
        clie = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        return (conf[0] if conf else {}), (prod if prod else []), (clie if clie else [])
    except: return {}, [], []

# --- 3. INTERFACE ESTILO WINDOWS ---
st.markdown("""
    <style>
    .stApp { background-color: #F0F2F5; }
    .win-tile { background: white; padding: 20px; border-radius: 8px; border-top: 5px solid #0078D4; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .val-m { font-size: 2.2rem; font-weight: bold; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("ACESSAR 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    # CARREGAMENTO GLOBAL
    emp, estoque, clientes = carregar_dados()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'SGV'))
        menu = st.radio("MENUS", ["🏠 Dashboard", "🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Ajustes"])

    # --- ABA: IMPORTAÇÃO (TOTALMENTE MAPEADA PELOS SEUS ARQUIVOS) ---
    if menu == "📑 Importação":
        st.header("📑 Carga de Dados (Padrão Siscom/FPQ)")
        alvo = st.selectbox("Escolha o destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Suba o arquivo XLSX", type=["xlsx"])
        
        if arq and st.button("🚀 EXECUTAR CARGA"):
            df = pd.read_excel(arq)
            prog = st.progress(0)
            rows = df.to_dict('records')
            
            for i, r in enumerate(rows):
                try:
                    if alvo == "produtos":
                        # MAPEAMENTO BASEADO NO SEU PRODUTOS.DBF
                        pld = {
                            "descricao": str(r.get('DESCRICAO', r.get('NOME', 'SEM NOME'))),
                            "preco_venda": limpar_valor(r.get('P_VENDA', 0)),
                            "ean13": str(r.get('BARRA', r.get('CODIGO', '')))
                        }
                    else:
                        # MAPEAMENTO BASEADO NO SEU CLIENTES.DBF
                        endereco_completo = f"{r.get('RUA', '')}, {r.get('BAI', '')} - {r.get('CID', '')}/{r.get('UF', '')}"
                        pld = {
                            "nome_completo": str(r.get('NOM', r.get('NOME', ''))),
                            "cpf_cnpj": str(r.get('CGC', r.get('CPF', ''))),
                            "endereco": endereco_completo
                        }
                    supabase.table(alvo).insert(pld).execute()
                except: pass
                prog.progress((i + 1) / len(rows))
            st.success("Carga finalizada!"); time.sleep(1); st.rerun()

    # --- EXIBIÇÃO DE ESTOQUE E CLIENTES ---
    elif menu in ["📦 Estoque", "👥 Clientes"]:
        tabela = "produtos" if menu == "📦 Estoque" else "Clientes"
        st.header(f"Relação de {tabela}")
        dados = estoque if tabela == "produtos" else clientes
        if dados:
            st.dataframe(pd.DataFrame(dados), use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum dado encontrado no banco.")

    # --- AJUSTES (CONTROLE TOTAL) ---
    elif menu == "⚙️ Ajustes":
        st.header("⚙️ Configurações e Manutenção")
        with st.form("f"):
            n = st.text_input("Nome Empresa", value=emp.get('nome', ''))
            e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logo PNG", type=["png"])
            if st.form_submit_button("💾 SALVAR"):
                l_b64 = emp.get('logo_base64', '')
                if logo: l_b64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n, "end": e, "logo_base64": l_b64}).execute()
                st.rerun()
        
        st.divider()
        if st.button("🔥 ZERAR TUDO (HARD RESET)"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute()
            st.rerun()

    # --- DASHBOARD ---
    elif menu == "🏠 Dashboard":
        st.header(f"Painel Operacional | {emp.get('nome', 'SGV')}")
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="win-tile">PRODUTOS<br><span class="val-m">{len(estoque)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile">CLIENTES<br><span class="val-m">{len(clientes)}</span></div>', unsafe_allow_html=True)
