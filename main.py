import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

# --- 2. CSS: ESTILO WINDOWS TILES (MODO CLARO) ---
st.markdown("""
    <style>
    .stApp { background-color: #F3F4F7; }
    .win-tile {
        background: white; padding: 20px; border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        border-bottom: 4px solid #0078D4; text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #e1e1e1; border-radius: 4px 4px 0 0; padding: 10px 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES MESTRAS (O FIM DO EFEITO SANFONA) ---
def buscar_dados_empresa():
    res = supabase.table("config").select("*").eq("id", 1).execute()
    return res.data[0] if res.data else {}

def motor_import_baguncado(df, tipo):
    mapa = {
        "produtos": {"ean13": ["CODIGO", "BARRA"], "descricao": ["DESCRICAO", "NOME"], "preco_venda": ["P_VENDA", "PRECO"], "unidade": ["UNIDADE", "UN"]},
        "Clientes": {"nome_completo": ["NOM", "NOME"], "cpf_cnpj": ["CGC", "CPF"], "endereco": ["RUA", "ENDERECO"], "bairro": ["BAI", "BAIRRO"], "cidade": ["CID", "CIDADE"], "uf": ["UF"]}
    }
    novo_df = pd.DataFrame()
    for campo_bd, sinonimos in mapa[tipo].items():
        col = next((c for c in df.columns if str(c).upper().strip() in sinonimos), None)
        if col: novo_df[campo_bd] = df[col]
    return novo_df

# --- 4. CONTROLE DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS</h1>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1,1,1])
        if col2.text_input("Acesso Biométrico/Senha", type="password") == "Naksu@6026":
            if col2.button("ENTRAR"): st.session_state.auth = True; st.rerun()
else:
    # Sidebar consolidada
    menu = st.sidebar.radio("Navegação", ["🏠 Início", "🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importação", "📊 Relatórios", "⚙️ Configurações"])

    # --- ABA: INÍCIO (WINDOWS TILES) ---
    if menu == "🏠 Início":
        st.title("Painel de Controle JMQJ")
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown('<div class="win-tile"><b>VENDAS HOJE</b><br><h2>0</h2></div>', unsafe_allow_html=True)
        c2.markdown('<div class="win-tile"><b>PRODUTOS</b><br><h2>Ver</h2></div>', unsafe_allow_html=True)
        c3.markdown('<div class="win-tile"><b>CLIENTES</b><br><h2>Ver</h2></div>', unsafe_allow_html=True)
        c4.markdown('<div class="win-tile"><b>CAIXA</b><br><h2>R$ 0,00</h2></div>', unsafe_allow_html=True)

    # --- ABA: VENDAS (ATIVADA E POLIDA) ---
    elif menu == "🛒 Vendas":
        st.header("🛒 Ponto de Venda (PDV)")
        col_v1, col_v2 = st.columns([2, 1])
        with col_v1:
            busca = st.text_input("🔍 Buscar Produto (Nome ou Código)")
            if busca:
                itens = supabase.table("produtos").select("*").ilike("descricao", f"%{busca}%").execute().data
                for it in itens:
                    cv1, cv2, cv3 = st.columns([3, 1, 1])
                    cv1.write(it['descricao'])
                    cv2.write(f"R$ {it['preco_venda']}")
                    if cv3.button("➕", key=f"pdv_{it['id']}"): st.toast("Adicionado!")
        with col_v2:
            st.subheader("Carrinho")
            st.write("---")
            st.markdown("### Total: R$ 0,00")
            st.button("Finalizar Venda", type="primary")

    # --- ABA: CLIENTES (CONTROLE TOTAL) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        with st.expander("➕ Inclusão Manual de Cliente"):
            with st.form("cli_manual"):
                c1, c2 = st.columns(2)
                n = c1.text_input("Nome/Razão Social")
                d = c2.text_input("CPF/CNPJ")
                end = st.text_input("Endereço (Rua/Nº)")
                c3, c4, c5 = st.columns([2, 2, 1])
                bai, cid, uf = c3.text_input("Bairro"), c4.text_input("Cidade"), c5.text_input("UF")
                if st.form_submit_button("Salvar Cliente"):
                    supabase.table("Clientes").insert({"nome_completo": n, "cpf_cnpj": d, "endereco": end, "bairro": bai, "cidade": cid, "uf": uf}).execute()
                    st.rerun()
        
        res_c = supabase.table("Clientes").select("*").execute().data
        if res_c: st.dataframe(pd.DataFrame(res_c), use_container_width=True)

    # --- ABA: CONFIGURAÇÕES (PRESERVAÇÃO TOTAL) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Configurações do Sistema")
        emp = buscar_dados_empresa()
        
        with st.form("conf_empresa"):
            st.subheader("Dados Fixos da Empresa")
            c1, c2 = st.columns(2)
            n_f = c1.text_input("Nome Fantasia", value=emp.get('nome', ''))
            c_f = c2.text_input("CNPJ", value=emp.get('cnpj', ''))
            e_f = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Upload da Logomarca", type=["png", "jpg"])
            if st.form_submit_button("💾 SALVAR E PRESERVAR"):
                supabase.table("config").upsert({"id": 1, "nome": n_f, "cnpj": c_f, "end": e_f}).execute()
                st.success("Dados eternizados no banco de dados!")
        
        if st.button("🔥 ZERAR TUDO"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.rerun()

    # --- ABA: IMPORTAÇÃO (BAGUNÇADO OK) ---
    elif menu == "📑 Importação":
        st.header("📑 Importação em Massa")
        t_imp = st.selectbox("Tipo", ["produtos", "Clientes"])
        file = st.file_uploader("Excel Bagunçado", type=["xlsx"])
        if file:
            df = pd.read_excel(file)
            df_organizado = motor_import_baguncado(df, t_imp)
            st.write("Dados Organizados pelo Sistema:")
            st.dataframe(df_organizado.head())
            if st.button("Confirmar Carga"):
                for _, row in df_organizado.iterrows():
                    supabase.table(t_imp).insert(row.to_dict()).execute()
                st.success("Carga realizada!")
