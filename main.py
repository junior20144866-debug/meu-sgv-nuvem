import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

# --- 2. MOTOR DE LEITURA (VERDADE ÚNICA) ---
def db_read(tabela):
    try:
        res = supabase.table(tabela).select("*").order("id", desc=True).execute()
        return res.data if res.data else []
    except: return []

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .win-tile {
        background: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-top: 6px solid #0078D4;
        text-align: center; margin-bottom: 20px;
    }
    .tile-num { font-size: 2.8rem; font-weight: 800; color: #0078D4; margin: 0; }
    .tile-label { font-weight: bold; color: #555; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CONTROLE DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #0078D4;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("LIGAR SISTEMA 🚀", use_container_width=True):
            if senha == "Naksu@6026":
                st.session_state.auth = True
                st.rerun()
else:
    # CARREGAMENTO GLOBAL
    config_db = db_read("config")
    emp = config_db[0] if config_db else {}
    estoque = db_read("produtos")
    clientes = db_read("Clientes")

    # BARRA LATERAL (IDENTIDADE FIXA)
    with st.sidebar:
        # LOGOMARCA (Se houver URL no banco, exibe)
        if emp.get('logo_base64'):
            st.image(emp['logo_base64'], use_container_width=True)
        
        st.title(emp.get('nome', 'JMQJ SGV'))
        st.caption(f"CNPJ: {emp.get('cnpj', 'Não definido')}")
        st.write("---")
        menu = st.radio("NAVEGAÇÃO", ["🏠 Dashboard", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Configurações"])

    # --- ABA: DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel Operacional | {emp.get('nome', 'SGV')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-tile"><p class="tile-label">Produtos</p><p class="tile-num">{len(estoque)}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile"><p class="tile-label">Clientes</p><p class="tile-num">{len(clientes)}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile"><p class="tile-label">Vendas</p><p class="tile-num">0</p></div>', unsafe_allow_html=True)

    # --- ABA: ESTOQUE E CLIENTES (CADASTRO) ---
    elif menu in ["📦 Estoque", "👥 Clientes"]:
        tab = "produtos" if menu == "📦 Estoque" else "Clientes"
        st.header(f"Gestão de {menu}")
        
        with st.expander("📝 Cadastrar Novo / Editar"):
            with st.form("form_global"):
                id_reg = st.number_input("ID (0 para Novo)", min_value=0)
                if tab == "produtos":
                    desc = st.text_input("Descrição")
                    ean = st.text_input("Código EAN")
                    pr = st.number_input("Preço de Venda", format="%.2f")
                    pld = {"descricao": desc, "ean13": ean, "preco_venda": pr}
                else:
                    nome = st.text_input("Nome Completo")
                    doc = st.text_input("CPF/CNPJ")
                    end = st.text_input("Endereço")
                    pld = {"nome_completo": nome, "cpf_cnpj": doc, "endereco": end}
                
                if st.form_submit_button("💾 SALVAR"):
                    if id_reg == 0: supabase.table(tab).insert(pld).execute()
                    else: supabase.table(tab).update(pld).eq("id", id_reg).execute()
                    st.rerun()

        dados = estoque if tab == "produtos" else clientes
        if dados:
            st.dataframe(pd.DataFrame(dados), use_container_width=True)
            id_del = st.number_input("ID para Deletar", min_value=0, key="del_btn")
            if st.button("🗑️ Confirmar Exclusão"):
                supabase.table(tab).delete().eq("id", id_del).execute()
                st.rerun()

    # --- ABA: IMPORTAÇÃO ---
    elif menu == "📑 Importação":
        st.header("📑 Importação XLSX")
        alvo = st.selectbox("Escolha o destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Arquivo Excel", type=["xlsx"])
        if arq and st.button("🚀 EXECUTAR CARGA"):
            df = pd.read_excel(arq)
            for _, row in df.iterrows():
                try:
                    if alvo == "produtos":
                        p_val = str(row.get('P_VENDA', 0)).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        item = {"descricao": str(row.get('DESCRICAO')), "preco_venda": float(p_val), "ean13": str(row.get('CODIGO'))}
                    else:
                        item = {"nome_completo": str(row.get('NOM')), "cpf_cnpj": str(row.get('CGC')), "endereco": str(row.get('RUA'))}
                    supabase.table(alvo).insert(item).execute()
                except: pass
            st.success("Carga realizada!"); time.sleep(1); st.rerun()

    # --- ABA: CONFIGURAÇÕES (RESETS E LOGO) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Identidade e Manutenção")
        
        with st.form("form_config"):
            st.subheader("Dados da Empresa")
            n = st.text_input("Nome da Empresa", value=emp.get('nome', ''))
            c = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            l = st.text_input("URL da Logomarca (Link da imagem)", value=emp.get('logo_base64', ''))
            st.caption("Dica: Hospede sua logo em sites como imgbb.com e cole o link direto aqui.")
            
            if st.form_submit_button("💾 FIXAR TUDO"):
                supabase.table("config").upsert({"id": 1, "nome": n, "cnpj": c, "logo_base64": l}).execute()
                st.success("Dados fixados!"); time.sleep(1); st.rerun()

        st.divider()
        st.subheader("🗑️ ZONA DE RESET (Limpeza Total)")
        col1, col2, col3 = st.columns(3)
        if col1.button("🗑️ ZERAR ESTOQUE"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            st.rerun()
        if col2.button("🗑️ ZERAR CLIENTES"):
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.rerun()
        if col3.button("🔥 RESET TOTAL SISTEMA"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute()
            st.rerun()
