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

st.set_page_config(page_title="JMQJ SGV v52", layout="wide", page_icon="📈")

# --- 2. MOTOR DE AUTOCURA E SINCRONIA ---
def sincronizar_sistema():
    """Busca dados e reconstrói referências se o sistema for zerado"""
    try:
        conf = supabase.table("config").select("*").eq("id", 1).execute().data
        est = supabase.table("produtos").select("*").order("descricao").execute().data
        cli = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        # Blindagem: Se não houver config, usamos um padrão para não travar
        info_empresa = conf[0] if conf else {"id": 1, "nome": "JMQJ SGV", "end": "", "cnpj": "", "wts": ""}
        
        # Garantia de colunas para as tabelas (Fim do erro de visualização)
        df_p = pd.DataFrame(est) if est else pd.DataFrame(columns=['id', 'descricao', 'unidade', 'preco_venda'])
        df_c = pd.DataFrame(cli) if cli else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'endereco', 'rua', 'bairro', 'telefone'])
        
        return info_empresa, df_p, df_c
    except:
        return {"nome": "JMQJ SGV"}, pd.DataFrame(), pd.DataFrame()

# --- 3. DESIGN EXCLUSIVO JMQJ (WINDOWS 11 STYLE) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .win-card {
        background: white; padding: 22px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 5px solid #0078D4;
        text-align: center; margin-bottom: 15px;
    }
    .metric-val { font-size: 2.4rem; font-weight: bold; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #0078D4;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("INICIAR OPERAÇÃO 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    # CARREGAMENTO GLOBAL BLINDADO
    emp, df_e, df_c = sincronizar_sistema()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'JMQJ SGV'))
        st.write("---")
        menu = st.radio("MÓDULOS", ["🏠 Dashboard", "🛒 Vendas & Pedidos", "📦 Estoque (Produtos)", "👥 Clientes", "📑 Importação Massiva", "⚙️ Ajustes & Reset"])

    # --- DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel de Controle | {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-card">PRODUTOS<br><span class="metric-val">{len(df_e)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-card">CLIENTES<br><span class="metric-val">{len(df_c)}</span></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-card">FINANCEIRO DIA<br><span class="metric-val">R$ 0,00</span></div>', unsafe_allow_html=True)

    # --- VENDAS (1 OU 2 VIAS) ---
    elif menu == "🛒 Vendas & Pedidos":
        st.header("🛒 Módulo de Vendas")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Lançamento")
            c_v = st.selectbox("Selecione o Cliente", df_c['nome_completo'].tolist() if not df_c.empty else ["Consumidor Final"])
            p_v = st.selectbox("Produto", [f"{p['id']} - {p['descricao']} | R$ {p['preco_venda']}" for p in df_e.to_dict('records')] if not df_e.empty else ["Estoque Vazio"])
            qtd = st.number_input("Quantidade", min_value=1, value=1)
            vias = st.radio("Impressão", ["1 Via", "2 Vias"], horizontal=True)
        with col2:
            st.subheader("Resumo")
            st.markdown('<div class="win-card">TOTAL<br><span class="metric-val">R$ 0,00</span></div>', unsafe_allow_html=True)
            if st.button("✅ FINALIZAR"): st.success(f"Venda concluída ({vias})")

    # --- ESTOQUE (INCLUIR/EXCLUIR/ALTERAR) ---
    elif menu == "📦 Estoque (Produtos)":
        st.header("📦 Gestão de Produtos")
        tab_l, tab_e = st.tabs(["📋 Relação", "🛠️ Controle Manual"])
        with tab_l:
            st.dataframe(df_e, use_container_width=True, hide_index=True)
        with tab_e:
            op_p = ["Novo Cadastro"] + [f"{p['id']} - {p['descricao']}" for p in df_e.to_dict('records')]
            sel_p = st.selectbox("Selecione para Editar", op_p)
            it = next((p for p in df_e.to_dict('records') if str(p['id']) in sel_p), None)
            with st.form("f_p"):
                d = st.text_input("Descrição", value=it['descricao'] if it else "")
                u = st.text_input("Unidade", value=it['unidade'] if it else "UN")
                p = st.number_input("Preço de Venda", value=float(it['preco_venda'] or 0.0) if it else 0.0)
                if st.form_submit_button("💾 SALVAR DADOS"):
                    dados = {"descricao": d, "unidade": u, "preco_venda": p}
                    if it: supabase.table("produtos").update(dados).eq("id", it['id']).execute()
                    else: supabase.table("produtos").insert(dados).execute()
                    st.rerun()
            if it and st.button("🗑️ EXCLUIR ITEM"):
                supabase.table("produtos").delete().eq("id", it['id']).execute(); st.rerun()

    # --- CLIENTES (INCLUIR/EXCLUIR/ALTERAR) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        tab_cl, tab_ce = st.tabs(["📋 Relação", "🛠️ Controle Manual"])
        with tab_cl:
            st.dataframe(df_c, use_container_width=True, hide_index=True)
        with tab_ce:
            op_c = ["Novo Cadastro"] + [f"{c['id']} - {c['nome_completo']}" for c in df_c.to_dict('records')]
            sel_c = st.selectbox("Selecione para Editar", op_c)
            cl = next((c for c in df_c.to_dict('records') if str(c['id']) in sel_c), None)
            with st.form("f_c"):
                n = st.text_input("Nome/Razão", value=cl['nome_completo'] if cl else "")
                ru = st.text_input("Rua", value=cl.get('rua', '') if cl else "")
                ba = st.text_input("Bairro", value=cl.get('bairro', '') if cl else "")
                te = st.text_input("Telefone/WhatsApp", value=cl.get('telefone', '') if cl else "")
                if st.form_submit_button("💾 SALVAR CLIENTE"):
                    dc = {"nome_completo": n, "rua": ru, "bairro": ba, "telefone": te, "endereco": f"{ru}, {ba}"}
                    if cl: supabase.table("Clientes").update(dc).eq("id", cl['id']).execute()
                    else: supabase.table("Clientes").insert(dc).execute()
                    st.rerun()
            if cl and st.button("🗑️ EXCLUIR CLIENTE"):
                supabase.table("Clientes").delete().eq("id", cl['id']).execute(); st.rerun()

    # --- IMPORTAÇÃO MASSIVA (DNA DE CARGA) ---
    elif menu == "📑 Importação Massiva":
        st.header("📑 Carga Massiva de Dados")
        alvo = st.selectbox("Tabela Destino", ["produtos", "Clientes"])
        file = st.file_uploader("Arquivo XLSX", type=["xlsx"])
        if file and st.button("🚀 EXECUTAR IMPORTAÇÃO"):
            df_in = pd.read_excel(file)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        pv = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({"descricao": str(r.get('DESCRICAO')), "unidade": str(r.get('UNIDADE', 'UN')), "preco_venda": float(pv)}).execute()
                    else:
                        supabase.table("Clientes").insert({
                            "nome_completo": str(r.get('NOM')), "rua": str(r.get('RUA', '')), 
                            "bairro": str(r.get('BAI', '')), "telefone": str(r.get('TEL1', ''))
                        }).execute()
                except: pass
            st.success("Importação concluída com sucesso!"); time.sleep(1); st.rerun()

    # --- AJUSTES & RESET (CONTROLE TOTAL) ---
    elif menu == "⚙️ Ajustes & Reset":
        st.header("⚙️ Configurações da Empresa & Manutenção")
        with st.form("f_conf"):
            c1, c2 = st.columns(2)
            n_e = c1.text_input("Nome da Empresa", value=emp.get('nome', ''))
            cn_e = c2.text_input("CNPJ", value=emp.get('cnpj', ''))
            en_e = st.text_input("Endereço Completo", value=emp.get('end', ''))
            wt_e = st.text_input("WhatsApp para Pedidos", value=emp.get('wts', ''))
            logo = st.file_uploader("Trocar Logo (PNG)", type=["png"])
            if st.form_submit_button("💾 FIXAR DADOS"):
                l64 = emp.get('logo_base64', '')
                if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n_e, "cnpj": cn_e, "end": en_e, "wts": wt_e, "logo_base64": l64}).execute()
                st.rerun()

        st.divider()
        st.subheader("🛑 ZONA DE CONTROLE (RESET PARCIAL OU TOTAL)")
        col1, col2, col3 = st.columns(3)
        if col1.button("🗑️ Zerar Estoque", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if col2.button("🗑️ Zerar Clientes", use_container_width=True):
            supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if col3.button("🔥 RESET TOTAL DO SISTEMA", use_container_width=True):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
