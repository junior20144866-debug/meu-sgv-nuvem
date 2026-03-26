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

# --- 2. MOTOR DE RECUPERAÇÃO (INTELIGÊNCIA ARTIFICIAL DE MAPEAMENTO) ---
def sincronizar_v84():
    try:
        # Busca Empresa
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        empresa = c[0] if c else {"id": 1, "nome": "JMQJ SGV", "cnpj": "", "end": ""}
        
        # Busca Produtos e Clientes
        p = supabase.table("produtos").select("*").execute().data
        cl = supabase.table("Clientes").select("*").execute().data
        
        df_p = pd.DataFrame(p) if p else pd.DataFrame()
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame()
        
        # NORMALIZAÇÃO: Converte todas as colunas para MAIÚSCULAS para evitar erros de leitura
        if not df_p.empty: df_p.columns = [str(col).upper() for col in df_p.columns]
        if not df_c.empty: df_c.columns = [str(col).upper() for col in df_c.columns]
            
        return empresa, df_p, df_c
    except:
        return {"id": 1, "nome": "ERRO CONEXÃO"}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
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
    emp, df_e, df_c = sincronizar_v84()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.subheader(emp.get('nome', 'SGV'))
        menu = st.radio("NAVEGAÇÃO", ["📊 Painel", "💰 Vendas", "📦 Estoque", "👥 Clientes", "📂 Importação", "⚙️ Ajustes"])

    # --- INDICADORES (O FIM DO ZERO) ---
    if menu == "📊 Painel":
        st.header(f"Painel Operacional | {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'>PRODUTOS<br><span class='metric-val'>{len(df_e)}</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'>CLIENTES<br><span class='metric-val'>{len(df_c)}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'>VENDAS DIA<br><span class='metric-val'>0</span></div>", unsafe_allow_html=True)

    # --- ABA IMPORTAÇÃO (MAPEADOR INTELIGENTE) ---
    elif menu == "📂 Importação":
        st.header("Carga Massiva Inteligente")
        alvo = st.selectbox("Tabela", ["produtos", "Clientes"])
        arq = st.file_uploader("Arquivo XLSX", type=["xlsx"])
        if arq and st.button("🚀 INICIAR IMPORTAÇÃO"):
            df_in = pd.read_excel(arq)
            # Limpa o nome das colunas do Excel para bater com o banco
            df_in.columns = [str(c).upper().strip() for c in df_in.columns]
            
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        # Mapeia P_VENDA, PRECO ou VALOR automaticamente
                        preco = r.get('P_VENDA', r.get('PRECO', r.get('VALOR', 0)))
                        pv = str(preco).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({
                            "DESCRICAO": str(r.get('DESCRICAO', r.get('NOME', ''))),
                            "P_VENDA": float(pv),
                            "UNIDADE": str(r.get('UNIDADE', 'UN'))
                        }).execute()
                    else:
                        # Mapeia NOM ou NOME automaticamente
                        supabase.table("Clientes").insert({
                            "NOM": str(r.get('NOM', r.get('NOME', ''))),
                            "RUA": str(r.get('RUA', '')),
                            "BAI": str(r.get('BAI', '')),
                            "TEL1": str(r.get('TEL1', ''))
                        }).execute()
                except: pass
            st.success("Importação concluída! Verifique o Painel."); time.sleep(1); st.rerun()

    # --- AJUSTES (CONTROLE TOTAL) ---
    elif menu == "⚙️ Ajustes":
        st.header("Configurações")
        with st.form("f_emp"):
            n_e = st.text_input("Empresa", value=emp.get('nome', ''))
            c_e = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            if st.form_submit_button("💾 FIXAR DADOS"):
                supabase.table("config").upsert({"id": 1, "nome": n_e, "cnpj": c_e}).execute()
                st.rerun()
        
        st.divider()
        if st.button("🔥 RESET TOTAL DO SISTEMA"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.rerun()
