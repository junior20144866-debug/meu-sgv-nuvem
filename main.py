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

# --- 2. SEGURANÇA E ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.markdown("<h2 style='text-align: center;'>🔐 JMQJ Sistemas</h2>", unsafe_allow_html=True)
        senha = st.text_input("Senha Mestra", type="password")
        if st.button("LIGAR SISTEMA", use_container_width=True):
            if senha == "Naksu@6026": 
                st.session_state.auth = True
                st.rerun()
            else: st.error("Senha inválida.")
    st.stop()

# --- 3. MOTOR DE DADOS ADAPTÁVEL (EVITA ERRO PGRST204) ---
def carregar_contexto_total():
    try:
        e = supabase.table("config").select("*").execute().data
        p = supabase.table("produtos").select("*").execute().data
        c = supabase.table("Clientes").select("*").execute().data
        return (e[0] if e else {}), pd.DataFrame(p), pd.DataFrame(c)
    except Exception as err:
        st.error(f"Erro de Sincronia: {err}")
        return {}, pd.DataFrame(), pd.DataFrame()

emp, df_p, df_c = carregar_contexto_total()

# --- 4. BARRA LATERAL (CONTROLE E IDENTIDADE) ---
with st.sidebar:
    st.title("JMQJ Sistemas")
    if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
    st.write(f"**Empresa:** {emp.get('nome', 'JMQJ Sistemas')}")
    st.divider()
    menu = st.radio("NAVEGAÇÃO", ["📊 Dashboard", "📝 Emitir Pedido", "📦 Estoque", "👥 Clientes", "⚙️ Ajustes"])

# --- MODULO: AJUSTES (CONFIGURAÇÃO DA EMPRESA) ---
if menu == "⚙️ Ajustes":
    st.header("⚙️ Configurações e Identidade")
    with st.form("f_config"):
        nome_e = st.text_input("Nome da Empresa", value=emp.get('nome', ''))
        cnpj_e = st.text_input("CNPJ", value=emp.get('cnpj', ''))
        end_e = st.text_input("Endereço Completo", value=emp.get('end', ''))
        tel_e = st.text_input("Telefone/WhatsApp", value=emp.get('tel', ''))
        logo = st.file_uploader("Sua Logomarca (PNG)", type=["png"])
        if st.form_submit_button("💾 SALVAR CONFIGURAÇÃO"):
            l64 = emp.get('logo_base64', '')
            if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
            supabase.table("config").upsert({
                "id": 1, "nome": nome_e, "cnpj": cnpj_e, "end": end_e, "tel": tel_e, "logo_base64": l64
            }).execute()
            st.success("Configurações cravadas!"); st.rerun()
    
    st.divider()
    if st.button("🔥 RESET TOTAL DO BANCO"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        st.rerun()

# --- MODULO: CLIENTES (FOCO OPERACIONAL) ---
elif menu == "👥 Clientes":
    st.header("👥 Gestão de Clientes")
    with st.expander("➕ Adicionar Novo Cliente", expanded=df_c.empty):
        with st.form("f_cli", clear_on_submit=True):
            n = st.text_input("Nome/Razão Social (NOM)")
            c1, c2 = st.columns(2)
            doc = c1.text_input("CPF/CNPJ")
            tel = c2.text_input("Telefone")
            rua = st.text_input("Endereço")
            if st.form_submit_button("💾 SALVAR CLIENTE"):
                supabase.table("Clientes").insert({"NOM": n, "CPF": doc, "TEL": tel, "RUA": rua}).execute()
                st.success("Cliente salvo!"); time.sleep(1); st.rerun()
    
    if not df_c.empty:
        st.dataframe(df_c, use_container_width=True, hide_index=True)

# --- MODULO: ESTOQUE (PRODUTOS) ---
elif menu == "📦 Estoque":
    st.header("📦 Gestão de Produtos")
    with st.expander("➕ Adicionar Novo Produto", expanded=df_p.empty):
        with st.form("f_pro", clear_on_submit=True):
            desc = st.text_input("Descrição do Produto")
            c1, c2 = st.columns(2)
            uni = c1.text_input("Unidade", value="UN")
            prc = c2.number_input("Preço de Venda (R$)", min_value=0.0, step=1.0)
            if st.form_submit_button("💾 SALVAR PRODUTO"):
                # O sistema agora só envia o que é garantido existir no banco
                payload = {"descricao": desc, "unidade": uni, "p_venda": prc}
                supabase.table("produtos").insert(payload).execute()
                st.success("Produto salvo!"); time.sleep(1); st.rerun()
    
    if not df_p.empty:
        st.dataframe(df_p, use_container_width=True, hide_index=True)

# --- MODULO: PEDIDO (FUNCIONALIDADE BÚSSOLA) ---
elif menu == "📝 Emitir Pedido":
    st.header("🧾 Emissão de Pedido")
    if df_c.empty or df_p.empty:
        st.warning("Cadastre clientes e produtos para operar.")
    else:
        col1, col2 = st.columns([1, 1.2])
        with col1:
            with st.form("venda"):
                c_sel = st.selectbox("Cliente", df_c['NOM'].tolist())
                p_sel = st.selectbox("Produto", df_p['descricao'].tolist())
                qtd = st.number_input("Quantidade", min_value=1)
                desc = st.number_input("Desconto (R$)", value=0.0)
                if st.form_submit_button("GERAR PRÉVIA DO PEDIDO"):
                    st.session_state.venda_ok = True
                    st.session_state.v_cli = df_c[df_c['NOM'] == c_sel].iloc[0]
                    st.session_state.v_pro = df_p[df_p['descricao'] == p_sel].iloc[0]
                    st.session_state.v_qtd = qtd
                    st.session_state.v_desc = desc

        if st.session_state.get('venda_ok'):
            with col2:
                # Layout Profissional de Impressão
                cli = st.session_state.v_cli
                pro = st.session_state.v_pro
                q = st.session_state.v_qtd
                d = st.session_state.v_desc
                total = (pro['p_venda'] * q) - d
                
                st.markdown(f"""
                <div style="border: 2px solid #000; padding: 20px; font-family: monospace; background: white; color: black;">
                    <h3 style="text-align:center;">{emp.get('nome', 'JMQJ SISTEMAS')}</h3>
                    <p style="text-align:center;">{emp.get('cnpj', '')} | {emp.get('tel', '')}</p>
                    <hr>
                    <p><b>CLIENTE:</b> {cli['NOM']}</p>
                    <p><b>ITEM:</b> {pro['descricao']} | {q} {pro['unidade']} x R$ {pro['p_venda']:.2f}</p>
                    <p style="text-align:right;">Subtotal: R$ {pro['p_venda']*q:.2f}</p>
                    <p style="text-align:right; color: red;">Desconto: R$ {d:.2f}</p>
                    <h2 style="text-align:right;">TOTAL: R$ {total:.2f}</h2>
                </div>
                """, unsafe_allow_html=True)

elif menu == "📊 Dashboard":
    st.header("Resumo Operacional")
    c1, c2 = st.columns(2)
    c1.metric("Clientes Ativos", len(df_c))
    c2.metric("Itens Cadastrados", len(df_p))
