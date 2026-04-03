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
        senha = st.text_input("Chave de Operação", type="password")
        if st.button("ABRIR SISTEMA", use_container_width=True):
            if senha == "Naksu@6026": 
                st.session_state.auth = True
                st.rerun()
            else: st.error("Chave inválida.")
    st.stop()

# --- 3. MOTOR DE DADOS ---
def carregar_contexto():
    try:
        e = supabase.table("config").select("*").execute().data
        p = supabase.table("produtos").select("*").execute().data
        c = supabase.table("Clientes").select("*").execute().data
        return (e[0] if e else {}), pd.DataFrame(p), pd.DataFrame(c)
    except Exception as err:
        st.error(f"Erro de conexão: {err}")
        return {}, pd.DataFrame(), pd.DataFrame()

emp, df_p, df_c = carregar_contexto()

# --- 4. INTERFACE ---
with st.sidebar:
    st.title("JMQJ Sistemas")
    if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
    st.write(f"**Empresa:** {emp.get('nome', 'JMQJ Sistemas')}")
    st.divider()
    menu = st.radio("MÓDULOS", ["📊 Dashboard", "📝 Emitir Pedido", "📦 Produtos", "👥 Clientes", "⚙️ Ajustes"])

# --- MODULO: AJUSTES ---
if menu == "⚙️ Ajustes":
    st.header("⚙️ Configurações do Sistema")
    with st.form("f_conf"):
        n_e = st.text_input("Nome da Empresa", value=emp.get('nome', ''))
        c_e = st.text_input("CNPJ", value=emp.get('cnpj', ''))
        t_e = st.text_input("Telefone", value=emp.get('tel', ''))
        logo = st.file_uploader("Logomarca (PNG)", type=["png"])
        if st.form_submit_button("💾 FIXAR DADOS"):
            l64 = emp.get('logo_base64', '')
            if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
            supabase.table("config").upsert({"id": 1, "nome": n_e, "cnpj": c_e, "tel": t_e, "logo_base64": l64}).execute()
            st.success("Configuração salva!"); st.rerun()
    
    st.divider()
    if st.button("🔥 ZERAR TUDO (RESET TOTAL)"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        st.rerun()

# --- MODULO: CLIENTES ---
elif menu == "👥 Clientes":
    st.header("👥 Cadastro de Clientes")
    with st.form("f_cli", clear_on_submit=True):
        nome = st.text_input("Nome/Razão Social (NOM) *")
        c1, c2 = st.columns(2)
        doc = c1.text_input("CPF/CNPJ")
        tel = c2.text_input("Telefone")
        rua = st.text_input("Endereço")
        if st.form_submit_button("💾 SALVAR CLIENTE"):
            if nome:
                supabase.table("Clientes").insert({"NOM": nome, "CPF": doc, "TEL": tel, "RUA": rua}).execute()
                st.success("Cliente gravado!"); time.sleep(1); st.rerun()
            else: st.warning("Nome é obrigatório.")
    if not df_c.empty: st.dataframe(df_c, use_container_width=True, hide_index=True)

# --- MODULO: PRODUTOS ---
elif menu == "📦 Produtos":
    st.header("📦 Cadastro de Produtos")
    with st.form("f_pro", clear_on_submit=True):
        desc = st.text_input("Descrição do Item *")
        c1, c2 = st.columns(2)
        uni = c1.text_input("Unidade", value="UN")
        prc = c2.number_input("Preço de Venda", value=0.0)
        if st.form_submit_button("💾 SALVAR PRODUTO"):
            if desc:
                supabase.table("produtos").insert({"descricao": desc, "unidade": uni, "p_venda": prc}).execute()
                st.success("Produto gravado!"); time.sleep(1); st.rerun()
            else: st.warning("Descrição é obrigatória.")
    if not df_p.empty: st.dataframe(df_p, use_container_width=True, hide_index=True)

# --- MODULO: PEDIDO ---
elif menu == "📝 Emitir Pedido":
    st.header("🧾 Novo Pedido")
    if df_c.empty or df_p.empty:
        st.warning("Cadastre dados antes de vender.")
    else:
        col1, col2 = st.columns([1, 1.2])
        with col1:
            with st.form("f_venda"):
                c_sel = st.selectbox("Selecione o Cliente", df_c['NOM'].tolist())
                p_sel = st.selectbox("Selecione o Produto", df_p['descricao'].tolist())
                qtd = st.number_input("Quantidade", min_value=1, value=1)
                desc = st.number_input("Desconto R$", value=0.0)
                if st.form_submit_button("GERAR PRÉVIA"):
                    st.session_state.print_ok = True
                    st.session_state.p_cli = df_c[df_c['NOM'] == c_sel].iloc[0]
                    st.session_state.p_pro = df_p[df_p['descricao'] == p_sel].iloc[0]
                    st.session_state.p_qtd = qtd
                    st.session_state.p_desc = desc

        if st.session_state.get('print_ok'):
            with col2:
                v_cli = st.session_state.p_cli
                v_pro = st.session_state.p_pro
                total = (v_pro['p_venda'] * st.session_state.p_qtd) - st.session_state.p_desc
                st.markdown(f"""
                <div style="border: 2px solid #000; padding: 20px; font-family: monospace; background: white; color: black;">
                    <h3 style="text-align:center;">{emp.get('nome', 'JMQJ SISTEMAS')}</h3>
                    <hr>
                    <p><b>CLIENTE:</b> {v_cli['NOM']}</p>
                    <p><b>ITEM:</b> {v_pro['descricao']} | {st.session_state.p_qtd} x {v_pro['p_venda']}</p>
                    <h2 style="text-align:right;">TOTAL: R$ {total:.2f}</h2>
                </div>
                """, unsafe_allow_html=True)

elif menu == "📊 Dashboard":
    st.header("📊 Painel Operacional")
    c1, c2 = st.columns(2)
    c1.metric("Clientes Cadastrados", len(df_c))
    c2.metric("Itens no Estoque", len(df_p))
