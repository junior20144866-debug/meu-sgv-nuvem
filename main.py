import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# --- 2. LAYOUT DIGNO DE TESLA (Custom CSS) ---
st.set_page_config(page_title="Evolution Tesla OS", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Estética Dark de Luxo */
    .stApp { background-color: #0A0A0A; color: #E0E0E0; }
    [data-testid="stSidebar"] { background-color: #111111; border-right: 1px solid #333; }
    
    /* Cards de Informação */
    .tesla-card {
        background: #1A1A1A;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #333;
        margin-bottom: 15px;
        transition: 0.3s;
    }
    .tesla-card:hover { border-color: #0078D4; box-shadow: 0 0 15px rgba(0,120,212,0.2); }
    
    /* Inputs Estilizados */
    input { background-color: #222 !important; color: white !important; border-radius: 8px !important; }
    
    /* Botões Tesla */
    .stButton>button {
        background-color: #E81123; /* Vermelho Tesla */
        color: white; border-radius: 25px; border: none; padding: 10px 25px;
        font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES DE PERSISTÊNCIA ---
def carregar_empresa():
    try:
        res = supabase.table("config").select("*").eq("id", 1).execute()
        return res.data[0] if res.data else {}
    except: return {}

# --- 4. NAVEGAÇÃO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #E81123;'>EVOLUTION TESLA OS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.text_input("Acesso Biométrico (Senha)", type="password") == "Naksu@6026":
            if st.button("INICIAR SISTEMAS"): st.session_state.auth = True; st.rerun()
else:
    with st.sidebar:
        st.markdown("<h2 style='color: #E81123;'>Evolution OS</h2>", unsafe_allow_html=True)
        menu = st.radio("SISTEMAS", ["📊 Dashboard", "🛒 PDV Vendas", "📦 Controle de Estoque", "👥 Base de Clientes", "💰 Financeiro", "⚙️ Configurações"])

    # --- PÁGINA: ESTOQUE (CONTROLE TOTAL DETALHADO) ---
    if menu == "📦 Controle de Estoque":
        st.title("📦 Inventário de Produtos")
        
        with st.expander("➕ Adicionar Novo Produto (Manual)"):
            with st.form("new_product"):
                c1, c2, c3 = st.columns([2, 2, 1])
                desc = c1.text_input("Descrição do Produto")
                ean = c2.text_input("EAN / Código")
                unid = c3.selectbox("Unidade", ["UN", "KG", "CX", "PC", "LT"])
                
                c4, c5 = st.columns(2)
                p_venda = c4.number_input("Preço de Venda", min_value=0.0)
                estoque_min = c5.number_input("Estoque Mínimo", min_value=0)
                
                if st.form_submit_button("CADASTRAR PRODUTO"):
                    supabase.table("produtos").insert({"descricao": desc, "ean13": ean, "unidade": unid, "preco_venda": p_venda}).execute()
                    st.success("Produto integrado ao sistema!"); st.rerun()

        # LISTAGEM TESLA STYLE
        res = supabase.table("produtos").select("*").order("descricao").execute().data
        if res:
            for p in res:
                st.markdown(f"""
                <div class="tesla-card">
                    <div style="display: flex; justify-content: space-between;">
                        <span><b>{p['descricao']}</b> | {p.get('unidade', 'UN')}</span>
                        <span style="color: #0078D4;">{f"R$ {p['preco_venda']:,.2f}"}</span>
                    </div>
                    <small style="color: #888;">Cód: {p.get('ean13', '---')}</small>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🗑️ Remover", key=f"del_{p['id']}"):
                    supabase.table("produtos").delete().eq("id", p['id']).execute(); st.rerun()
        else: st.info("Hangar de produtos vazio.")

    # --- PÁGINA: CLIENTES (DADOS COMPLETOS) ---
    elif menu == "👥 Base de Clientes":
        st.title("👥 Gestão de Clientes")
        
        with st.expander("➕ Novo Cadastro"):
            with st.form("new_client"):
                nome = st.text_input("Nome Completo / Razão Social")
                c1, c2 = st.columns(2)
                doc = c1.text_input("CPF / CNPJ")
                tel = c2.text_input("Telefone")
                
                st.markdown("---")
                end = st.text_input("Endereço (Rua, Número)")
                c3, c4, c5 = st.columns([2, 2, 1])
                bairro = c3.text_input("Bairro")
                cidade = c4.text_input("Cidade")
                uf = c5.text_input("UF")
                
                if st.form_submit_button("SALVAR CLIENTE"):
                    dados_c = {"nome_completo": nome, "cpf_cnpj": doc, "telefone": tel, "endereco": end, "bairro": bairro, "cidade": cidade, "uf": uf}
                    supabase.table("Clientes").insert(dados_c).execute()
                    st.success("Cliente cadastrado com sucesso!"); st.rerun()

        # Listagem em Tabela Moderna
        res_c = supabase.table("Clientes").select("*").execute().data
        if res_c:
            df_c = pd.DataFrame(res_c)
            st.dataframe(df_c[['nome_completo', 'cpf_cnpj', 'cidade', 'uf', 'telefone']], use_container_width=True)
        else: st.info("Nenhum cliente na base.")

    # --- PÁGINA: CONFIGURAÇÕES (THE CONTROL CENTER) ---
    elif menu == "⚙️ Configurações":
        st.title("⚙️ Centro de Comando")
        conf = carregar_empresa()
        
        with st.container():
            st.markdown("<div class='tesla-card'>", unsafe_allow_html=True)
            st.subheader("🏢 Identidade da Empresa")
            col_a, col_b = st.columns(2)
            n_emp = col_a.text_input("Nome Fantasia", conf.get('nome', ''))
            c_emp = col_b.text_input("CNPJ", conf.get('cnpj', ''))
            e_emp = st.text_input("Endereço Completo", conf.get('end', ''))
            
            if st.button("SALVAR ALTERAÇÕES"):
                supabase.table("config").upsert({"id": 1, "nome": n_emp, "cnpj": c_emp, "end": e_emp}).execute()
                st.success("Configurações atualizadas!"); time.sleep(1); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.subheader("🧹 Limpeza Total")
        if st.button("🔥 ZERAR TODO O SISTEMA"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.success("Sistema limpo!"); st.rerun()
