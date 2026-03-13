import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONFIGURAÇÃO E CONEXÃO ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# --- 2. IDIOMAS ---
texts = {
    "Português": {"vendas": "Vendas", "estoque": "Estoque", "clientes": "Clientes", "import": "Importar Dados", "idioma": "Idioma", "config": "Configurações"},
    "English": {"vendas": "Sales", "estoque": "Inventory", "clientes": "Customers", "import": "Import Data", "idioma": "Language", "config": "Settings"},
    "Español": {"vendas": "Ventas", "estoque": "Inventario", "clientes": "Clientes", "import": "Importar", "idioma": "Idioma", "config": "Ajustes"}
}
if 'lang' not in st.session_state: st.session_state.lang = "Português"
T = texts[st.session_state.lang]

# --- 3. FUNÇÕES (Formatacao segura) ---
def formato_br(valor):
    try: return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "0,00"

def mapear_colunas(df):
    sinonimos = {
        "ean13": ["ean", "codigo", "referencia", "ref", "ean13", "cod"],
        "descricao": ["nome", "produto", "descricao", "item", "nome do produto"],
        "preco_venda": ["preco", "valor", "venda", "preço", "unitario"],
        "unidade": ["un", "unid", "unidade"]
    }
    mapeado = {}
    for alvo, lista in sinonimos.items():
        for col in df.columns:
            if str(col).lower().strip() in lista:
                mapeado[col] = alvo
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
        else: st.error("Senha incorreta")
else:
    with st.sidebar:
        st.title("JMQJR Evolution")
        escolha_lang = st.selectbox(f"🌐 {T['idioma']}", list(texts.keys()), index=list(texts.keys()).index(st.session_state.lang))
        if escolha_lang != st.session_state.lang:
            st.session_state.lang = escolha_lang
            st.rerun()
        menu = st.sidebar.radio("Navegação", [f"🛒 {T['vendas']}", f"📦 {T['estoque']}", f"👥 {T['clientes']}", f"📑 {T['import']}", f"⚙️ {T['config']}"])

    # --- ABA IMPORTAR ---
    if menu == f"📑 {T['import']}":
        st.header("📑 Importação")
        tipo_db = st.selectbox("Destino", ["produtos", "Clientes"])
        arquivo = st.file_uploader("Suba o arquivo Excel ou CSV", type=["xlsx", "csv"])
        if arquivo:
            try:
                # Tenta ler Excel (precisa do openpyxl no requirements.txt)
                df = pd.read_excel(arquivo, engine='openpyxl') if arquivo.name.endswith('xlsx') else pd.read_csv(arquivo)
                mapa = mapear_colunas(df)
                if mapa:
                    df_final = df[list(mapa.keys())].rename(columns=mapa)
                    st.write("✅ Colunas identificadas:")
                    st.dataframe(df_final.head())
                    if st.button("🚀 Confirmar Importação"):
                        for _, row in df_final.iterrows():
                            supabase.table(tipo_db).upsert(row.to_dict()).execute()
                        st.success("Dados importados!"); st.balloons()
                else: st.error("Colunas não identificadas no seu arquivo.")
            except Exception as e:
                st.error(f"Erro ao ler arquivo: Certifique-se de ter o arquivo 'requirements.txt' com 'openpyxl'. Erro: {e}")

    # --- ABA ESTOQUE (Blindada contra erro de coluna) ---
    elif menu == f"📦 {T['estoque']}":
        st.header("📦 Estoque")
        res = supabase.table("produtos").select("*").execute().data
        if res:
            df_v = pd.DataFrame(res)
            # Criamos a coluna formatada 'Preço (R$)' sem apagar a original
            if 'preco_venda' in df_v.columns:
                df_v['Preço (R$)'] = df_v['preco_venda'].apply(formato_br)
            
            # Exibimos apenas as colunas que EXISTIREM para não dar KeyError
            colunas_existentes = [c for c in ['ean13', 'descricao', 'Preço (R$)'] if c in df_v.columns]
            st.dataframe(df_v[colunas_existentes], use_container_width=True)
        else: st.info("Estoque vazio.")

    # ... (outras abas seguem a mesma lógica)
