import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
import re
from datetime import datetime

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v49", layout="wide", page_icon="📈")

# --- 2. MOTOR DE SINCRONIZAÇÃO (ANTI-SANFONA) ---
def carregar_dados_sistema():
    try:
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        cl = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'unidade', 'preco_venda'])
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'endereco'])
        
        return (c[0] if c else {}), df_p, df_c
    except Exception as e:
        return {}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO WINDOWS 11 ---
st.markdown("""
    <style>
    .stApp { background-color: #F3F3F3; }
    .win-card {
        background: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 5px solid #0078D4;
        text-align: center; margin-bottom: 15px;
    }
    .metric-val { font-size: 2.5rem; font-weight: bold; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    # CARREGAMENTO GLOBAL
    emp, df_e, df_c = carregar_dados_sistema()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'SGV OPERACIONAL'))
        st.caption(f"CNPJ: {emp.get('cnpj', '')}")
        st.write("---")
        menu = st.radio("MENUS", ["🏠 Dashboard", "🛒 Pedido de Venda", "📦 Gestão de Estoque", "👥 Gestão de Clientes", "📑 Importação Massiva", "⚙️ Ajustes & Controle"])

    # --- ABA: DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel Gerencial | {emp.get('nome', 'SGV')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-card">PRODUTOS<br><span class="metric-val">{len(df_e)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-card">CLIENTES<br><span class="metric-val">{len(df_c)}</span></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-card">VENDAS DIA<br><span class="metric-val">0</span></div>', unsafe_allow_html=True)

    # --- ABA: ESTOQUE (CONTROLE TOTAL: INCLUIR / EDITAR / EXCLUIR) ---
    elif menu == "📦 Gestão de Estoque":
        st.header("📦 Controle Total de Produtos")
        
        tab1, tab2 = st.tabs(["📋 Relação de Itens", "🛠️ Adicionar ou Corrigir"])
        
        with tab1:
            if not df_e.empty:
                st.dataframe(df_e, use_container_width=True, hide_index=True)
            else: st.info("Estoque vazio.")

        with tab2:
            st.subheader("Formulário de Produto")
            opcoes_p = ["Novo Registro"] + [f"{p['id']} - {p['descricao']}" for p in df_e.to_dict('records')]
            p_sel = st.selectbox("Selecione um produto para EDITAR ou escolha 'Novo'", opcoes_p)
            
            # Busca dados do selecionado para preencher o form
            item_ed = next((p for p in df_e.to_dict('records') if str(p['id']) in p_sel), None)
            
            with st.form("f_produto", clear_on_submit=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                desc = c1.text_input("Descrição", value=item_ed['descricao'] if item_ed else "")
                unid = c2.text_input("Unidade", value=item_ed['unidade'] if item_ed else "UN")
                prec = c3.number_input("Preço Venda", value=float(item_ed['preco_venda'] or 0.0) if item_ed else 0.0)
                
                btn_txt = "💾 SALVAR ALTERAÇÕES" if item_ed else "➕ CADASTRAR PRODUTO"
                if st.form_submit_button(btn_txt):
                    pld = {"descricao": desc, "unidade": unid, "preco_venda": prec}
                    if item_ed: supabase.table("produtos").update(pld).eq("id", item_ed['id']).execute()
                    else: supabase.table("produtos").insert(pld).execute()
                    st.success("Operação realizada!"); time.sleep(1); st.rerun()

            if item_ed:
                if st.button("🗑️ EXCLUIR ESTE PRODUTO DEFINITIVAMENTE"):
                    supabase.table("produtos").delete().eq("id", item_ed['id']).execute()
                    st.rerun()

    # --- ABA: CLIENTES (CONTROLE TOTAL) ---
    elif menu == "👥 Gestão de Clientes":
        st.header("👥 Controle Total de Clientes")
        tab_c1, tab_c2 = st.tabs(["📋 Lista de Clientes", "🛠️ Adicionar ou Corrigir"])
        
        with tab_c1:
            if not df_c.empty: st.dataframe(df_c, use_container_width=True, hide_index=True)
        
        with tab_c2:
            opcoes_c = ["Novo Cliente"] + [f"{c['id']} - {c['nome_completo']}" for c in df_c.to_dict('records')]
            c_sel = st.selectbox("Selecione para EDITAR", opcoes_c)
            cli_ed = next((c for c in df_c.to_dict('records') if str(c['id']) in c_sel), None)
            
            with st.form("f_cliente"):
                nom = st.text_input("Nome Completo", value=cli_ed['nome_completo'] if cli_ed else "")
                doc = st.text_input("CPF ou CNPJ", value=cli_ed['cpf_cnpj'] if cli_ed else "")
                end = st.text_input("Endereço Completo", value=cli_ed['endereco'] if cli_ed else "")
                if st.form_submit_button("💾 SALVAR DADOS"):
                    pld_c = {"nome_completo": nom, "cpf_cnpj": doc, "endereco": end}
                    if cli_ed: supabase.table("Clientes").update(pld_c).eq("id", cli_ed['id']).execute()
                    else: supabase.table("Clientes").insert(pld_c).execute()
                    st.success("Dados salvos!"); time.sleep(1); st.rerun()

            if cli_ed:
                if st.button("🗑️ EXCLUIR CLIENTE"):
                    supabase.table("Clientes").delete().eq("id", cli_ed['id']).execute()
                    st.rerun()

    # --- ABA: AJUSTES & CONTROLE (DADOS FIXOS DA EMPRESA) ---
    elif menu == "⚙️ Ajustes & Controle":
        st.header("⚙️ Configurações e Identidade")
        with st.form("f_empresa"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Nome da Empresa (Razão/Fantasia)", value=emp.get('nome', ''))
            cn = c2.text_input("CNPJ", value=emp.get('cnpj', ''))
            e = st.text_input("Endereço Completo (Rua, Bairro, CEP, Cidade, UF)", value=emp.get('end', ''))
            t = st.text_input("Telefone / WhatsApp", value=emp.get('wts', ''))
            logo = st.file_uploader("Trocar Logomarca (PNG)", type=["png"])
            if st.form_submit_button("💾 FIXAR DADOS E IDENTIDADE"):
                l_b64 = emp.get('logo_base64', '')
                if logo: l_b64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                pld_e = {"id": 1, "nome": n, "cnpj": cn, "end": e, "wts": t, "logo_base64": l_b64}
                supabase.table("config").upsert(pld_e).execute()
                st.success("Identidade Fixada!"); time.sleep(1); st.rerun()

        st.divider()
        st.subheader("🛑 ZONA DE RESET (Limpeza por Fase)")
        r1, r2, r3 = st.columns(3)
        if r1.button("🗑️ Zerar Estoque"): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if r2.button("🗑️ Zerar Clientes"): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if r3.button("🔥 RESET TOTAL"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
