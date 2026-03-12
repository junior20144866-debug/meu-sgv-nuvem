import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONFIGURAÇÃO INICIAL (Sempre no topo) ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

# Conexão Supabase
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# Dicionário de Idiomas
texts = {
    "Português": {"vendas": "Vendas", "estoque": "Estoque", "clientes": "Clientes", "import": "Importar Dados", "idioma": "Idioma", "config": "Configurações"},
    "English": {"vendas": "Sales", "estoque": "Inventory", "clientes": "Customers", "import": "Import Data", "idioma": "Language", "config": "Settings"},
    "Español": {"vendas": "Ventas", "estoque": "Inventario", "clientes": "Clientes", "import": "Importar", "idioma": "Idioma", "config": "Ajustes"}
}

# Inicialização do Estado do Idioma (EVITA O ERRO NAMEERROR 'T')
if 'lang' not in st.session_state:
    st.session_state.lang = "Português"

# Define T globalmente para o restante do código
T = texts[st.session_state.lang]

# --- 2. FUNÇÕES DE APOIO ---
def formato_br(valor):
    try:
        return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00"

def mapear_colunas(df):
    sinonimos = {
        "ean13": ["ean", "codigo", "referencia", "ref", "ean13", "cod"],
        "descricao": ["nome", "produto", "descricao", "item", "nome do produto"],
        "preco_venda": ["preco", "valor", "venda", "preço", "unitario"],
        "unidade": ["un", "unid", "unidade"],
        "nome_completo": ["cliente", "nome", "nome completo", "razao social"],
        "cpf_cnpj": ["cpf", "cnpj", "documento", "doc", "identidade"],
        "telefone": ["fone", "celular", "tel", "whatsapp"],
        "cidade": ["cidade", "municipio"],
        "bairro": ["bairro", "distrito"],
        "cep": ["cep", "postal"]
    }
    mapeado = {}
    for alvo, lista_sinonimos in sinonimos.items():
        for original in df.columns:
            if str(original).lower().strip() in lista_sinonimos:
                mapeado[original] = alvo
                break
    return mapeado

# --- 3. CONTROLE DE ACESSO ---
if not st.session_state.get("autenticado"):
    st.title("🔒 Login SGV Evolution")
    senha = st.text_input("Digite a senha de acesso", type="password")
    if st.button("Acessar"):
        if senha == "Naksu@6026":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
else:
    # --- 4. INTERFACE APÓS LOGIN ---
    with st.sidebar:
        st.title("JMQJR Evolution")
        # Seletor de Idioma
        escolha_lang = st.selectbox(f"🌐 {T['idioma']}", list(texts.keys()), index=list(texts.keys()).index(st.session_state.lang))
        if escolha_lang != st.session_state.lang:
            st.session_state.lang = escolha_lang
            st.rerun()
            
        menu = st.radio("Menu", [f"🛒 {T['vendas']}", f"📦 {T['estoque']}", f"👥 {T['clientes']}", f"📑 {T['import']}", f"⚙️ {T['config']}"])

    # --- ABA IMPORTAR ---
    if menu == f"📑 {T['import']}":
        st.header("📑 Importação Inteligente")
        tipo_db = st.selectbox("Escolha o destino da planilha", ["produtos", "Clientes"])
        arquivo = st.file_uploader("Suba o arquivo Excel ou CSV", type=["xlsx", "csv"])
        
        if arquivo:
            try:
                df = pd.read_excel(arquivo) if arquivo.name.endswith('xlsx') else pd.read_csv(arquivo)
                mapa = mapear_colunas(df)
                
                if mapa:
                    st.success(f"🔍 Detectamos {len(mapa)} colunas compatíveis!")
                    df_final = df[list(mapa.keys())].rename(columns=mapa)
                    st.write("Prévia dos dados que serão salvos:")
                    st.dataframe(df_final.head())
                    
                    if st.button("🚀 Confirmar e Importar"):
                        total = len(df_final)
                        prog = st.progress(0)
                        for i, row in df_final.iterrows():
                            # O .upsert usa o EAN13 ou ID único para evitar duplicados
                            supabase.table(tipo_db).upsert(row.to_dict()).execute()
                            prog.progress((i + 1) / total)
                        st.success(f"Importação de {total} registros concluída!")
                        st.balloons()
                else:
                    st.error("⚠️ Nenhuma coluna reconhecida. Verifique os títulos do seu arquivo.")
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")

    # --- ABA ESTOQUE ---
    elif menu == f"📦 {T['estoque']}":
        st.header("📦 Estoque")
        res = supabase.table("produtos").select("*").execute().data
        if res:
            df_v = pd.DataFrame(res)
            df_v['Preço'] = df_v['preco_venda'].apply(formato_br)
            st.dataframe(df_v[['ean13', 'descricao', 'Preço']], use_container_width=True)
        else:
            st.warning("Estoque vazio.")

    # --- OUTRAS ABAS (Placeholder para evitar erros) ---
    else:
        st.write(f"Tela de {menu} em desenvolvimento.")
