import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64

# --- CONEXÃO ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

def carregar_dados():
    try:
        # Busca Clientes usando as colunas exatas da sua foto (NOM, RUA, BAI...)
        cl = supabase.table("Clientes").select("*").order("NOM").execute().data
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'NOM', 'RUA', 'BAI', 'TEL1'])
        
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        emp = c[0] if c else {"nome": "JMQJ SGV"}
        
        return emp, df_c
    except Exception as e:
        st.error(f"Erro na sincronia: {e}")
        return {"nome": "SGV"}, pd.DataFrame()

emp, df_c = carregar_dados()

# --- ABA CLIENTES REFINADA ---
st.title(f"💼 {emp.get('nome')}")
menu = st.tabs(["👥 Relação de Clientes", "➕ Inclusão Manual"])

with menu[0]:
    if not df_c.empty:
        st.subheader("Clientes Cadastrados")
        # Exibe com nomes amigáveis na tabela
        st.dataframe(df_c.rename(columns={'NOM': 'Nome', 'RUA': 'Endereço', 'BAI': 'Bairro', 'TEL1': 'Telefone'}), 
                     use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum cliente encontrado. Faça a carga massiva.")

with menu[1]:
    with st.form("novo_cliente", clear_on_submit=True):
        st.subheader("Cadastrar Novo Cliente")
        nome = st.text_input("Nome Completo (NOM)")
        rua = st.text_input("Rua (RUA)")
        bairro = st.text_input("Bairro (BAI)")
        fone = st.text_input("Telefone (TEL1)")
        
        if st.form_submit_button("💾 SALVAR NO BANCO"):
            # IMPORTANTE: Não enviamos o ID, deixamos o banco (int8 autoincrement) gerar
            payload = {"NOM": nome, "RUA": rua, "BAI": bairro, "TEL1": fone}
            res = supabase.table("Clientes").insert(payload).execute()
            st.success("Cliente fixado com sucesso!")
            time.sleep(1)
            st.rerun()
