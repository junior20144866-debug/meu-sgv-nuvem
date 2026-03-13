import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONFIGURAÇÃO E CONEXÃO ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# --- 2. IDIOMAS E ESTADO ---
texts = {
    "Português": {"vendas": "Vendas", "estoque": "Estoque", "clientes": "Clientes", "import": "Importar Dados", "idioma": "Idioma", "config": "Configurações"},
    "English": {"vendas": "Sales", "estoque": "Inventory", "clientes": "Customers", "import": "Import Data", "idioma": "Language", "config": "Settings"},
    "Español": {"vendas": "Ventas", "estoque": "Inventario", "clientes": "Clientes", "import": "Importar", "idioma": "Idioma", "config": "Ajustes"}
}

if 'lang' not in st.session_state: st.session_state.lang = "Português"
T = texts[st.session_state.lang]

# --- 3. FUNÇÕES ---
def formato_br(valor):
    try: return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "0,00"

def mapear_colunas(df):
    sinonimos = {
        "ean13": ["ean", "codigo", "referencia", "ref", "ean13", "cod"],
        "descricao": ["nome", "produto", "descricao", "item", "nome do produto"],
        "preco_venda": ["preco", "valor", "venda", "preço", "unitario"],
        "unidade": ["un", "unid", "unidade"],
        "nome_completo": ["cliente", "nome", "nome completo", "razao social"],
        "cpf_cnpj": ["cpf", "cnpj", "documento", "doc"],
        "telefone": ["fone", "celular", "tel", "whatsapp"]
    }
    mapeado = {}
    for alvo, lista_sinonimos in sinonimos.items():
        for original in df.columns:
            if str(original).lower().strip() in lista_sinonimos:
                mapeado[original] = alvo
                break
    return mapeado

# --- 4. FLUXO DE ACESSO ---
if not st.session_state.get("autenticado"):
    st.title("🔒 Login SGV Evolution")
    senha = st.text_input("Digite a senha", type="password")
    if st.button("Acessar"):
        if senha == "Naksu@6026":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta")
else:
    # TUDO DAQUI PARA BAIXO SÓ APARECE SE ESTIVER LOGADO
    with st.sidebar:
        st.title("JMQJR Evolution")
        escolha_lang = st.selectbox(f"🌐 {T['idioma']}", list(texts.keys()), index=list(texts.keys()).index(st.session_state.lang))
        if escolha_lang != st.session_state.lang:
            st.session_state.lang = escolha_lang
            st.rerun()
        
        # DEFINIÇÃO DO MENU LATERAL
        menu = st.radio("Menu", [f"🛒 {T['vendas']}", f"📦 {T['estoque']}", f"👥 {T['clientes']}", f"📑 {T['import']}", f"⚙️ {T['config']}"])

    # --- ABA IMPORTAR ---
    if menu == f"📑 {T['import']}":
        st.header("📑 Importação Inteligente")
        tipo_db = st.selectbox("Destino", ["produtos", "Clientes"])
        arquivo = st.file_uploader("Suba o arquivo", type=["xlsx", "csv"])
        if arquivo:
            df = pd.read_excel(arquivo) if arquivo.name.endswith('xlsx') else pd.read_csv(arquivo)
            mapa = mapear_colunas(df)
            if mapa:
                df_final = df[list(mapa.keys())].rename(columns=mapa)
                st.dataframe(df_final.head())
                if st.button("🚀 Confirmar Importação"):
                    for _, row in df_final.iterrows():
                        supabase.table(tipo_db).upsert(row.to_dict()).execute()
                    st.success("Importado com sucesso!"); st.balloons()

    # --- ABA ESTOQUE ---
    elif menu == f"📦 {T['estoque']}":
        st.header("📦 Estoque")
        res = supabase.table("produtos").select("*").execute().data
        if res:
            df_v = pd.DataFrame(res)
            df_v['Preço'] = df_v['preco_venda'].apply(formato_br)
            st.dataframe(df_v[['ean13', 'descricao', 'Preço']], use_container_width=True)
        else: st.info("Nenhum produto encontrado. Use a aba Importar.")

    # --- ABA CLIENTES ---
    elif menu == f"👥 {T['clientes']}":
        st.header("👥 Clientes")
        res_c = supabase.table("Clientes").select("*").execute().data
        if res_c: st.dataframe(pd.DataFrame(res_c), use_container_width=True)
        else: st.info("Nenhum cliente cadastrado.")

    # --- ABA CONFIGURAÇÕES ---
    elif menu == f"⚙️ {T['config']}":
        st.header("⚙️ Configurações do Sistema")
        st.write("Ajustes de perfil e logomarca.")
        if st.button("Sair do Sistema"):
            st.session_state.autenticado = False
            st.rerun()

    # --- ABA VENDAS ---
    elif menu == f"🛒 {T['vendas']}":
        st.header("🛒 Ponto de Venda")
        st.write("Selecione os itens para a venda.")
