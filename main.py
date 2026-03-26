import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
from datetime import datetime, timedelta

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SaaS", layout="wide", page_icon="🎯")

# --- 2. MOTOR DE RECUPERAÇÃO (TRADUTOR DE DNA) ---
def sincronizar_v82():
    try:
        # Busca Empresa (DADOS.DBF)
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        empresa = c[0] if c else {"id": 1, "nome": "JMQJ SGV", "cnpj": "", "end": ""}
        
        # Busca Produtos (CADASTRO.DBF)
        p = supabase.table("produtos").select("*").execute().data
        df_p = pd.DataFrame(p) if p else pd.DataFrame()
        
        # Busca Clientes (CLIENTES.DBF)
        cl = supabase.table("Clientes").select("*").execute().data
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame()
        
        # TRADUTOR: Se os dados vierem do banco em qualquer formato, 
        # forçamos as colunas para MAIÚSCULAS para o código não se perder.
        if not df_p.empty: df_p.columns = [c.upper() for c in df_p.columns]
        if not df_c.empty: df_c.columns = [c.upper() for c in df_c.columns]
            
        return empresa, df_p, df_c
    except Exception as e:
        return {"id": 1, "nome": "ERRO CONEXÃO"}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO VISUAL SAAS ---
st.markdown("""
    <style>
    .stApp { background-color: #F9FAFB; }
    .card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center; }
    .metric-val { font-size: 2.3rem; font-weight: 700; color: #2563EB; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.title("JMQJ SGV 🚀")
        senha = st.text_input("Senha", type="password")
        if st.button("LIGAR"):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = sincronizar_v82()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.subheader(emp.get('nome', 'SGV'))
        menu = st.radio("NAVEGAÇÃO", ["📊 Painel", "💰 Vendas", "📦 Estoque", "👥 Clientes", "📂 Importação", "⚙️ Ajustes"])

    # --- INDICADORES (FIM DO ZERO A ZERO) ---
    if menu == "📊 Painel":
        st.header(f"Gestão Operacional | {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'>PRODUTOS<br><span class='metric-val'>{len(df_e)}</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'>CLIENTES<br><span class='metric-val'>{len(df_c)}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'>VENDAS DIA<br><span class='metric-val'>0</span></div>", unsafe_allow_html=True)

    # --- ESTOQUE E CLIENTES (AUTO-DETECÇÃO) ---
    elif menu == "📦 Estoque":
        st.header("Estoque")
        if not df_e.empty: st.dataframe(df_e, use_container_width=True, hide_index=True)
        else: st.info("Lista de produtos vazia no banco.")

    elif menu == "👥 Clientes":
        st.header("Clientes")
        if not df_c.empty: st.dataframe(df_c, use_container_width=True, hide_index=True)
        else: st.info("Lista de clientes vazia no banco.")

    # --- VENDAS (PROTEÇÃO CONTRA PÁGINA BRANCA) ---
    elif menu == "💰 Vendas":
        st.header("Lançamento de Vendas")
        if df_e.empty or df_c.empty:
            st.error("ERRO: É necessário importar Clientes e Produtos antes de lançar vendas.")
        else:
            st.success("Módulo de Vendas ativo.")

    # --- IMPORTAÇÃO (MAPEADOR INTELIGENTE) ---
    elif menu == "📂 Importação":
        st.header("Importação Massiva")
        alvo = st.selectbox("Tabela", ["produtos", "Clientes"])
        arq = st.file_uploader("Arquivo XLSX", type=["xlsx"])
        if arq and st.button("🚀 IMPORTAR"):
            df_in = pd.read_excel(arq)
            # Normalizamos o seu Excel para MAIÚSCULAS antes de enviar
            df_in.columns = [str(c).upper().strip() for c in df_in.columns]
            
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        pv = str(r.get('P_VENDA', r.get('PRECO', 0))).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({
                            "DESCRICAO": str(r.get('DESCRICAO', r.get('NOME', ''))),
                            "P_VENDA": float(pv),
                            "UNIDADE": str(r.get('UNIDADE', 'PC'))
                        }).execute()
                    else:
                        supabase.table("Clientes").insert({
                            "NOM": str(r.get('NOM', r.get('NOME', ''))),
                            "RUA": str(r.get('RUA', '')), "BAI": str(r.get('BAI', '')),
                            "TEL1": str(r.get('TEL1', ''))
                        }).execute()
                except: pass
            st.success("Carga concluída!"); time.sleep(1); st.rerun()

    # --- AJUSTES (CONTROLE TOTAL) ---
    elif menu == "⚙️ Ajustes":
        st.header("Ajustes")
        with st.form("f_emp"):
            nome_e = st.text_input("Empresa", value=emp.get('nome', ''))
            cnpj_e = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            logo = st.file_uploader("Logo PNG", type=["png"])
            if st.form_submit_button("💾 FIXAR DADOS"):
                l64 = emp.get('logo_base64', '')
                if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": nome_e, "cnpj": cnpj_e, "logo_base64": l64}).execute()
                st.rerun()
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        if c1.button("ZERAR ESTOQUE", use_container_width=True): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if c2.button("ZERAR CLIENTES", use_container_width=True): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if c3.button("RESET TOTAL", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
