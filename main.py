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

st.set_page_config(page_title="JMQJ SGV v50", layout="wide", page_icon="📈")

# --- 2. MOTOR DE BLINDAGEM (O FIM DO EFEITO SANFONA) ---
def carregar_dados_seguros():
    """Busca dados e garante que o sistema não trave se as tabelas estiverem zeradas"""
    try:
        conf = supabase.table("config").select("*").eq("id", 1).execute().data
        est = supabase.table("produtos").select("*").order("descricao").execute().data
        cli = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        # Se zerou tudo, cria um dicionário vazio para não dar erro de 'None'
        empresa = conf[0] if conf else {"id": 1, "nome": "SGV SISTEMAS", "end": "", "cnpj": "", "wts": ""}
        df_p = pd.DataFrame(est) if est else pd.DataFrame(columns=['id', 'descricao', 'unidade', 'preco_venda'])
        df_c = pd.DataFrame(cli) if cli else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'endereco', 'rua', 'bairro', 'cidade', 'uf', 'telefone'])
        
        return empresa, df_p, df_c
    except:
        return {"nome": "ERRO DE CONEXÃO"}, pd.DataFrame(), pd.DataFrame()

# --- 3. DESIGN WINDOWS 11 ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .win-card {
        background: white; padding: 22px; border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 6px solid #0078D4;
        text-align: center; margin-bottom: 15px;
    }
    .metric-val { font-size: 2.3rem; font-weight: bold; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR MOTORES 🚀", use_container_width=True):
            if senha == "Naksu@6026": st.session_state.auth = True; st.rerun()
else:
    emp, df_e, df_c = carregar_dados_seguros()

    with st.sidebar:
        if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'SGV'))
        st.write("---")
        menu = st.radio("SISTEMA", ["🏠 Dashboard", "🛒 Vendas & Pedidos", "📦 Estoque (Produtos)", "👥 Clientes", "📑 Importação", "⚙️ Ajustes & Reset"])

    # --- DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Centro de Comando | {emp.get('nome')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-card">PRODUTOS<br><span class="metric-val">{len(df_e)}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-card">CLIENTES<br><span class="metric-val">{len(df_c)}</span></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-card">PEDIDOS HOJE<br><span class="metric-val">0</span></div>', unsafe_allow_html=True)

    # --- ABA: VENDAS (LAYOUT IMPRESSÃO) ---
    elif menu == "🛒 Vendas & Pedidos":
        st.header("🛒 Módulo de Vendas")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Carrinho")
            c_v = st.selectbox("Cliente", df_c['nome_completo'].tolist() if not df_c.empty else ["Consumidor Final"])
            p_v = st.selectbox("Produto", [f"{p['id']} - {p['descricao']} | R$ {p['preco_venda']}" for p in df_e.to_dict('records')] if not df_e.empty else ["Vazio"])
            qtd = st.number_input("Qtd", min_value=1, value=1)
            vias = st.radio("Vias de Impressão", ["1 Via", "2 Vias"], horizontal=True)
        with col2:
            st.subheader("Totalizador")
            st.markdown('<div class="win-card">VALOR TOTAL<br><span class="metric-val">R$ 0,00</span></div>', unsafe_allow_html=True)
            if st.button("✅ FINALIZAR VENDA"): st.balloons()

    # --- ABA: ESTOQUE (CONTROLE TOTAL) ---
    elif menu == "📦 Estoque (Produtos)":
        st.header("📦 Gestão de Produtos")
        tab_list, tab_edit = st.tabs(["📋 Listagem", "🛠️ Incluir/Alterar"])
        with tab_list:
            st.dataframe(df_e, use_container_width=True, hide_index=True)
        with tab_edit:
            opcoes_p = ["Novo Registro"] + [f"{p['id']} - {p['descricao']}" for p in df_e.to_dict('records')]
            sel_p = st.selectbox("Selecione para Editar", opcoes_p)
            item_ed = next((p for p in df_e.to_dict('records') if str(p['id']) in sel_p), None)
            with st.form("form_prod"):
                d = st.text_input("Descrição", value=item_ed['descricao'] if item_ed else "")
                u = st.text_input("Unidade", value=item_ed['unidade'] if item_ed else "UN")
                pr = st.number_input("Preço", value=float(item_ed['preco_venda'] or 0.0) if item_ed else 0.0)
                if st.form_submit_button("💾 SALVAR PRODUTO"):
                    pld = {"descricao": d, "unidade": u, "preco_venda": pr}
                    if item_ed: supabase.table("produtos").update(pld).eq("id", item_ed['id']).execute()
                    else: supabase.table("produtos").insert(pld).execute()
                    st.rerun()
            if item_ed:
                if st.button("🗑️ EXCLUIR PRODUTO"):
                    supabase.table("produtos").delete().eq("id", item_ed['id']).execute(); st.rerun()

    # --- ABA: CLIENTES (CONTROLE TOTAL) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        tab_clist, tab_cedit = st.tabs(["📋 Listagem", "🛠️ Incluir/Alterar"])
        with tab_clist:
            st.dataframe(df_c, use_container_width=True, hide_index=True)
        with tab_cedit:
            opcoes_c = ["Novo Cliente"] + [f"{c['id']} - {c['nome_completo']}" for c in df_c.to_dict('records')]
            sel_c = st.selectbox("Selecione para Editar", opcoes_c)
            cli_ed = next((c for c in df_c.to_dict('records') if str(c['id']) in sel_c), None)
            with st.form("form_cli"):
                n = st.text_input("Nome", value=cli_ed['nome_completo'] if cli_ed else "")
                r = st.text_input("Rua", value=cli_ed.get('rua', '') if cli_ed else "")
                b = st.text_input("Bairro", value=cli_ed.get('bairro', '') if cli_ed else "")
                t = st.text_input("Telefone", value=cli_ed.get('telefone', '') if cli_ed else "")
                if st.form_submit_button("💾 SALVAR CLIENTE"):
                    pld_c = {"nome_completo": n, "rua": r, "bairro": b, "telefone": t, "endereco": f"{r}, {b}"}
                    if cli_ed: supabase.table("Clientes").update(pld_c).eq("id", cli_ed['id']).execute()
                    else: supabase.table("Clientes").insert(pld_c).execute()
                    st.rerun()

    # --- ABA: IMPORTAÇÃO (BLINDADA) ---
    elif menu == "📑 Importação":
        st.header("📑 Carga Massiva")
        alvo = st.selectbox("Tabela", ["produtos", "Clientes"])
        file = st.file_uploader("Arquivo XLSX", type=["xlsx"])
        if file and st.button("🚀 IMPORTAR"):
            df_in = pd.read_excel(file)
            rows = df_in.to_dict('records')
            for r in rows:
                try:
                    if alvo == "produtos":
                        p_raw = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        supabase.table("produtos").insert({"descricao": str(r.get('DESCRICAO')), "preco_venda": float(p_raw)}).execute()
                    else:
                        supabase.table("Clientes").insert({"nome_completo": str(r.get('NOM')), "rua": str(r.get('RUA')), "bairro": str(r.get('BAI')), "telefone": str(r.get('TEL1'))}).execute()
                except: pass
            st.success("Carga finalizada!"); time.sleep(1); st.rerun()

    # --- ABA: AJUSTES & RESET (CONTROLE TOTAL) ---
    elif menu == "⚙️ Ajustes & Reset":
        st.header("⚙️ Configurações & Resets")
        with st.form("f_emp"):
            nome_e = st.text_input("Empresa", value=emp.get('nome', ''))
            cnpj_e = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            end_e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logo", type=["png"])
            if st.form_submit_button("💾 FIXAR DADOS"):
                l_b64 = emp.get('logo_base64', '')
                if logo: l_b64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": nome_e, "cnpj": cnpj_e, "end": end_e, "logo_base64": l_b64}).execute()
                st.rerun()

        st.divider()
        st.subheader("🗑️ ZONA DE RESET (CONTROLADO)")
        c_r1, c_r2, c_r3 = st.columns(3)
        if c_r1.button("🗑️ Zerar Estoque"): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if c_r2.button("🗑️ Zerar Clientes"): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if c_r3.button("🔥 RESET TOTAL"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute(); st.rerun()
