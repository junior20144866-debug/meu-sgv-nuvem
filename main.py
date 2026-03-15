import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. FUNDAÇÃO E CONEXÃO (IMUTÁVEL) ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

# --- 2. ESTILO WINDOWS DINÂMICO (MODO CLARO) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .win-card {
        background: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 4px solid #0078D4;
        margin-bottom: 20px; height: 100%;
    }
    .tile-label { font-size: 0.9rem; color: #666; font-weight: bold; }
    .tile-value { font-size: 1.8rem; color: #0078D4; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTOR DE SINCRONIZAÇÃO (O FIM DO EFEITO SANFONA) ---
def sincronizar_empresa():
    res = supabase.table("config").select("*").eq("id", 1).execute()
    return res.data[0] if res.data else {}

def importar_massa_inteligente(df, destino):
    # Dicionário baseado nos nomes reais dos seus arquivos enviados (ESTOQUE e CLIENTES)
    mapas = {
        "produtos": {"ean13": ["CODIGO", "BARRA"], "descricao": ["DESCRICAO"], "preco_venda": ["P_VENDA"], "unidade": ["UNIDADE"]},
        "Clientes": {"nome_completo": ["NOM"], "cpf_cnpj": ["CGC", "CPF"], "endereco": ["RUA"], "bairro": ["BAI"], "cidade": ["CID"], "uf": ["UF"]}
    }
    limpo = pd.DataFrame()
    for bd, excel in mapas[destino].items():
        col = next((c for c in df.columns if str(c).upper().strip() in excel), None)
        if col: limpo[bd] = df[col]
    return limpo

# --- 4. INTERFACE ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #0078D4;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.text_input("Chave de Segurança", type="password") == "Naksu@6026":
            if st.button("INICIAR", use_container_width=True): st.session_state.auth = True; st.rerun()
else:
    menu = st.sidebar.radio("SISTEMAS", ["🏠 Painel Início", "🛒 Vendas (PDV)", "📦 Estoque Total", "👥 Gestão Clientes", "📑 Importação", "📊 Relatórios", "⚙️ Ajustes"])

    # --- ABA: INÍCIO (JANELAS DINÂMICAS) ---
    if menu == "🏠 Painel Início":
        st.title("Painel Geral de Operações")
        c1, c2, c3, c4 = st.columns(4)
        
        # BUSCA DADOS REAIS PARA AS JANELAS
        count_p = len(supabase.table("produtos").select("id").execute().data)
        count_c = len(supabase.table("Clientes").select("id").execute().data)
        
        with c1: st.markdown(f'<div class="win-card"><p class="tile-label">VENDAS</p><p class="tile-value">R$ 0,00</p></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="win-card"><p class="tile-label">ESTOQUE</p><p class="tile-value">{count_p} itens</p></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="win-card"><p class="tile-label">CLIENTES</p><p class="tile-value">{count_c} registros</p></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="win-card"><p class="tile-label">STATUS</p><p class="tile-value" style="color:green">Ativo</p></div>', unsafe_allow_html=True)

    # --- ABA: VENDAS (PDV COM BUSCA TOTAL) ---
    elif menu == "🛒 Vendas (PDV)":
        st.header("🛒 Terminal de Vendas")
        col_pdv1, col_pdv2 = st.columns([2,1])
        with col_pdv1:
            q = st.text_input("Pesquisar produto por Nome ou Código EAN")
            if q:
                res = supabase.table("produtos").select("*").ilike("descricao", f"%{q}%").execute().data
                for r in res:
                    cp1, cp2, cp3 = st.columns([3, 1, 1])
                    cp1.write(f"**{r['descricao']}**")
                    cp2.write(f"R$ {r['preco_venda']}")
                    if cp3.button("Adicionar", key=f"add_{r['id']}"): st.toast("Item no Carrinho!")
        with col_pdv2:
            st.subheader("Carrinho Atual")
            st.write("---")
            st.markdown("### Total: R$ 0,00")
            st.button("Finalizar e Lançar no Financeiro", type="primary")

    # --- ABA: ESTOQUE (CONTROLE TOTAL) ---
    elif menu == "📦 Estoque Total":
        st.header("📦 Inventário e Produtos")
        with st.expander("➕ Inclusão Manual Detalhada"):
            with st.form("form_p"):
                c1, c2, c3 = st.columns([3, 1, 1])
                desc = c1.text_input("Descrição Completa")
                ean = c2.text_input("Código EAN")
                un = c3.text_input("Unidade (ex: KG, UN)")
                preco = st.number_input("Preço de Venda", min_value=0.0)
                if st.form_submit_button("💾 Salvar no Inventário"):
                    supabase.table("produtos").insert({"descricao": desc, "ean13": ean, "unidade": un, "preco_venda": preco}).execute()
                    st.rerun()
        
        # LISTAGEM REAL
        itens = supabase.table("produtos").select("*").order("descricao").execute().data
        if itens: st.dataframe(pd.DataFrame(itens), use_container_width=True)

    # --- ABA: CONFIGURAÇÕES (BLINDAGEM DE DADOS) ---
    elif menu == "⚙️ Ajustes":
        st.header("⚙️ Configurações da Empresa")
        dados_e = sincronizar_empresa()
        
        with st.form("form_e"):
            st.subheader("Informações da JMQJ SGV SISTEMAS")
            c1, c2 = st.columns(2)
            n_emp = c1.text_input("Nome", value=dados_e.get('nome', ''))
            c_emp = c2.text_input("CNPJ", value=dados_e.get('cnpj', ''))
            e_emp = st.text_input("Endereço Completo", value=dados_e.get('end', ''))
            logo = st.file_uploader("Trocar Logomarca", type=["png", "jpg"])
            if st.form_submit_button("🔒 GRAVAR E FIXAR CONFIGURAÇÕES"):
                supabase.table("config").upsert({"id": 1, "nome": n_emp, "cnpj": c_emp, "end": e_emp}).execute()
                st.success("Dados fixados com sucesso!")

    # --- ABA: IMPORTAÇÃO (MOTOR ANTI-BAGUNÇA) ---
    elif menu == "📑 Importação":
        st.header("📑 Carga de Dados em Massa")
        t = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Arraste o Excel bagunçado aqui", type=["xlsx"])
        if arq:
            df = pd.read_excel(arq)
            df_limpo = importar_massa_inteligente(df, t)
            st.write("Dados organizados automaticamente:")
            st.dataframe(df_limpo.head())
            if st.button("🚀 Iniciar Carga"):
                for _, row in df_limpo.iterrows():
                    supabase.table(t).insert(row.to_dict()).execute()
                st.success("Carga finalizada!"); st.rerun()
