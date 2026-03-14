import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# --- 2. LAYOUT MODO CLARO & ESTILO WINDOWS DYNAMICS ---
st.set_page_config(page_title="JMQJ SGV SISTEMAS", layout="wide")

st.markdown("""
    <style>
    /* Fundo Claro e Moderno */
    .stApp { background-color: #F0F2F5; color: #1C1E21; }
    
    /* Estilo "Tiles" (Janelas Dinâmicas do Windows) */
    .win-tile {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 6px solid #0078D4;
        transition: transform 0.2s;
        cursor: pointer;
        margin-bottom: 20px;
    }
    .win-tile:hover { transform: scale(1.02); box-shadow: 0 6px 16px rgba(0,0,0,0.12); }
    .tile-title { font-weight: bold; color: #0078D4; font-size: 1.2rem; }
    
    /* Botões Padrão Windows */
    .stButton>button {
        background-color: #0078D4; color: white; border-radius: 4px;
        border: none; padding: 10px 20px; font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CÉREBRO: IMPORTAÇÃO INTELIGENTE (ADAPTA BAGUNÇA) ---
def motor_importacao(df, destino):
    mapas = {
        "produtos": {
            "ean13": ["CODIGO", "EAN", "BARRA", "REF", "COD"],
            "descricao": ["DESCRICAO", "NOME", "ITEM", "PRODUTO"],
            "preco_venda": ["P_VENDA", "PRECO", "VALOR", "VENDA"],
            "unidade": ["UNIDADE", "UN", "MEDIDA"]
        },
        "Clientes": {
            "nome_completo": ["NOM", "NOME", "CLIENTE", "RAZAO"],
            "cpf_cnpj": ["CGC", "CPF", "CNPJ", "DOCUMENTO"],
            "cidade": ["CID", "CIDADE"],
            "telefone": ["TEL", "FONE", "CELULAR", "CONTATO"]
        }
    }
    
    df_limpo = pd.DataFrame()
    for campo_bd, sinonimos in mapas[destino].items():
        # Busca inteligente: encontra a coluna no Excel que mais se parece com o que o banco precisa
        coluna_encontrada = next((c for c in df.columns if str(c).upper().strip() in sinonimos), None)
        if coluna_encontrada:
            df_limpo[campo_bd] = df[coluna_encontrada]
            
    return df_limpo

# --- 4. INTERFACE PRINCIPAL ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center; color: #0078D4;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.text_input("Senha de Acesso", type="password") == "Naksu@6026":
            if st.button("ENTRAR", use_container_width=True):
                st.session_state.auth = True; st.rerun()
else:
    # Menu Lateral
    menu = st.sidebar.radio("NAVEGAÇÃO", ["🏠 Painel Início", "🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importação", "⚙️ Configurações"])

    # --- TELA DE INÍCIO (ESTILO JANELAS WINDOWS) ---
    if menu == "🏠 Painel Início":
        st.title("Bem-vindo ao JMQJ SGV")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="win-tile"><p class="tile-title">🛒 VENDAS</p><p>Realizar nova venda agora.</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="win-tile"><p class="tile-title">📦 ESTOQUE</p><p>Gerenciar produtos e preços.</p></div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="win-tile"><p class="tile-title">👥 CLIENTES</p><p>Base de dados e contatos.</p></div>', unsafe_allow_html=True)

    # --- SESSÃO VENDAS (PDV ATIVADO) ---
    elif menu == "🛒 Vendas":
        st.title("🛒 Frente de Venda")
        col_v1, col_v2 = st.columns([2, 1])
        
        with col_v1:
            busca = st.text_input("🔍 Buscar Produto")
            if busca:
                prods = supabase.table("produtos").select("*").ilike("descricao", f"%{busca}%").execute().data
                for p in prods:
                    col_p1, col_p2, col_p3 = st.columns([3, 1, 1])
                    col_p1.write(p['descricao'])
                    col_p2.write(f"R$ {p['preco_venda']}")
                    if col_p3.button("➕", key=p['id']):
                        st.success("Adicionado!")
        
        with col_v2:
            st.subheader("Carrinho de Vendas")
            st.write("Total: R$ 0,00")
            st.button("Finalizar Pedido")

    # --- IMPORTAÇÃO INTELIGENTE (ADAPTAÇÃO AUTOMÁTICA) ---
    elif menu == "📑 Importação":
        st.title("📑 Importação Inteligente de Dados")
        st.info("Nosso sistema identifica automaticamente as colunas, mesmo que os nomes estejam diferentes.")
        
        dest = st.selectbox("Onde salvar os dados?", ["produtos", "Clientes"])
        arq = st.file_uploader("Suba seu arquivo Excel", type=["xlsx"])
        
        if arq:
            df_raw = pd.read_excel(arq)
            st.write("Dados Brutos detectados:")
            st.dataframe(df_raw.head(3))
            
            df_organizado = motor_importacao(df_raw, dest)
            
            if not df_organizado.empty:
                st.write("✅ Sistema adaptou os dados para nossa tabela:")
                st.dataframe(df_organizado.head())
                
                if st.button("🚀 Confirmar e Integrar ao Banco"):
                    for _, row in df_organizado.iterrows():
                        dados = {k: v for k, v in row.to_dict().items() if pd.notnull(v)}
                        supabase.table(dest).insert(dados).execute()
                    st.success(f"Sucesso! {len(df_organizado)} registros inseridos.")
            else:
                st.error("Não consegui encontrar colunas compatíveis. Verifique o arquivo.")

    # --- CONFIGURAÇÕES ---
    elif menu == "⚙️ Configurações":
        st.title("⚙️ Configurações do Sistema")
        st.subheader("JMQJ SGV SISTEMAS")
        if st.button("Limpar Cache do Sistema"):
            st.rerun()
