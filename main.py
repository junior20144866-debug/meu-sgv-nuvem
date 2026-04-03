import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ Sistemas", layout="wide", page_icon="🎯")

# --- 2. SEGURANÇA (LOGIN) ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.subheader("🎯 JMQJ Sistemas")
        senha = st.text_input("Senha", type="password")
        if st.button("LIGAR"):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE DADOS INTELIGENTE ---
def buscar_universo():
    try:
        e = supabase.table("config").select("*").execute().data
        p = supabase.table("produtos").select("*").execute().data
        c = supabase.table("Clientes").select("*").execute().data
        return (e[0] if e else {}), pd.DataFrame(p), pd.DataFrame(c)
    except Exception as err:
        st.error(f"Erro de Sincronia: {err}")
        return {}, pd.DataFrame(), pd.DataFrame()

emp, df_p, df_c = buscar_universo()

# --- 4. INTERFACE ---
with st.sidebar:
    st.title("JMQJ Sistemas")
    if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
    menu = st.radio("MENS", ["📊 Painel", "👥 Clientes", "📦 Produtos", "⚙️ Ajustes"])

# --- MODULO CLIENTES (COM MAPEAMENTO DINÂMICO) ---
if menu == "👥 Clientes":
    st.header("👥 Cadastro de Clientes")
    # Identificamos como o banco chama a coluna de Nome (pode ser NOM ou nome)
    col_nome_c = "NOM" if "NOM" in df_c.columns else ("nome" if "nome" in df_c.columns else None)
    
    with st.form("f_cli", clear_on_submit=True):
        val_nome = st.text_input("Nome/Razão Social *")
        val_tel = st.text_input("Telefone")
        val_rua = st.text_input("Endereço/Rua")
        
        if st.form_submit_button("💾 SALVAR CLIENTE"):
            if val_nome:
                # Criamos o pacote de dados APENAS com o que o banco aceita
                payload = {}
                if col_nome_c: payload[col_nome_c] = val_nome
                if "RUA" in df_c.columns: payload["RUA"] = val_rua
                elif "endereco" in df_c.columns: payload["endereco"] = val_rua
                
                try:
                    supabase.table("Clientes").insert(payload).execute()
                    st.success("Gravado com sucesso!")
                    time.sleep(1); st.rerun()
                except Exception as e:
                    st.error(f"O banco ainda recusa. Colunas atuais: {list(df_c.columns)}. Erro: {e}")
            else: st.warning("Nome é obrigatório.")
    st.dataframe(df_c, use_container_width=True)

# --- MODULO PRODUTOS ---
elif menu == "📦 Produtos":
    st.header("📦 Cadastro de Produtos")
    # Identificamos como o banco chama a descrição (pode ser descricao ou nome)
    col_desc = "descricao" if "descricao" in df_p.columns else ("nome" if "nome" in df_p.columns else None)
    col_preco = "p_venda" if "p_venda" in df_p.columns else ("preco" if "preco" in df_p.columns else None)

    with st.form("f_pro", clear_on_submit=True):
        val_desc = st.text_input("Descrição do Item *")
        val_prc = st.number_input("Preço", value=0.0)
        
        if st.form_submit_button("💾 SALVAR PRODUTO"):
            if val_desc:
                payload = {}
                if col_desc: payload[col_desc] = val_desc
                if col_preco: payload[col_preco] = val_prc
                
                try:
                    supabase.table("produtos").insert(payload).execute()
                    st.success("Produto salvo!"); time.sleep(1); st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar. Colunas do banco: {list(df_p.columns)}. Erro: {e}")

# --- MODULO AJUSTES ---
elif menu == "⚙️ Ajustes":
    st.header("⚙️ Configurações")
    with st.form("f_aj"):
        n_e = st.text_input("Nome da Empresa", value=emp.get('nome', emp.get('NOM', '')))
        logo = st.file_uploader("Logo PNG", type=["png"])
        if st.form_submit_button("💾 FIXAR"):
            l64 = emp.get('logo_base64', '')
            if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
            
            # Upsert adaptável
            payload = {"id": 1}
            if "nome" in emp or not emp: payload["nome"] = n_e
            elif "NOM" in emp: payload["NOM"] = n_e
            if l64: payload["logo_base64"] = l64
            
            supabase.table("config").upsert(payload).execute()
            st.success("Configuração salva!"); st.rerun()
    
    st.divider()
    if st.button("🔥 RESET TOTAL DO SISTEMA"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        st.rerun()

elif menu == "📊 Painel":
    st.metric("Clientes", len(df_c))
    st.metric("Produtos", len(df_p))
