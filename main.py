import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONEXÃO BLINDADA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

# --- 2. CSS WINDOWS PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .win-tile {
        background: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 5px solid #0078D4;
        text-align: center; margin-bottom: 20px;
    }
    .tile-val { font-size: 2rem; font-weight: 800; color: #0078D4; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES DE PERSISTÊNCIA (O FIM DA SANFONA) ---
def buscar_empresa():
    res = supabase.table("config").select("*").eq("id", 1).execute()
    return res.data[0] if res.data else {}

def listar(tabela):
    return supabase.table(tabela).select("*").execute().data

# --- 4. INTERFACE ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS</h1>", unsafe_allow_html=True)
    with st.container():
        _, col, _ = st.columns([1,1,1])
        with col:
            if st.text_input("Senha", type="password") == "Naksu@6026":
                if st.button("ACESSAR"): st.session_state.auth = True; st.rerun()
else:
    emp = buscar_empresa()
    menu = st.sidebar.radio("MENU", ["🏠 Início", "🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Configurações"])

    # --- ABA: INÍCIO (TILES) ---
    if menu == "🏠 Início":
        st.header(f"Gestão: {emp.get('nome', 'JMQJ')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-tile">📦 ESTOQUE<br><p class="tile-val">{len(listar("produtos"))}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile">👥 CLIENTES<br><p class="tile-val">{len(listar("Clientes"))}</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile">💰 VENDAS<br><p class="tile-val">0</p></div>', unsafe_allow_html=True)

    # --- ABA: ESTOQUE & CLIENTES (COM EDIÇÃO E ZERAR) ---
    elif menu in ["📦 Estoque", "👥 Clientes"]:
        tab = "produtos" if menu == "📦 Estoque" else "Clientes"
        st.header(f"{menu}")
        
        # INSERIR / EDITAR
        with st.expander("➕ Inserir/Editar Manualmente"):
            with st.form("form_dados"):
                id_edit = st.number_input("ID (Deixe 0 para novo, ou digite o ID para editar)", min_value=0)
                if tab == "produtos":
                    d, e, p = st.text_input("Descrição"), st.text_input("EAN"), st.number_input("Preço")
                    dados = {"descricao": d, "ean13": e, "preco_venda": p}
                else:
                    n, c, end = st.text_input("Nome"), st.text_input("CPF/CNPJ"), st.text_input("Endereço")
                    dados = {"nome_completo": n, "cpf_cnpj": c, "endereco": end}
                
                if st.form_submit_button("SALVAR"):
                    if id_edit == 0: supabase.table(tab).insert(dados).execute()
                    else: supabase.table(tab).update(dados).eq("id", id_edit).execute()
                    st.success("Operação realizada!"); st.rerun()

        # LISTA COM BOTÃO DE EXCLUIR POR LINHA
        df = pd.DataFrame(listar(tab))
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            id_del = st.number_input(f"ID para EXCLUIR de {menu}", min_value=0, key="del_box")
            if st.button("🗑️ Confirmar Exclusão"):
                supabase.table(tab).delete().eq("id", id_del).execute(); st.rerun()

    # --- ABA: IMPORTAÇÃO (CORRIGIDA) ---
    elif menu == "📑 Importação":
        st.header("📑 Importação em Massa")
        target = st.selectbox("Tabela Destino", ["produtos", "Clientes"])
        file = st.file_uploader("Arquivo Excel", type=["xlsx"])
        if file and st.button("🚀 IMPORTAR AGORA"):
            df_in = pd.read_excel(file)
            for _, row in df_in.iterrows():
                d = row.to_dict()
                # Mapeamento forçado para seus arquivos
                if target == "produtos":
                    ready = {"descricao": str(d.get('DESCRICAO', '')), "preco_venda": float(d.get('P_VENDA', 0)), "ean13": str(d.get('CODIGO', ''))}
                else:
                    ready = {"nome_completo": str(d.get('NOM', '')), "cpf_cnpj": str(d.get('CGC', '')), "endereco": str(d.get('RUA', ''))}
                
                supabase.table(target).insert(ready).execute()
            st.success("Importação concluída com sucesso!"); st.rerun()

    # --- ABA: CONFIGURAÇÕES (BOTÕES DE ZERAR E LOGO REPOSTOS) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Configurações e Controle Total")
        
        with st.form("conf"):
            st.subheader("Dados da Empresa")
            n = st.text_input("Razão Social", value=emp.get('nome', ''))
            doc = st.text_input("CNPJ", value=emp.get('cnpj', ''))
            if st.form_submit_button("💾 SALVAR CONFIGURAÇÕES"):
                supabase.table("config").upsert({"id": 1, "nome": n, "cnpj": doc}).execute()
                st.success("Dados fixados!"); st.rerun()
        
        st.divider()
        st.subheader("🖼️ Identidade Visual")
        st.file_uploader("Upload Logomarca (PNG)", type=["png"])
        
        st.divider()
        st.subheader("🔥 ZONA DE PERIGO (Limpeza Total)")
        c1, c2 = st.columns(2)
        if c1.button("🗑️ ZERAR TUDO (ESTOQUE)"):
            supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if c2.button("🗑️ ZERAR TUDO (CLIENTES)"):
            supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
