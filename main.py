import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
import re

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v56", layout="wide", page_icon="📈")

# --- 2. MOTOR DE PERSISTÊNCIA (O FIM DO GARGALO) ---
def buscar_dados_v56():
    try:
        # Busca Configuração (Força o ID 1)
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        empresa = c[0] if c else {"id": 1, "nome": "JMQJ SGV"}
        
        # Busca Produtos e Clientes
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        cl = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'unidade', 'preco_venda'])
        # Garantimos que 'nome_completo' seja a chave de visualização
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'rua', 'bairro', 'telefone'])
        
        return empresa, df_p, df_c
    except:
        return {"nome": "JMQJ SGV"}, pd.DataFrame(), pd.DataFrame()

# --- 3. ESTILO VISUAL WINDOWS 11 ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .win-card {
        background: white; padding: 22px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 5px solid #0078D4;
        text-align: center; margin-bottom: 15px;
    }
    .metric-val { font-size: 2.3rem; font-weight: bold; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #0078D4;'>JMQJ SGV SISTEMAS</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR OPERAÇÃO 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = buscar_dados_v56()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'JMQJ SGV'))
        st.write("---")
        menu = st.radio("MÓDULOS", ["🏠 Dashboard", "🛒 Vendas & Financeiro", "📦 Estoque (Produtos)", "👥 Clientes", "📑 Carga de Dados", "⚙️ Ajustes & Reset"])

    # --- DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel Operacional | {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-card">PRODUTOS<br><span class="metric-val">{len(df_e)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-card">CLIENTES<br><span class="metric-val">{len(df_c)}</span></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-card">VENDAS DIA<br><span class="metric-val">0</span></div>', unsafe_allow_html=True)

    # --- ESTOQUE (FIXAÇÃO DA INCLUSÃO MANUAL) ---
    elif menu == "📦 Estoque (Produtos)":
        st.header("📦 Gestão de Produtos")
        tab_l, tab_e = st.tabs(["📋 Relação", "🛠️ Controle Manual"])
        with tab_l:
            st.dataframe(df_e, use_container_width=True, hide_index=True)
        with tab_e:
            op_p = ["Novo Cadastro"] + [f"{p['id']} - {p['descricao']}" for p in df_e.to_dict('records')]
            sel_p = st.selectbox("Escolha um produto", op_p)
            it = next((p for p in df_e.to_dict('records') if str(p['id']) in sel_p), None)
            with st.form("f_p", clear_on_submit=True):
                d = st.text_input("Descrição", value=it['descricao'] if it else "")
                u = st.text_input("Unidade", value=it['unidade'] if it else "UN")
                p = st.number_input("Preço", value=float(it['preco_venda'] or 0.0) if it else 0.0)
                if st.form_submit_button("💾 SALVAR PRODUTO"):
                    if it: # Atualizar existente
                        supabase.table("produtos").update({"descricao": d, "unidade": u, "preco_venda": p}).eq("id", it['id']).execute()
                    else: # Novo registro (Sem enviar ID para o banco gerar)
                        supabase.table("produtos").insert({"descricao": d, "unidade": u, "preco_venda": p}).execute()
                    st.success("Produto salvo!"); time.sleep(1); st.rerun()

    # --- CLIENTES (FIXAÇÃO DA CARGA E INCLUSÃO MANUAL) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        tab_cl, tab_ce = st.tabs(["📋 Relação de Clientes", "🛠️ Controle Manual"])
        with tab_cl:
            if not df_c.empty:
                st.dataframe(df_c, use_container_width=True, hide_index=True)
            else:
                st.info("Lista de clientes vazia. Realize a Carga de Dados.")
        with tab_ce:
            op_c = ["Novo Cadastro"] + [f"{c['id']} - {c['nome_completo']}" for c in df_c.to_dict('records')]
            sel_c = st.selectbox("Escolha um cliente", op_c)
            cl = next((c for c in df_c.to_dict('records') if str(c['id']) in sel_c), None)
            with st.form("f_c", clear_on_submit=True):
                n = st.text_input("Nome/Razão", value=cl['nome_completo'] if cl else "")
                ru = st.text_input("Rua", value=cl.get('rua', '') if cl else "")
                ba = st.text_input("Bairro", value=cl.get('bairro', '') if cl else "")
                tl = st.text_input("Telefone", value=cl.get('telefone', '') if cl else "")
                if st.form_submit_button("💾 SALVAR CLIENTE"):
                    dados_c = {"nome_completo": n, "rua": ru, "bairro": ba, "telefone": tl}
                    if cl: supabase.table("Clientes").update(dados_c).eq("id", cl['id']).execute()
                    else: supabase.table("Clientes").insert(dados_c).execute()
                    st.success("Cliente fixado!"); time.sleep(1); st.rerun()

    # --- CARGA DE DADOS (DNA ROBUSTO) ---
    elif menu == "📑 Carga de Dados":
        st.header("📑 Carga Massiva")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Arquivo XLSX", type=["xlsx"])
        if arq and st.button("🚀 EXECUTAR CARGA"):
            df_in = pd.read_excel(arq)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        pv = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({"descricao": str(r.get('DESCRICAO')), "unidade": str(r.get('UNIDADE', 'UN')), "preco_venda": float(pv)}).execute()
                    else:
                        # Mapeamento DNA Siscom -> JMQJ SGV (NOM, RUA, BAI, TEL1)
                        supabase.table("Clientes").insert({
                            "nome_completo": str(r.get('NOM', r.get('NOME', ''))),
                            "rua": str(r.get('RUA', '')), "bairro": str(r.get('BAI', '')),
                            "telefone": str(r.get('TEL1', ''))
                        }).execute()
                except: pass
            st.success("Carga realizada com sucesso!"); time.sleep(1); st.rerun()

    # --- AJUSTES & RESET (FIXAÇÃO DA EMPRESA) ---
    elif menu == "⚙️ Ajustes & Reset":
        st.header("⚙️ Identidade da Empresa")
        with st.form("f_emp"):
            c1, c2 = st.columns(2)
            n_e = c1.text_input("Nome Empresa", value=emp.get('nome', ''))
            cn_e = c2.text_input("CNPJ", value=emp.get('cnpj', ''))
            en_e = st.text_input("Endereço", value=emp.get('end', ''))
            wt_e = st.text_input("WhatsApp", value=emp.get('wts', ''))
            logo = st.file_uploader("Logo PNG", type=["png"])
            if st.form_submit_button("💾 FIXAR DADOS DA EMPRESA"):
                l64 = emp.get('logo_base64', '')
                if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                # O Segredo da fixação: Upsert forçado no ID 1
                supabase.table("config").upsert({"id": 1, "nome": n_e, "cnpj": cn_e, "end": en_e, "wts": wt_e, "logo_base64": l64}).execute()
                st.success("Dados cravados no sistema!"); time.sleep(1); st.rerun()

        st.divider()
        st.subheader("🛑 ZONA DE RESET (CONTROLE TOTAL)")
        cr1, cr2, cr3 = st.columns(3)
        if cr1.button("🗑️ Zerar Estoque"): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if cr2.button("🗑️ Zerar Clientes"): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if cr3.button("🔥 RESET TOTAL"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
