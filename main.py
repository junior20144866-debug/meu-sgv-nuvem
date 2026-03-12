import streamlit as st
from supabase import create_client
import pandas as pd
import time

# 1. CONFIGURAÇÃO E CONEXÃO (Executa antes de tudo)
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# 2. SISTEMA DE TRADUÇÃO (Sempre disponível)
texts = {
    "Português": {"vendas": "Vendas", "estoque": "Estoque", "clientes": "Clientes", "import": "Importar Dados", "idioma": "Idioma"},
    "English": {"vendas": "Sales", "estoque": "Inventory", "clientes": "Customers", "import": "Import Data", "idioma": "Language"},
    "Español": {"vendas": "Ventas", "estoque": "Inventario", "clientes": "Clientes", "import": "Importar", "idioma": "Idioma"}
}

if 'lang' not in st.session_state: st.session_state.lang = "Português"
T = texts[st.session_state.lang]

# 3. FUNÇÕES UTILITÁRIAS
def formato_br(valor):
    try: return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "0,00"

def mapear_colunas(df, tipo):
    sinonimos = {
        "ean13": ["ean", "codigo", "referencia", "ref", "ean13", "cod"],
        "descricao": ["nome", "produto", "descricao", "item", "nome do produto"],
        "preco_venda": ["preco", "valor", "venda", "preço", "unitario"],
        "unidade": ["un", "unid", "unidade"],
        "nome_completo": ["cliente", "nome", "nome completo", "razao social"],
        "cpf_cnpj": ["cpf", "cnpj", "documento", "doc"],
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

# 4. CONTROLE DE ACESSO (O Cadeado)
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
    # --- LOGADO COM SUCESSO ---
    with st.sidebar:
        st.title("JMQJR Evolution")
        st.session_state.lang = st.selectbox(f"🌐 {T['idioma']}", list(texts.keys()))
        menu = st.radio("Menu", [f"🛒 {T['vendas']}", f"📦 {T['estoque']}", f"👥 {T['clientes']}", f"📑 {T['import']}"])

    # --- ABA IMPORTAR ---
    if menu == f"📑 {T['import']}":
        st.header("📑 Importação Inteligente")
        tipo_db = st.selectbox("Destino da planilha", ["produtos", "Clientes"])
        arquivo = st.file_uploader("Suba o Excel ou CSV", type=["xlsx", "csv"])
        
        if arquivo:
            try:
                df = pd.read_excel(arquivo) if arquivo.name.endswith('xlsx') else pd.read_csv(arquivo)
                mapa = mapear_colunas(df, tipo_db)
                
                if mapa:
                    st.success(f"✅ Identificamos {len(mapa)} colunas compatíveis!")
                    df_final = df[list(mapa.keys())].rename(columns=mapa)
                    st.write("Prévia dos dados:")
                    st.dataframe(df_final.head())
                    
                    if st.button("🚀 Confirmar Importação"):
                        total = len(df_final)
                        prog = st.progress(0)
                        for i, row in df_final.iterrows():
                            supabase.table(tipo_db).upsert(row.to_dict()).execute()
                            prog.progress((i + 1) / total)
                        st.success(f"Importação de {total} itens concluída!")
                        st.balloons()
                else:
                    st.error("⚠️ Não encontramos colunas com nomes reconhecíveis. Verifique o cabeçalho.")
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")

    # --- ABA ESTOQUE ---
    elif menu == f"📦 {T['estoque']}":
        st.header("📦 Gestão de Estoque")
        res = supabase.table("produtos").select("*").execute().data
        if res:
            df_v = pd.DataFrame(res)
            df_v['Preço'] = df_v['preco_venda'].apply(formato_br)
            st.dataframe(df_v[['ean13', 'descricao', 'Preço']], use_container_width=True)
