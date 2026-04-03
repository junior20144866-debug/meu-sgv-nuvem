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
        st.markdown("<h2 style='text-align: center;'>🎯 JMQJ Sistemas</h2>", unsafe_allow_html=True)
        senha = st.text_input("Chave de Acesso", type="password")
        if st.button("LIGAR SISTEMA", use_container_width=True):
            if senha == "Naksu@6026": 
                st.session_state.auth = True
                st.rerun()
            else: st.error("Chave inválida.")
    st.stop()

# --- 3. MOTOR DE DADOS ADAPTATIVO ---
def carregar_universo():
    try:
        e = supabase.table("config").select("*").execute().data
        p = supabase.table("produtos").select("*").execute().data
        c = supabase.table("Clientes").select("*").execute().data
        return (e[0] if e else {}), pd.DataFrame(p), pd.DataFrame(c)
    except Exception as err:
        st.error(f"Erro de Conexão: {err}")
        return {}, pd.DataFrame(), pd.DataFrame()

emp, df_p, df_c = carregar_universo()

# --- 4. INTERFACE ---
with st.sidebar:
    st.title("JMQJ Sistemas")
    if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
    st.write(f"**Empresa:** {emp.get('nome', 'JMQJ')}")
    st.divider()
    menu = st.radio("MÓDULOS", ["📊 Painel", "🧾 Emitir Pedido", "📦 Produtos", "👥 Clientes", "⚙️ Ajustes"])

# --- MODULO: AJUSTES (CRAVAR CONFIGURAÇÃO) ---
if menu == "⚙️ Ajustes":
    st.header("⚙️ Configurações da Empresa")
    with st.form("f_ajustes"):
        n_e = st.text_input("Nome da Empresa", value=emp.get('nome',''))
        tel_e = st.text_input("Telefone", value=emp.get('tel',''))
        logo = st.file_uploader("Logomarca (PNG)", type=["png"])
        if st.form_submit_button("💾 FIXAR DADOS"):
            l64 = emp.get('logo_base64', '')
            if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
            
            # Upsert inteligente: só envia colunas confirmadas
            payload = {"id": 1, "nome": n_e}
            if tel_e: payload["tel"] = tel_e
            if l64: payload["logo_base64"] = l64
            
            try:
                supabase.table("config").upsert(payload).execute()
                st.success("Configuração salva!"); time.sleep(1); st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
    
    st.divider()
    if st.button("🔥 RESET TOTAL DO SISTEMA"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        st.rerun()

# --- MODULO: CLIENTES (MAPEAMENTO DINÂMICO) ---
elif menu == "👥 Clientes":
    st.header("👥 Gestão de Clientes")
    with st.form("f_cli", clear_on_submit=True):
        nome = st.text_input("Nome/Razão Social *")
        tel = st.text_input("Telefone")
        end = st.text_input("Endereço/Rua")
        if st.form_submit_button("💾 SALVAR CLIENTE"):
            if nome:
                try:
                    # Mapeia para as colunas minúsculas que vimos nas suas imagens
                    supabase.table("Clientes").insert({"nome": nome, "telefone": tel, "endereco": end}).execute()
                    st.success("Cliente gravado!"); time.sleep(1); st.rerun()
                except Exception as e:
                    st.error(f"O banco recusou a gravação: {e}")
            else: st.warning("Nome é obrigatório.")
    if not df_c.empty: st.dataframe(df_c, use_container_width=True)

# --- MODULO: PRODUTOS ---
elif menu == "📦 Produtos":
    st.header("📦 Gestão de Produtos")
    with st.form("f_pro", clear_on_submit=True):
        desc = st.text_input("Descrição do Item *")
        prc = st.number_input("Preço de Venda", value=0.0)
        if st.form_submit_button("💾 SALVAR PRODUTO"):
            if desc:
                try:
                    supabase.table("produtos").insert({"nome": desc, "preco": prc}).execute()
                    st.success("Produto cravado!"); time.sleep(1); st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
    if not df_p.empty: st.dataframe(df_p, use_container_width=True)

# --- MODULO: PEDIDO (IMPRESSÃO A5) ---
elif menu == "🧾 Emitir Pedido":
    st.header("🧾 Novo Pedido")
    if df_c.empty or df_p.empty:
        st.warning("Cadastre dados antes de vender.")
    else:
        with st.form("venda"):
            # Ajustado para ler as colunas 'nome' (minúsculo)
            c_sel = st.selectbox("Cliente", df_c['nome'].tolist() if 'nome' in df_c.columns else [])
            p_sel = st.selectbox("Produto", df_p['nome'].tolist() if 'nome' in df_p.columns else [])
            qtd = st.number_input("Qtd", min_value=1, value=1)
            if st.form_submit_button("GERAR PRÉVIA"):
                st.session_state.v_ok = True
                st.session_state.v_cli = c_sel
                st.session_state.v_pro = p_sel
                st.session_state.v_qtd = qtd

        if st.session_state.get('v_ok'):
            st.markdown(f"""
            <div style="border: 2px solid #000; padding: 20px; font-family: monospace; background: white; color: black;">
                <h3 style="text-align:center;">{emp.get('nome', 'JMQJ SISTEMAS')}</h3>
                <hr>
                <p><b>CLIENTE:</b> {st.session_state.v_cli}</p>
                <p><b>ITEM:</b> {st.session_state.v_pro} | Qtd: {st.session_state.v_qtd}</p>
                <br><br>
                <p style="text-align:center;">________________________<br>Assinatura</p>
            </div>
            """, unsafe_allow_html=True)

elif menu == "📊 Painel":
    st.header("📊 Resumo")
    c1, c2 = st.columns(2)
    c1.metric("Clientes", len(df_c))
    c2.metric("Produtos", len(df_p))
