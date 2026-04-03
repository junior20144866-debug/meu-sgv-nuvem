import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
from datetime import datetime

# --- 1. CONEXÃO BLINDADA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ Sistemas", layout="wide", page_icon="🎯")

# --- 2. GATEKEEPER (SEGURANÇA JÚNIOR) ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.markdown("<h2 style='text-align: center;'>🎯 JMQJ Sistemas</h2>", unsafe_allow_html=True)
        senha = st.text_input("Chave de Acesso", type="password")
        if st.button("INICIAR OPERAÇÃO", use_container_width=True):
            if senha == "Naksu@6026": 
                st.session_state.auth = True
                st.rerun()
            else: st.error("Chave inválida.")
    st.stop()

# --- 3. MOTOR DE DADOS ADAPTATIVO ---
def sincronizar_banco():
    try:
        # Busca dinâmica para evitar erros de colunas inexistentes
        c_data = supabase.table("config").select("*").execute().data
        p_data = supabase.table("produtos").select("*").execute().data
        cl_data = supabase.table("Clientes").select("*").execute().data
        return (c_data[0] if c_data else {}), pd.DataFrame(p_data), pd.DataFrame(cl_data)
    except Exception as e:
        st.error(f"Erro de Sincronia: {e}")
        return {}, pd.DataFrame(), pd.DataFrame()

emp, df_p, df_c = sincronizar_banco()

# --- 4. INTERFACE E CONTROLE TOTAL ---
with st.sidebar:
    st.title("JMQJ Sistemas")
    if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
    st.write(f"**Empresa:** {emp.get('nome', 'Não Configurada')}")
    st.divider()
    menu = st.radio("MÓDULOS", ["📊 Painel", "🧾 Novo Pedido", "👥 Clientes", "📦 Produtos", "⚙️ Configurações"])

# --- MODULO: CLIENTES (INSERÇÃO MANUAL PURA) ---
if menu == "👥 Clientes":
    st.header("👥 Gestão de Clientes")
    with st.expander("➕ Novo Cadastro Manual", expanded=df_c.empty):
        with st.form("f_cli", clear_on_submit=True):
            nome = st.text_input("Nome/Razão Social *")
            c1, c2 = st.columns(2)
            cpf = c1.text_input("CPF/CNPJ")
            tel = c2.text_input("Telefone/WhatsApp")
            rua = st.text_input("Endereço Completo")
            if st.form_submit_button("💾 SALVAR CLIENTE"):
                if nome:
                    res = supabase.table("Clientes").insert({"NOM": nome, "CPF": cpf, "TEL": tel, "RUA": rua}).execute()
                    st.success("Cliente fixado!"); time.sleep(1); st.rerun()
                else: st.warning("Preencha o nome.")
    if not df_c.empty: st.dataframe(df_c, use_container_width=True, hide_index=True)

# --- MODULO: PRODUTOS (ESTOQUE) ---
elif menu == "📦 Produtos":
    st.header("📦 Gestão de Estoque")
    with st.expander("➕ Novo Item Manual", expanded=df_p.empty):
        with st.form("f_pro", clear_on_submit=True):
            desc = st.text_input("Descrição do Produto *")
            c1, c2 = st.columns(2)
            uni = c1.text_input("Unidade", value="UN")
            prc = c2.number_input("Preço de Venda (R$)", min_value=0.0, step=0.5)
            if st.form_submit_button("💾 SALVAR PRODUTO"):
                if desc:
                    # Envia apenas colunas básicas para evitar erro de schema (PGRST204)
                    supabase.table("produtos").insert({"descricao": desc, "unidade": uni, "p_venda": prc}).execute()
                    st.success("Item adicionado!"); time.sleep(1); st.rerun()
    if not df_p.empty: st.dataframe(df_p, use_container_width=True, hide_index=True)

# --- MODULO: PEDIDO (O CORAÇÃO DO SISTEMA) ---
elif menu == "🧾 Novo Pedido":
    st.header("🧾 Emissão de Venda")
    if df_c.empty or df_p.empty:
        st.warning("Cadastre clientes e produtos antes de vender.")
    else:
        col1, col2 = st.columns([1, 1.2])
        with col1:
            with st.form("f_venda"):
                c_sel = st.selectbox("Selecione o Cliente", df_c['NOM'].tolist())
                p_sel = st.selectbox("Selecione o Produto", df_p['descricao'].tolist())
                qtd = st.number_input("Qtd", min_value=1, value=1)
                desc = st.number_input("Desconto (R$)", value=0.0)
                if st.form_submit_button("📄 GERAR DOCUMENTO"):
                    st.session_state.v_print = True
                    st.session_state.v_data = {
                        'cli': df_c[df_c['NOM'] == c_sel].iloc[0],
                        'pro': df_p[df_p['descricao'] == p_sel].iloc[0],
                        'qtd': qtd, 'desc': desc
                    }

        if st.session_state.get('v_print'):
            with col2:
                v = st.session_state.v_data
                sub = v['pro']['p_venda'] * v['qtd']
                total = sub - v['desc']
                # Layout A5 (Metade A4) Profissional
                st.markdown(f"""
                <div style="border: 2px solid #000; padding: 25px; font-family: monospace; background: white; color: black;">
                    <h3 style="text-align:center; margin:0;">{emp.get('nome', 'JMQJ SISTEMAS')}</h3>
                    <p style="text-align:center; font-size:12px;">{emp.get('cnpj', '')} | {emp.get('tel', '')}</p>
                    <hr>
                    <p><b>CLIENTE:</b> {v['cli']['NOM']}</p>
                    <p><b>END:</b> {v['cli'].get('RUA', 'Não informado')}</p>
                    <table style="width:100%; border-bottom:1px solid #000;">
                        <tr><td>{v['pro']['descricao']}</td><td align="right">{v['qtd']} {v['pro']['unidade']} x {v['pro']['p_venda']:.2f}</td></tr>
                    </table>
                    <div style="text-align:right; margin-top:10px;">
                        <p>SUBTOTAL: R$ {sub:.2f}</p>
                        <p style="color:red">DESCONTO: R$ {v['desc']:.2f}</p>
                        <h2 style="margin:0;">TOTAL: R$ {total:.2f}</h2>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES ---
elif menu == "⚙️ Configurações":
    st.header("⚙️ Ajustes do Sistema")
    with st.form("f_conf"):
        n = st.text_input("Nome da Empresa", value=emp.get('nome',''))
        c = st.text_input("CNPJ", value=emp.get('cnpj',''))
        t = st.text_input("Telefone", value=emp.get('tel',''))
        logo = st.file_uploader("Logo (PNG)", type=["png"])
        if st.form_submit_button("💾 FIXAR DADOS"):
            l64 = emp.get('logo_base64', '')
            if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
            supabase.table("config").upsert({"id": 1, "nome": n, "cnpj": c, "tel": t, "logo_base64": l64}).execute()
            st.success("Sistema configurado!"); st.rerun()
    st.divider()
    if st.button("🔥 RESET TOTAL"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        st.rerun()

elif menu == "📊 Painel":
    st.header("📊 Painel de Controle")
    c1, c2 = st.columns(2)
    c1.metric("Clientes", len(df_c))
    c2.metric("Produtos", len(df_p))
