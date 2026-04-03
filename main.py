import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
from datetime import datetime

# --- 1. CONEXÃO DIRETA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ Sistemas", layout="wide", page_icon="🎯")

# --- 2. ACESSO MESTRE ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.markdown("<h2 style='text-align: center;'>🎯 JMQJ Sistemas</h2>", unsafe_allow_html=True)
        senha = st.text_input("Chave de Segurança", type="password")
        if st.button("LIGAR SISTEMA", use_container_width=True):
            if senha == "Naksu@6026": 
                st.session_state.auth = True
                st.rerun()
            else: st.error("Chave incorreta.")
    st.stop()

# --- 3. MOTOR DE DADOS ---
def carregar_dados():
    try:
        e = supabase.table("config").select("*").execute().data
        p = supabase.table("produtos").select("*").execute().data
        c = supabase.table("Clientes").select("*").execute().data
        return (e[0] if e else {}), pd.DataFrame(p), pd.DataFrame(c)
    except Exception as err:
        st.error(f"Erro de Sincronia: {err}")
        return {}, pd.DataFrame(), pd.DataFrame()

emp, df_p, df_c = carregar_dados()

# --- 4. INTERFACE ---
with st.sidebar:
    st.title("JMQJ Sistemas")
    if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
    st.write(f"**Gestão:** {emp.get('nome', 'JMQJ Sistemas')}")
    st.divider()
    menu = st.radio("NAVEGAÇÃO", ["📊 Painel", "🧾 Emitir Pedido", "📦 Produtos", "👥 Clientes", "⚙️ Ajustes"])

# --- MODULO: CLIENTES ---
if menu == "👥 Clientes":
    st.header("👥 Cadastro de Clientes")
    with st.form("f_cli", clear_on_submit=True):
        n = st.text_input("Nome/Razão Social *")
        c1, c2 = st.columns(2)
        doc = c1.text_input("CPF/CNPJ")
        t = c2.text_input("Telefone")
        end = st.text_input("Endereço")
        if st.form_submit_button("💾 SALVAR CLIENTE"):
            if n:
                # Usando 'nome' minúsculo conforme sua tabela do Supabase
                supabase.table("Clientes").insert({"nome": n, "CPF": doc, "TEL": t, "RUA": end}).execute()
                st.success("✅ Cliente gravado!"); time.sleep(1); st.rerun()
            else: st.warning("Nome é obrigatório.")
    if not df_c.empty: st.dataframe(df_c, use_container_width=True, hide_index=True)

# --- MODULO: PRODUTOS ---
elif menu == "📦 Produtos":
    st.header("📦 Cadastro de Produtos")
    with st.form("f_pro", clear_on_submit=True):
        d = st.text_input("Descrição do Item *")
        c1, c2 = st.columns(2)
        u = c1.text_input("Unidade", value="UN")
        p = c2.number_input("Preço de Venda", value=0.0)
        if st.form_submit_button("💾 SALVAR PRODUTO"):
            if d:
                # Usando 'nome' e 'preco' minúsculos conforme sua tabela
                supabase.table("produtos").insert({"nome": d, "unidade": u, "preco": p}).execute()
                st.success("✅ Produto gravado!"); time.sleep(1); st.rerun()

# --- MODULO: PEDIDO ---
elif menu == "🧾 Emitir Pedido":
    st.header("🧾 Novo Pedido")
    if df_c.empty or df_p.empty:
        st.warning("Cadastre dados antes de emitir vendas.")
    else:
        with st.form("venda"):
            cli = st.selectbox("Cliente", df_c['nome'].tolist())
            prod = st.selectbox("Produto", df_p['nome'].tolist())
            q = st.number_input("Quantidade", min_value=1, value=1)
            if st.form_submit_button("GERAR PEDIDO"):
                # Layout Meia Folha A4
                p_data = df_p[df_p['nome'] == prod].iloc[0]
                total = p_data['preco'] * q
                st.markdown(f"""
                <div style="border: 2px solid #000; padding: 20px; font-family: monospace; background: white; color: black;">
                    <h3 style="text-align:center;">{emp.get('nome', 'JMQJ SISTEMAS')}</h3>
                    <hr>
                    <p><b>CLIENTE:</b> {cli}</p>
                    <p><b>ITEM:</b> {prod} | {q} x R$ {p_data['preco']:.2f}</p>
                    <h2 style="text-align:right;">TOTAL: R$ {total:.2f}</h2>
                </div>
                """, unsafe_allow_html=True)

# --- MODULO: AJUSTES ---
elif menu == "⚙️ Ajustes":
    st.header("⚙️ Configurações")
    with st.form("f_conf"):
        nome_e = st.text_input("Nome da sua Empresa", value=emp.get('nome', ''))
        tel_e = st.text_input("Telefone", value=emp.get('tel', ''))
        logo = st.file_uploader("Sua Logo (PNG)", type=["png"])
        if st.form_submit_button("💾 FIXAR DADOS"):
            l64 = emp.get('logo_base64', '')
            if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
            supabase.table("config").upsert({"id": 1, "nome": nome_e, "tel": tel_e, "logo_base64": l64}).execute()
            st.success("Configuração salva!"); st.rerun()
    
    st.divider()
    if st.button("🔥 RESET TOTAL"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        st.rerun()

elif menu == "📊 Painel":
    st.header("📊 Resumo Operacional")
    c1, c2 = st.columns(2)
    c1.metric("Clientes Ativos", len(df_c))
    c2.metric("Itens Cadastrados", len(df_p))
