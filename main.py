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

st.set_page_config(page_title="JMQJ SGV v85", layout="wide", page_icon="🎯")

# --- 2. MOTOR DE TRADUÇÃO (O TRADUTOR DA BÚSSOLA) ---
def normalizar_colunas(df):
    """ Converte qualquer variação de nome para o padrão da Bússola (MAIÚSCULAS) """
    mapeamento = {
        'NOME': 'NOM', 'CLIENTE': 'NOM', 'RAZAO': 'NOM',
        'PRECO': 'P_VENDA', 'VALOR': 'P_VENDA', 'VENDA': 'P_VENDA',
        'PRODUTO': 'DESCRICAO', 'ITEM': 'DESCRICAO'
    }
    df.columns = [c.upper().strip() for c in df.columns]
    df.rename(columns=mapeamento, inplace=True)
    return df

def carregar_universo_v85():
    try:
        emp = supabase.table("config").select("*").eq("id", 1).execute().data
        p = supabase.table("produtos").select("*").execute().data
        cl = supabase.table("Clientes").select("*").execute().data
        
        df_p = pd.DataFrame(p) if p else pd.DataFrame()
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame()
        
        # Garante que o Python enxergue as colunas em MAIÚSCULAS vindo do banco
        if not df_p.empty: df_p.columns = [c.upper() for c in df_p.columns]
        if not df_c.empty: df_c.columns = [c.upper() for c in df_c.columns]
            
        return (emp[0] if emp else {"id":1, "nome":"SGV"}), df_p, df_c
    except:
        return {"id":1, "nome":"SGV"}, pd.DataFrame(), pd.DataFrame()

# --- 3. INTERFACE OPERACIONAL ---
emp, df_e, df_c = carregar_universo_v85()

with st.sidebar:
    if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
    st.title(emp.get('nome', 'SGV'))
    menu = st.radio("NAVEGAÇÃO", ["📊 Dashboard", "💰 Vendas & O.S", "📦 Estoque", "👥 Clientes", "📂 Carga Massiva", "⚙️ Ajustes"])

# --- DASHBOARD (INDICADORES REAIS) ---
if menu == "📊 Dashboard":
    st.header(f"Gestão: {emp.get('nome')}")
    c1, c2, c3 = st.columns(3)
    c1.metric("PRODUTOS", len(df_e))
    c2.metric("CLIENTES", len(df_c))
    c3.metric("VENDAS DIA", 0)

# --- CARGA MASSIVA (O MOTOR DE TRADUÇÃO EM AÇÃO) ---
elif menu == "📂 Carga Massiva":
    st.header("📂 Importação de Dados da Bússola")
    alvo = st.selectbox("Escolha a Tabela", ["Produtos", "Clientes"])
    arquivo = st.file_uploader("Suba seu Excel (.xlsx)", type=["xlsx"])
    
    if arquivo:
        df_temp = pd.read_excel(arquivo)
        df_temp = normalizar_colunas(df_temp)
        
        st.subheader("Prévia dos Dados (Como o sistema vai ler):")
        st.dataframe(df_temp.head(3))
        
        if st.button("🚀 CONFIRMAR E GRAVAR NO BANCO"):
            progresso = st.progress(0)
            linhas = df_temp.to_dict('records')
            for i, r in enumerate(linhas):
                try:
                    if alvo == "Produtos":
                        p_v = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({
                            "DESCRICAO": str(r.get('DESCRICAO', '')),
                            "P_VENDA": float(p_v), "UNIDADE": str(r.get('UNIDADE', 'UN'))
                        }).execute()
                    else:
                        supabase.table("Clientes").insert({
                            "NOM": str(r.get('NOM', '')), "RUA": str(r.get('RUA', '')),
                            "BAI": str(r.get('BAI', '')), "TEL1": str(r.get('TEL1', ''))
                        }).execute()
                except: pass
                progresso.progress((i + 1) / len(linhas))
            st.success("Carga realizada! Os indicadores vão 'acordar' agora.")
            time.sleep(1); st.rerun()

# --- VENDAS (ROBUSTEZ SAAS) ---
elif menu == "💰 Vendas & O.S":
    st.header("Lançamento de Pedidos")
    if df_e.empty or df_c.empty:
        st.error("⚠️ ERRO: Dashboard zerada. Importe dados antes de vender.")
    else:
        with st.form("venda_os"):
            col_cli = "NOM" if "NOM" in df_c.columns else df_c.columns[0]
            st.selectbox("Cliente", df_c[col_cli].tolist())
            st.selectbox("Item", df_e['DESCRICAO'].tolist())
            st.number_input("Qtd", min_value=1)
            st.form_submit_button("GERAR PEDIDO")

# --- AJUSTES (CONTROLE DE RESET) ---
elif menu == "⚙️ Ajustes":
    st.header("Controle de Sistema")
    with st.form("ajuste_emp"):
        n = st.text_input("Empresa", value=emp.get('nome',''))
        if st.form_submit_button("FIXAR EMPRESA"):
            supabase.table("config").upsert({"id": 1, "nome": n}).execute()
            st.rerun()
    st.divider()
    if st.button("🔥 RESET TOTAL (LIMPAR TUDO)"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        st.rerun()
