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

# --- 2. MOTOR DE RECUPERAÇÃO (MAPEAMENTO DINÂMICO DE DNA) ---
def carregar_dados_v79():
    try:
        # Busca Empresa
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        empresa = c[0] if c else {"id": 1, "nome": "JMQJ SGV", "cnpj": "", "end": ""}
        
        # Busca Produtos
        p = supabase.table("produtos").select("*").execute().data
        df_p = pd.DataFrame(p) if p else pd.DataFrame()
        
        # Busca Clientes
        cl = supabase.table("Clientes").select("*").execute().data
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame()
        
        # TRATAMENTO DE COLUNAS (O SEGREDO PARA SAIR DO ZERO)
        # Se as colunas vierem em MAIÚSCULAS do seu DBF, nós as "traduzimos"
        if not df_p.empty:
            df_p.columns = [c.upper() for c in df_p.columns]
        if not df_c.empty:
            df_c.columns = [c.upper() for c in df_c.columns]
            
        return empresa, df_p, df_c
    except:
        return {"id": 1, "nome": "SGV"}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .metric-val { font-size: 2.2rem; font-weight: 700; color: #2563EB; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.title("JMQJ SGV 🚀")
        senha = st.text_input("Acesso", type="password")
        if st.button("LIGAR"):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = carregar_dados_v79()

    with st.sidebar:
        if emp.get('logo_base64'): 
            try: st.image(emp['logo_base64'], use_container_width=True)
            except: pass
        st.subheader(emp.get('nome', 'SGV'))
        menu = st.radio("NAVEGAÇÃO", ["📊 Painel", "💰 Vendas", "📦 Estoque", "👥 Clientes", "📂 Importação", "⚙️ Ajustes"])

    # --- DASHBOARD (FIM DOS INDICADORES ZERADOS) ---
    if menu == "📊 Painel":
        st.header(f"Gestão: {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'>PRODUTOS<br><span class='metric-val'>{len(df_e)}</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'>CLIENTES<br><span class='metric-val'>{len(df_c)}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'>VENDAS HOJE<br><span class='metric-val'>0</span></div>", unsafe_allow_html=True)

    # --- ESTOQUE (MAPEAMENTO FLEXÍVEL) ---
    elif menu == "📦 Estoque":
        st.header("Estoque")
        if not df_e.empty:
            # Buscamos 'DESCRICAO' ou 'descricao' de forma inteligente
            cols = df_e.columns.tolist()
            st.dataframe(df_e, use_container_width=True, hide_index=True)
        else:
            st.info("Aguardando carga de produtos.")

    # --- CLIENTES (MAPEAMENTO FLEXÍVEL) ---
    elif menu == "👥 Clientes":
        st.header("Clientes")
        if not df_c.empty:
            st.dataframe(df_c, use_container_width=True, hide_index=True)
        else:
            st.warning("Aguardando carga de clientes.")

    # --- CARGA MASSIVA (O FIM DO GARGALO) ---
    elif menu == "📂 Importação":
        st.header("Importação Massiva")
        alvo = st.selectbox("Tabela", ["produtos", "Clientes"])
        arq = st.file_uploader("Arquivo XLSX", type=["xlsx"])
        if arq and st.button("🚀 IMPORTAR"):
            df_in = pd.read_excel(arq)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        pv = str(r.get('P_VENDA', r.get('p_venda', 0))).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({
                            "DESCRICAO": str(r.get('DESCRICAO', r.get('descricao', ''))),
                            "P_VENDA": float(pv),
                            "UNIDADE": str(r.get('UNIDADE', r.get('unidade', 'UN')))
                        }).execute()
                    else:
                        supabase.table("Clientes").insert({
                            "NOM": str(r.get('NOM', r.get('NOME', ''))),
                            "RUA": str(r.get('RUA', '')),
                            "BAI": str(r.get('BAI', '')),
                            "TEL1": str(r.get('TEL1', ''))
                        }).execute()
                except: pass
            st.success("Importação concluída!"); time.sleep(1); st.rerun()

    # --- AJUSTES (CONTROLE TOTAL) ---
    elif menu == "⚙️ Ajustes":
        st.header("Configurações")
        with st.form("f_emp"):
            n_e = st.text_input("Empresa", value=emp.get('nome', ''))
            c_e = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            e_e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logo PNG", type=["png"])
            if st.form_submit_button("💾 FIXAR DADOS"):
                l64 = emp.get('logo_base64', '')
                if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n_e, "cnpj": c_e, "end": e_e, "logo_base64": l64}).execute()
                st.success("Cravado!"); st.rerun()
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        if c1.button("ZERAR ESTOQUE", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if c2.button("ZERAR CLIENTES", use_container_width=True):
            supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if c3.button("RESET TOTAL", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
