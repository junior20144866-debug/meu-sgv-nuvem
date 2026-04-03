import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
from datetime import datetime

# --- 1. CONEXÃO SEGURA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
# Nota: Em um SaaS real, usamos chaves de serviço para backend seguro
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ Sistemas", layout="wide", page_icon="🛡️")

# --- 2. ACESSO PROTEGIDO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.markdown("<h2 style='text-align: center;'>🔐 JMQJ SISTEMAS</h2>", unsafe_allow_html=True)
        senha = st.text_input("Senha de Operação", type="password")
        if st.button("ATIVAR SISTEMA", use_container_width=True):
            if senha == "Naksu@6026": 
                st.session_state.auth = True
                st.rerun()
            else: st.error("Acesso negado.")
    st.stop()

# --- 3. CARREGAMENTO REAL-TIME ---
def carregar_contexto():
    try:
        e = supabase.table("config").select("*").eq("id", 1).execute().data
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        c = supabase.table("Clientes").select("*").order("NOM").execute().data
        return (e[0] if e else {}), pd.DataFrame(p), pd.DataFrame(c)
    except Exception as e:
        st.error(f"Erro de Segurança/Conexão: {e}")
        return {}, pd.DataFrame(), pd.DataFrame()

emp, df_p, df_c = carregar_contexto()

# --- 4. INTERFACE ---
with st.sidebar:
    st.title("JMQJ Sistemas")
    if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
    st.write(f"**Empresa:** {emp.get('nome', 'JMQJ')}")
    st.write("---")
    menu = st.radio("MÓDULOS", ["📊 Painel", "🧾 Vendas/Pedidos", "👥 Clientes", "📦 Produtos", "⚙️ Configurações"])

# --- MODULO CLIENTES (INSERÇÃO MANUAL ROBUSTA) ---
if menu == "👥 Clientes":
    st.header("👥 Cadastro Manual de Clientes")
    with st.form("form_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome/Razão Social *")
        doc = col2.text_input("CPF/CNPJ")
        
        rua = st.text_input("Rua/Logradouro")
        c1, c2, c3 = st.columns([2, 1, 1])
        bairro = c1.text_input("Bairro")
        cep = c2.text_input("CEP")
        uf = c3.text_input("UF", max_chars=2)
        
        cidade = st.text_input("Cidade")
        
        col3, col4 = st.columns(2)
        tel = col3.text_input("Telefone/WhatsApp")
        email = col4.text_input("E-mail")
        
        if st.form_submit_button("💾 SALVAR NO BANCO DE DADOS"):
            if not nome:
                st.warning("O Nome é obrigatório.")
            else:
                try:
                    payload = {
                        "NOM": nome, "CPF": doc, "RUA": rua, "BAI": bairro,
                        "CEP": cep, "UF": uf, "CIDADE": cidade, "TEL": tel, "EMAIL": email
                    }
                    supabase.table("Clientes").insert(payload).execute()
                    st.success("✅ Cliente gravado com sucesso!")
                    time.sleep(1); st.rerun()
                except Exception as err:
                    st.error(f"❌ Falha na gravação. Verifique as permissões do banco: {err}")

# --- MODULO CONFIGURAÇÕES ---
elif menu == "⚙️ Configurações":
    st.header("⚙️ Ajustes JMQJ Sistemas")
    with st.form("form_config"):
        st.subheader("Dados da sua Empresa")
        n_e = st.text_input("Nome da Empresa", value=emp.get('nome', ''))
        c_e = st.text_input("CNPJ", value=emp.get('cnpj', ''))
        t_e = st.text_input("Telefone/WhatsApp", value=emp.get('tel', ''))
        logo = st.file_uploader("Sua Logomarca (PNG)", type=["png"])
        
        if st.form_submit_button("💾 FIXAR IDENTIDADE"):
            l64 = emp.get('logo_base64', '')
            if logo:
                l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
            
            try:
                supabase.table("config").upsert({
                    "id": 1, "nome": n_e, "cnpj": c_e, "tel": t_e, "logo_base64": l64
                }).execute()
                st.success("Configuração salva!")
                st.rerun()
            except Exception as err:
                st.error(f"Erro ao salvar configuração: {err}")

    st.divider()
    if st.button("🔥 ZERAR SISTEMA (RESET)"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        st.rerun()

# --- MÓDULOS DE VISUALIZAÇÃO ---
elif menu == "📊 Painel":
    st.header("Resumo Operacional")
    st.metric("Total de Clientes", len(df_c))
    st.metric("Total de Produtos", len(df_p))

elif menu == "📦 Produtos":
    st.header("📦 Estoque")
    if not df_p.empty: st.dataframe(df_p, use_container_width=True)
    else: st.info("Nenhum produto cadastrado.")

elif menu == "🧾 Vendas/Pedidos":
    st.header("🧾 Emissão de Pedido")
    if df_c.empty: st.warning("Cadastre clientes primeiro.")
    else:
        st.selectbox("Selecione o Cliente", df_c['NOM'].tolist())
        st.info("Módulo pronto para emissão em Meia Folha A4.")
