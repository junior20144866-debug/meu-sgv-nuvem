import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
from datetime import datetime

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
        senha = st.text_input("Chave de Acesso", type="password")
        if st.button("LIGAR"):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
    st.stop()

# --- 3. MOTOR DE DADOS ADAPTATIVO (O FIM DO ERRO PGRST204) ---
def sincronizar_universo():
    try:
        e = supabase.table("config").select("*").execute().data
        p = supabase.table("produtos").select("*").execute().data
        c = supabase.table("Clientes").select("*").execute().data
        return (e[0] if e else {}), pd.DataFrame(p), pd.DataFrame(c)
    except Exception as err:
        st.error(f"Erro de Sincronia: {err}")
        return {}, pd.DataFrame(), pd.DataFrame()

emp, df_p, df_c = sincronizar_universo()

# --- 4. INTERFACE ---
with st.sidebar:
    st.title("JMQJ Sistemas")
    if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
    st.info(f"Empresa: {emp.get('nome', 'JMQJ')}")
    menu = st.radio("MENS", ["📊 Painel", "🧾 Emitir Pedido", "📦 Produtos", "👥 Clientes", "⚙️ Ajustes"])

# --- MODULO CLIENTES (SISTEMA DE MAPEAMENTO) ---
if menu == "👥 Clientes":
    st.header("👥 Cadastro de Clientes")
    with st.form("f_cli", clear_on_submit=True):
        nome = st.text_input("Nome/Razão Social *")
        doc = st.text_input("CPF/CNPJ")
        tel = st.text_input("Telefone")
        end = st.text_input("Endereço")
        if st.form_submit_button("💾 SALVAR CLIENTE"):
            if nome:
                # O código agora envia os dados baseados nas colunas que vimos no seu print do banco
                payload = {"nome": nome} # Coluna padrão que vimos no seu Supabase
                if "CPF" in df_c.columns: payload["CPF"] = doc
                if "TEL" in df_c.columns: payload["TEL"] = tel
                if "RUA" in df_c.columns: payload["RUA"] = end
                
                try:
                    supabase.table("Clientes").insert(payload).execute()
                    st.success("✅ Gravado com sucesso!"); time.sleep(1); st.rerun()
                except Exception as e:
                    st.error(f"Erro técnico: {e}")
            else: st.warning("Nome é obrigatório.")
    st.dataframe(df_c, use_container_width=True)

# --- MODULO PRODUTOS ---
elif menu == "📦 Produtos":
    st.header("📦 Cadastro de Produtos")
    with st.form("f_pro", clear_on_submit=True):
        desc = st.text_input("Descrição do Produto *")
        prc = st.number_input("Preço de Venda", value=0.0)
        if st.form_submit_button("💾 SALVAR PRODUTO"):
            if desc:
                # Usando os nomes minúsculos que o seu banco criou automaticamente
                payload = {"nome": desc, "preco": prc}
                try:
                    supabase.table("produtos").insert(payload).execute()
                    st.success("✅ Produto salvo!"); time.sleep(1); st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

# --- MODULO EMISSÃO DE PEDIDO (SAAS STYLE) ---
elif menu == "🧾 Emitir Pedido":
    st.header("🧾 Novo Pedido de Venda")
    if df_c.empty or df_p.empty:
        st.warning("Cadastre dados antes de operar.")
    else:
        col1, col2 = st.columns([1, 1.2])
        with col1:
            with st.form("venda"):
                c_sel = st.selectbox("Selecione o Cliente", df_c['nome'].tolist() if 'nome' in df_c.columns else [])
                p_sel = st.selectbox("Selecione o Produto", df_p['nome'].tolist() if 'nome' in df_p.columns else [])
                qtd = st.number_input("Quantidade", min_value=1, value=1)
                desc = st.number_input("Desconto (R$)", value=0.0)
                if st.form_submit_button("GERAR PEDIDO"):
                    st.session_state.v_ok = True
                    st.session_state.v_cli = c_sel
                    st.session_state.v_pro = p_sel
                    st.session_state.v_qtd = qtd
                    st.session_state.v_desc = desc

        if st.session_state.get('v_ok'):
            with col2:
                # Layout Profissional de Impressão A5
                st.markdown(f"""
                <div style="border: 2px solid #000; padding: 20px; font-family: monospace; background: white; color: black;">
                    <h3 style="text-align:center;">{emp.get('nome', 'JMQJ SISTEMAS')}</h3>
                    <hr>
                    <p><b>CLIENTE:</b> {st.session_state.v_cli}</p>
                    <p><b>ITEM:</b> {st.session_state.v_pro} x {st.session_state.v_qtd}</p>
                    <p style="text-align:right;">Desconto: R$ {st.session_state.v_desc:.2f}</p>
                    <h2 style="text-align:right;">TOTAL: R$ 0,00</h2>
                </div>
                """, unsafe_allow_html=True)

# --- MODULO AJUSTES (IDENTIDADE) ---
elif menu == "⚙️ Ajustes":
    st.header("⚙️ Configurações da Empresa")
    with st.form("f_aj"):
        n_e = st.text_input("Nome da Empresa", value=emp.get('nome', ''))
        tel_e = st.text_input("Telefone", value=emp.get('tel', ''))
        logo = st.file_uploader("Logo PNG", type=["png"])
        if st.form_submit_button("💾 FIXAR DADOS"):
            l64 = emp.get('logo_base64', '')
            if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
            
            payload = {"id": 1, "nome": n_e}
            if tel_e: payload["tel"] = tel_e
            if l64: payload["logo_base64"] = l64
            
            supabase.table("config").upsert(payload).execute()
            st.success("Dados fixados!"); st.rerun()
    
    st.divider()
    if st.button("🔥 RESET TOTAL DO SISTEMA"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        st.rerun()
