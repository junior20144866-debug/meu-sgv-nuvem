import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
import re

# --- 1. CONEXÃO ESTRUTURAL ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v45", layout="wide", page_icon="💼")

# --- 2. MOTOR DE TRATAMENTO AGRESSIVO (ANTI-ERRO) ---
def limpar_valor(v):
    try:
        if pd.isna(v) or str(v).strip() == "": return 0.0
        # Remove tudo que não for número, ponto ou vírgula
        s = re.sub(r'[^\d,.]', '', str(v))
        if ',' in s and '.' in s: s = s.replace('.', '').replace(',', '.')
        elif ',' in s: s = s.replace(',', '.')
        return float(s)
    except: return 0.0

def buscar_dados_reais():
    try:
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        cl = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'ean13', 'preco_venda'])
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'endereco'])
        return (c[0] if c else {}), df_p, df_c
    except: return {}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO VISUAL WINDOWS ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .win-tile { background: white; padding: 20px; border-radius: 10px; border-top: 4px solid #0078D4; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .val-m { font-size: 2.2rem; font-weight: bold; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR SISTEMA 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    # CARREGAMENTO GLOBAL DIRETO DO BANCO
    emp, df_e, df_c = buscar_dados_reais()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'JMQJ SGV'))
        menu = st.radio("MENUS", ["🏠 Dashboard", "🛒 Pedido de Venda", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Ajustes"])

    # --- ABA: IMPORTAÇÃO (CONSTRUÍDA SOBRE SEUS ARQUIVOS) ---
    if menu == "📑 Importação":
        st.header("📑 Carga Massiva (Padrão Siscom)")
        alvo = st.selectbox("Destino da Carga", ["produtos", "Clientes"])
        arq = st.file_uploader("Suba seu arquivo Excel (.xlsx)", type=["xlsx"])
        
        if arq and st.button("🚀 EXECUTAR CARGA AGORA"):
            df_in = pd.read_excel(arq)
            prog = st.progress(0)
            rows = df_in.to_dict('records')
            count = 0
            
            for i, r in enumerate(rows):
                try:
                    if alvo == "produtos":
                        # MAPEAMENTO EXATO: DESCRICAO e P_VENDA
                        nome_item = str(r.get('DESCRICAO', r.get('NOME', ''))).strip()
                        if nome_item and nome_item != 'nan':
                            pld = {
                                "descricao": nome_item,
                                "preco_venda": limpar_valor(r.get('P_VENDA', 0)),
                                "ean13": str(r.get('CODIGO', r.get('BARRA', ''))).replace('.0','')
                            }
                            supabase.table("produtos").insert(pld).execute()
                            count += 1
                    else:
                        # MAPEAMENTO EXATO CLIENTES: NOM e RUA
                        nome_cli = str(r.get('NOM', r.get('NOME', ''))).strip()
                        if nome_cli and nome_cli != 'nan':
                            pld = {
                                "nome_completo": nome_cli,
                                "cpf_cnpj": str(r.get('CGC', r.get('CPF', ''))).strip(),
                                "endereco": f"{r.get('RUA', '')}, {r.get('BAI', '')} - {r.get('CID', '')}"
                            }
                            supabase.table("Clientes").insert(pld).execute()
                            count += 1
                except: pass
                prog.progress((i + 1) / len(rows))
            st.success(f"Sucesso! {count} registros integrados."); time.sleep(1); st.rerun()

    # --- EXIBIÇÃO GARANTIDA ---
    elif menu in ["📦 Estoque", "👥 Clientes"]:
        st.header(f"Relação de {menu}")
        dados = df_e if "Estoque" in menu else df_c
        if not dados.empty:
            st.dataframe(dados, use_container_width=True, hide_index=True)
        else:
            st.warning("Nenhum dado encontrado. Realize a importação.")

    # --- DASHBOARD ---
    elif menu == "🏠 Dashboard":
        st.header(f"Centro de Comando | {emp.get('nome', 'SGV')}")
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="win-tile">ITENS NO ESTOQUE<br><span class="val-m">{len(df_e)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile">CLIENTES ATIVOS<br><span class="val-m">{len(df_c)}</span></div>', unsafe_allow_html=True)

    # --- AJUSTES E RESETS ---
    elif menu == "⚙️ Ajustes":
        st.header("⚙️ Configurações")
        with st.form("f"):
            n = st.text_input("Empresa", value=emp.get('nome', ''))
            e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logo PNG", type=["png"])
            if st.form_submit_button("💾 SALVAR"):
                l_b64 = emp.get('logo_base64', '')
                if logo: l_b64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n, "end": e, "logo_base64": l_b64}).execute(); st.rerun()
        
        st.divider()
        if st.button("🗑️ ZERAR TUDO (LIMPEZA TOTAL)"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.rerun()
