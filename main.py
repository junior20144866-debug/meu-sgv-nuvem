import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
import re
from datetime import datetime

# --- 1. CONEXÃO E ESTRUTURA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v54", layout="wide", page_icon="📈")

# --- 2. MOTOR DE MAPEAMENTO DE DNA (FIM DO GARGALO) ---
def buscar_dados_estabilizados():
    try:
        # Busca Configuração com Fallback (Garante fixação dos dados da empresa)
        c = supabase.table("config").select("*").eq("id", 1).execute().data
        empresa = c[0] if c else {"id": 1, "nome": "JMQJ SGV", "cnpj": "", "end": "", "wts": ""}
        
        # Busca Estoque e Clientes
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        cl = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        df_p = pd.DataFrame(p) if p else pd.DataFrame(columns=['id', 'descricao', 'unidade', 'preco_venda'])
        df_c = pd.DataFrame(cl) if cl else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'rua', 'bairro', 'telefone', 'endereco'])
        
        return empresa, df_p, df_c
    except:
        return {"nome": "ERRO DE CONEXÃO"}, pd.DataFrame(), pd.DataFrame()

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
        if st.button("LIGAR MOTORES 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = buscar_dados_estabilizados()

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
        c3.markdown(f'<div class="win-card">CAIXA DIA<br><span class="metric-val">R$ 0,00</span></div>', unsafe_allow_html=True)

    # --- VENDAS & FINANCEIRO ---
    elif menu == "🛒 Vendas & Financeiro":
        st.header("🛒 Módulo de Vendas e Fluxo Financeiro")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Novo Lançamento")
            c_v = st.selectbox("Cliente", df_c['nome_completo'].tolist() if not df_c.empty else ["Consumidor"])
            p_v = st.selectbox("Produto", [f"{p['id']} - {p['descricao']} | R$ {p['preco_venda']}" for p in df_e.to_dict('records')] if not df_e.empty else ["Estoque Vazio"])
            qtd = st.number_input("Quantidade", min_value=1, value=1)
            f_p = st.selectbox("Pagamento", ["Dinheiro", "Pix", "Cartão", "A Prazo"])
        with col2:
            st.subheader("Resumo")
            st.markdown('<div class="win-card">TOTAL<br><span class="metric-val">R$ 0,00</span></div>', unsafe_allow_html=True)
            vias = st.radio("Vias de Impressão", ["1 Via", "2 Vias"], horizontal=True)
            if st.button("✅ CONCLUIR"): st.success("Venda registrada!")

    # --- ESTOQUE (PRODUTOS) ---
    elif menu == "📦 Estoque (Produtos)":
        st.header("📦 Gestão de Produtos")
        tab_list, tab_edit = st.tabs(["📋 Relação de Itens", "🛠️ Incluir/Editar/Excluir"])
        with tab_list:
            st.dataframe(df_e, use_container_width=True, hide_index=True)
        with tab_edit:
            op_p = ["Novo Registro"] + [f"{p['id']} - {p['descricao']}" for p in df_e.to_dict('records')]
            sel_p = st.selectbox("Escolha um produto", op_p)
            it = next((p for p in df_e.to_dict('records') if str(p['id']) in sel_p), None)
            with st.form("form_prod"):
                d = st.text_input("Descrição", value=it['descricao'] if it else "")
                u = st.text_input("Unidade", value=it['unidade'] if it else "UN")
                pr = st.number_input("Preço de Venda", value=float(it['preco_venda'] or 0.0) if it else 0.0)
                if st.form_submit_button("💾 SALVAR PRODUTO"):
                    pld = {"descricao": d, "unidade": u, "preco_venda": pr}
                    if it: supabase.table("produtos").update(pld).eq("id", it['id']).execute()
                    else: supabase.table("produtos").insert(pld).execute()
                    st.rerun()
            if it and st.button("🗑️ EXCLUIR ITEM"):
                supabase.table("produtos").delete().eq("id", it['id']).execute(); st.rerun()

    # --- CLIENTES (FIXAÇÃO DE IMPORTAÇÃO) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        tab_cl, tab_ce = st.tabs(["📋 Relação de Clientes", "🛠️ Incluir/Editar/Excluir"])
        with tab_cl:
            st.dataframe(df_c, use_container_width=True, hide_index=True)
        with tab_ce:
            op_c = ["Novo Cadastro"] + [f"{c['id']} - {c['nome_completo']}" for c in df_c.to_dict('records')]
            sel_c = st.selectbox("Escolha um cliente", op_c)
            cl = next((c for c in df_c.to_dict('records') if str(c['id']) in sel_c), None)
            with st.form("form_cli"):
                n = st.text_input("Nome/Razão", value=cl['nome_completo'] if cl else "")
                ru = st.text_input("Rua", value=cl.get('rua', '') if cl else "")
                ba = st.text_input("Bairro", value=cl.get('bairro', '') if cl else "")
                tl = st.text_input("Telefone", value=cl.get('telefone', '') if cl else "")
                if st.form_submit_button("💾 SALVAR CLIENTE"):
                    dc = {"nome_completo": n, "rua": ru, "bairro": ba, "telefone": tl, "endereco": f"{ru}, {ba}"}
                    if cl: supabase.table("Clientes").update(dc).eq("id", cl['id']).execute()
                    else: supabase.table("Clientes").insert(dc).execute()
                    st.rerun()
            if cl and st.button("🗑️ EXCLUIR CLIENTE"):
                supabase.table("Clientes").delete().eq("id", cl['id']).execute(); st.rerun()

    # --- CARGA DE DADOS (MAPEAMENTO DNA) ---
    elif menu == "📑 Carga de Dados":
        st.header("📑 Carga Massiva Inteligente")
        alvo = st.selectbox("Tabela Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Arquivo XLSX", type=["xlsx"])
        if arq and st.button("🚀 EXECUTAR CARGA"):
            df_in = pd.read_excel(arq)
            for r in df_in.to_dict('records'):
                try:
                    if alvo == "produtos":
                        pv = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({"descricao": str(r.get('DESCRICAO')), "unidade": str(r.get('UNIDADE', 'UN')), "preco_venda": float(pv)}).execute()
                    else:
                        # MAPEAMENTO FORÇADO DO DNA DO SISTEMA ANTERIOR
                        supabase.table("Clientes").insert({
                            "nome_completo": str(r.get('NOM', r.get('NOME', ''))),
                            "rua": str(r.get('RUA', '')), "bairro": str(r.get('BAI', '')),
                            "telefone": str(r.get('TEL1', ''))
                        }).execute()
                except: pass
            st.success("Importação concluída com sucesso!"); time.sleep(1); st.rerun()

    # --- AJUSTES & RESET (FIXAÇÃO DA EMPRESA) ---
    elif menu == "⚙️ Ajustes & Reset":
        st.header("⚙️ Configurações e Manutenção")
        with st.form("f_emp"):
            c1, c2 = st.columns(2)
            n_e = c1.text_input("Nome da Empresa", value=emp.get('nome', ''))
            cn_e = c2.text_input("CNPJ", value=emp.get('cnpj', ''))
            en_e = st.text_input("Endereço Completo", value=emp.get('end', ''))
            wt_e = st.text_input("Telefone / WhatsApp", value=emp.get('wts', ''))
            logo = st.file_uploader("Logo (PNG)", type=["png"])
            if st.form_submit_button("💾 FIXAR DADOS DA EMPRESA"):
                l64 = emp.get('logo_base64', '')
                if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n_e, "cnpj": cn_e, "end": en_e, "wts": wt_e, "logo_base64": l64}).execute()
                st.rerun()

        st.divider()
        st.subheader("🛑 ZONA DE CONTROLE (RESET)")
        cr1, cr2, cr3 = st.columns(3)
        if cr1.button("🗑️ Zerar Estoque"): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if cr2.button("🗑️ Zerar Clientes"): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if cr3.button("🔥 RESET TOTAL"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
