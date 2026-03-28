import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64

# --- CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v87", layout="wide")

def carregar_dados():
    try:
        emp = supabase.table("config").select("*").eq("id", 1).execute().data[0]
        prod = supabase.table("produtos").select("*").execute().data
        clie = supabase.table("Clientes").select("*").execute().data
        
        # O segredo: Converter tudo para DataFrame e normalizar colunas para MAIÚSCULAS
        df_p = pd.DataFrame(prod) if prod else pd.DataFrame()
        df_c = pd.DataFrame(clie) if clie else pd.DataFrame()
        
        if not df_p.empty: df_p.columns = [c.upper() for c in df_p.columns]
        if not df_c.empty: df_c.columns = [c.upper() for c in df_c.columns]
            
        return emp, df_p, df_c
    except:
        return {"nome": "SGV"}, pd.DataFrame(), pd.DataFrame()

emp, df_p, df_c = carregar_dados()

# --- INTERFACE ---
st.title(f"🚀 {emp.get('nome')}")

menu = st.tabs(["📊 Painel", "👥 Clientes", "📦 Estoque", "📂 Carga Massiva", "⚙️ Ajustes"])

with menu[0]:
    c1, c2 = st.columns(2)
    c1.metric("CLIENTES NA BASE", len(df_c))
    c2.metric("ITENS NO ESTOQUE", len(df_p))

with menu[1]:
    if not df_c.empty: st.dataframe(df_c, use_container_width=True, hide_index=True)
    else: st.info("Lista de clientes vazia no banco.")

with menu[2]:
    if not df_p.empty: st.dataframe(df_p, use_container_width=True, hide_index=True)
    else: st.info("Lista de estoque vazia no banco.")

with menu[3]:
    st.subheader("Importação Inteligente")
    alvo = st.selectbox("Destino", ["produtos", "Clientes"])
    arquivo = st.file_uploader("Suba o Excel extraído da bússola", type=["xlsx"])
    if arquivo and st.button("CONFIRMAR CARGA"):
        df_in = pd.read_excel(arquivo)
        # Normaliza o Excel para bater com o banco (NOM, P_VENDA, DESCRICAO)
        df_in.columns = [str(c).upper().strip() for c in df_in.columns]
        for r in df_in.to_dict('records'):
            try:
                if alvo == "produtos":
                    supabase.table("produtos").insert({
                        "DESCRICAO": str(r.get('DESCRICAO', r.get('DESC', ''))),
                        "P_VENDA": float(str(r.get('P_VENDA', 0)).replace(',','.')),
                        "UNIDADE": str(r.get('UNIDADE', 'UN'))
                    }).execute()
                else:
                    supabase.table("Clientes").insert({
                        "NOM": str(r.get('NOM', r.get('NOME', ''))),
                        "RUA": str(r.get('RUA', '')),
                        "BAI": str(r.get('BAI', ''))
                    }).execute()
            except: pass
        st.success("Importação concluída! Verifique o Painel.")
        time.sleep(1); st.rerun()

with menu[4]:
    if st.button("🔥 RESET TOTAL DO BANCO"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        st.rerun()
