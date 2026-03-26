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

st.set_page_config(page_title="JMQJ SGV SaaS", layout="wide", page_icon="📈")

# --- 2. MOTOR DE RECUPERAÇÃO (ESTRUTURA DBF FORÇADA) ---
def sincronizar_universo_v77():
    try:
        # Busca Configuração
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        empresa = c[0] if c else {"id": 1, "nome": "JMQJ SGV", "cnpj": "", "end": ""}
        
        # Busca Produtos (CADASTRO.DBF -> DESCRICAO, P_VENDA, UNIDADE)
        p = supabase.table("produtos").select("*").execute().data
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'DESCRICAO', 'UNIDADE', 'P_VENDA'])
        
        # Busca Clientes (CLIENTES.DBF -> NOM, RUA, BAI, TEL1)
        cl = supabase.table("Clientes").select("*").execute().data
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'NOM', 'RUA', 'BAI', 'TEL1'])
        
        return empresa, df_p, df_c
    except Exception as e:
        st.error(f"Erro Crítico de Sincronia: {e}")
        return {"id": 1, "nome": "JMQJ SGV"}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center; }
    .metric-val { font-size: 2.2rem; font-weight: 700; color: #2563EB; }
    .paper { background: white; padding: 30px; border: 1px solid #000; font-family: monospace; color: black; line-height: 1.2; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.title("JMQJ SGV 🚀")
        senha = st.text_input("Acesso Mestre", type="password")
        if st.button("ACESSAR", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = sincronizar_universo_v77()

    with st.sidebar:
        if emp.get('logo_base64'): 
            try: st.image(emp['logo_base64'], use_container_width=True)
            except: pass
        st.title(emp.get('nome', 'SGV'))
        menu = st.radio("NAVEGAÇÃO", ["📊 Painel", "💰 Vendas", "📦 Estoque", "👥 Clientes", "📂 Carga Massiva", "⚙️ Ajustes"])

    # --- ABA: DASHBOARD ---
    if menu == "📊 Painel":
        st.header(f"Gestão: {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='card'>PRODUTOS<br><span class='metric-val'>{len(df_e)}</span></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='card'>CLIENTES<br><span class='metric-val'>{len(df_c)}</span></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='card'>VENDAS HOJE<br><span class='metric-val'>0</span></div>", unsafe_allow_html=True)

    # --- ABA: ESTOQUE (PRODUTOS - FIM DA PÁGINA EM BRANCO) ---
    elif menu == "📦 Estoque":
        st.header("📦 Relação de Itens")
        if not df_e.empty:
            # Selecionamos apenas colunas que temos certeza que existem no banco (MAIÚSCULAS)
            cols_show = [c for c in ['DESCRICAO', 'UNIDADE', 'P_VENDA'] if c in df_e.columns]
            st.dataframe(df_e[cols_show], use_container_width=True, hide_index=True)
        else:
            st.info("Estoque vazio. Vá em 'Carga Massiva'.")

    # --- ABA: CLIENTES (NOM, RUA, BAI) ---
    elif menu == "👥 Clientes":
        st.header("👥 Base de Clientes")
        if not df_c.empty:
            cols_cli = [c for c in ['NOM', 'RUA', 'BAI', 'TEL1'] if c in df_c.columns]
            st.dataframe(df_c[cols_cli], use_container_width=True, hide_index=True)
        else:
            st.warning("Lista de clientes vazia.")

    # --- ABA: AJUSTES (CONTROLE TOTAL) ---
    elif menu == "⚙️ Ajustes":
        st.header("⚙️ Configurações")
        with st.form("f_emp"):
            n_e = st.text_input("Nome da Empresa", value=emp.get('nome', ''))
            c_e = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            e_e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logo PNG", type=["png"])
            if st.form_submit_button("💾 SALVAR DADOS"):
                l64 = emp.get('logo_base64', '')
                if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n_e, "cnpj": c_e, "end": e_e, "logo_base64": l64}).execute()
                st.success("Dados fixados!"); st.rerun()
        
        st.divider()
        st.subheader("🗑️ ZONA DE RESET")
        cr1, cr2, cr3 = st.columns(3)
        if cr1.button("ZERAR ESTOQUE", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if cr2.button("ZERAR CLIENTES", use_container_width=True):
            supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if cr3.button("RESET TOTAL", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()

    # --- ABA: CARGA MASSIVA (MAPEAMENTO MAIÚSCULO) ---
    elif menu == "📂 Carga Massiva":
        st.header("📑 Importação XLSX")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Subir arquivo", type=["xlsx"])
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
