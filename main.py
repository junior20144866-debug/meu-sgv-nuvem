import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
from datetime import datetime, timedelta

# --- 1. CONEXÃO E CONFIGURAÇÃO ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v87", layout="wide", page_icon="🎯")

# --- 2. MOTOR DE SEGURANÇA (BLOQUEIO INICIAL) ---
if 'auth' not in st.session_state: st.session_state.auth = False

def login_screen():
    _, col, _ = st.columns([1,1,1])
    with col:
        st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito</h2>", unsafe_allow_html=True)
        senha = st.text_input("Senha Mestra", type="password")
        if st.button("ENTRAR NO SISTEMA", use_container_width=True):
            if senha == "Naksu@6026": 
                st.session_state.auth = True
                st.rerun()
            else: st.error("Senha incorreta.")

if not st.session_state.auth:
    login_screen()
    st.stop()

# --- 3. MOTOR DE DADOS (CACHE DE ESTADO) ---
@st.cache_data(ttl=60) # Atualiza a cada 1 min ou no clique de salvar
def buscar_dados():
    try:
        e = supabase.table("config").select("*").eq("id", 1).execute().data
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        c = supabase.table("Clientes").select("*").order("NOM").execute().data
        return (e[0] if e else {}), pd.DataFrame(p), pd.DataFrame(c)
    except:
        return {}, pd.DataFrame(), pd.DataFrame()

emp, df_p, df_c = buscar_dados()

# --- 4. INTERFACE OPERACIONAL ---
with st.sidebar:
    if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
    st.title(emp.get('nome', 'JMQJ SGV'))
    st.caption(f"Unidade: {emp.get('uf', 'CE')}")
    menu = st.radio("MÓDULOS", ["📊 Painel", "💰 Vendas & Pedidos", "📦 Estoque", "👥 Clientes", "📂 Importação", "⚙️ Ajustes"])

# --- MÓDULO: PAINEL ---
if menu == "📊 Painel":
    st.header("Indicadores de Gestão")
    c1, c2, c3 = st.columns(3)
    c1.metric("Produtos", len(df_p))
    c2.metric("Clientes", len(df_c))
    c3.metric("Status", "Online")

# --- MÓDULO: VENDAS (MOTOR DE IMPRESSÃO A5) ---
elif menu == "💰 Vendas & Pedidos":
    st.header("Emissão de Pedido")
    col1, col2 = st.columns([1, 1.3])
    with col1:
        with st.form("venda"):
            sel_cli = st.selectbox("Cliente", df_c['NOM'].tolist() if not df_c.empty else ["Vazio"])
            sel_prod = st.selectbox("Item", df_p['descricao'].tolist() if not df_p.empty else ["Vazio"])
            qtd = st.number_input("Qtd", min_value=1)
            vias = st.radio("Vias de Impressão", ["1 via (Metade A4)", "2 vias (Folha Inteira)"])
            if st.form_submit_button("GERAR DOCUMENTO"):
                st.session_state.venda_ok = True
    
    if st.session_state.get('venda_ok'):
        with col2:
            st.info("Visualização para Impressão")
            corpo_pedido = f"""
            <div style="border:1px solid #000; padding:20px; font-family:monospace; margin-bottom:10px;">
                <h3 style='text-align:center;'>{emp.get('nome')}</h3>
                <p>CNPJ: {emp.get('cnpj')} | {emp.get('end')}</p>
                <hr>
                <p><b>CLIENTE:</b> {sel_cli}</p>
                <p><b>ITEM:</b> {sel_prod} | QTD: {qtd}</p>
                <br><br><br>
                <p style='text-align:center;'>_________________________________<br>Assinatura</p>
            </div>
            """
            st.markdown(corpo_pedido, unsafe_allow_html=True)
            if vias == "2 vias (Folha Inteira)":
                st.markdown(corpo_pedido, unsafe_allow_html=True)

# --- MÓDULO: CLIENTES (INCLUSÃO MANUAL COMPLETA) ---
elif menu == "👥 Clientes":
    st.header("Gestão de Clientes")
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Novo Cadastro"])
    with tab1:
        st.dataframe(df_c, use_container_width=True, hide_index=True)
    with tab2:
        with st.form("cli_manual"):
            c1, c2 = st.columns(2)
            nome = c1.text_input("Nome/Razão Social (NOM)")
            doc = c2.text_input("CNPJ/CPF")
            rua = st.text_input("Rua")
            bairro = c1.text_input("Bairro")
            cep = c2.text_input("CEP")
            email = st.text_input("E-mail")
            if st.form_submit_button("💾 SALVAR CLIENTE"):
                supabase.table("Clientes").insert({"NOM": nome, "CPF": doc, "RUA": rua, "BAI": bairro, "CEP": cep, "EMAIL": email}).execute()
                st.cache_data.clear(); st.rerun()

# --- MÓDULO: IMPORTAÇÃO MASSIVA INTELIGENTE ---
elif menu == "📂 Importação":
    st.header("Importação Massiva (DNA Bússola)")
    arquivo = st.file_uploader("Suba o Excel (.xlsx)", type=["xlsx"])
    if arquivo and st.button("🚀 PROCESSAR"):
        df_in = pd.read_excel(arquivo)
        # TRADUTOR: Mapeia colunas do Excel para o Banco
        df_in.columns = [c.upper().strip() for c in df_in.columns]
        for r in df_in.to_dict('records'):
            try:
                # Lógica para produtos ou clientes baseada no cabeçalho
                if 'NOM' in df_in.columns:
                    supabase.table("Clientes").insert({"NOM": str(r.get('NOM')), "RUA": str(r.get('RUA','')), "BAI": str(r.get('BAI',''))}).execute()
                else:
                    supabase.table("produtos").insert({"descricao": str(r.get('DESCRICAO')), "p_venda": float(r.get('P_VENDA',0))}).execute()
            except: pass
        st.success("Importação concluída!")
        st.cache_data.clear(); time.sleep(1); st.rerun()

# --- MÓDULO: AJUSTES (CONTROLE TOTAL) ---
elif menu == "⚙️ Ajustes":
    st.header("Configurações da Empresa")
    with st.form("empresa"):
        n = st.text_input("Nome", value=emp.get('nome',''))
        cnpj = st.text_input("CNPJ", value=emp.get('cnpj',''))
        uf = st.selectbox("UF", ["CE", "RN", "PB", "PE"], index=0)
        logo = st.file_uploader("Logo", type=["png"])
        if st.form_submit_button("FIXAR DADOS"):
            l64 = emp.get('logo_base64', '')
            if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
            supabase.table("config").upsert({"id": 1, "nome": n, "cnpj": cnpj, "uf": uf, "logo_base64": l64}).execute()
            st.cache_data.clear(); st.rerun()
    
    st.divider()
    if st.button("🔥 RESET TOTAL DO BANCO"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        st.cache_data.clear(); st.rerun()
