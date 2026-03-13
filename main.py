import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONFIGURAÇÃO E CONEXÃO ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# --- 2. SISTEMA DE IDIOMAS ---
texts = {
    "Português": {"vendas": "Vendas", "estoque": "Estoque", "clientes": "Clientes", "import": "Importar Dados", "idioma": "Idioma", "config": "Configurações"},
    "English": {"vendas": "Sales", "estoque": "Inventory", "clientes": "Customers", "import": "Import Data", "idioma": "Language", "config": "Settings"},
    "Español": {"vendas": "Ventas", "estoque": "Inventario", "clientes": "Clientes", "import": "Importar", "idioma": "Idioma", "config": "Ajustes"}
}
if 'lang' not in st.session_state: st.session_state.lang = "Português"
T = texts[st.session_state.lang]

# --- 3. FUNÇÕES DE APOIO ---
def formato_br(valor):
    try: return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "0,00"

def mapear_colunas_dinamico(df, destino):
    # Sinônimos baseados nos arquivos reais que você enviou
    if destino == "produtos":
        referencias = {
            "ean13": ["codigo", "referencia", "ean", "ean13", "cod"],
            "descricao": ["descricao", "nome", "produto", "item"],
            "preco_venda": ["p_venda", "preco", "valor", "venda"],
            "unidade": ["unidade", "un", "unid"],
            "estoque_atual": ["quant_atua", "estoque", "quantidade"]
        }
    else: # Clientes
        referencias = {
            "nome_completo": ["nom", "nome", "cliente", "razao social"],
            "cpf_cnpj": ["cgc", "cpf", "cnpj", "documento"],
            "telefone": ["tel1", "telefone", "fone", "celular"],
            "cidade": ["cid", "cidade", "municipio"],
            "uf": ["est", "uf", "estado"],
            "cep": ["cep", "postal"]
        }
    
    mapeado = {}
    for alvo, lista_sinonimos in referencias.items():
        for col_original in df.columns:
            if str(col_original).lower().strip() in lista_sinonimos:
                mapeado[col_original] = alvo
                break
    return mapeado

# --- 4. FLUXO DE ACESSO ---
if not st.session_state.get("autenticado"):
    st.title("🔒 Login SGV Evolution")
    if st.text_input("Senha", type="password") == "Naksu@6026" and st.button("Acessar"):
        st.session_state.autenticado = True; st.rerun()
else:
    with st.sidebar:
        st.title("JMQJR Evolution")
        st.session_state.lang = st.selectbox(f"🌐 {T['idioma']}", list(texts.keys()))
        menu = st.radio("Navegação", [f"🛒 {T['vendas']}", f"📦 {T['estoque']}", f"👥 {T['clientes']}", f"📑 {T['import']}", f"⚙️ {T['config']}"])

    # --- ABA IMPORTAR (CORRIGIDA) ---
    if menu == f"📑 {T['import']}":
        st.header("📑 Importação Inteligente")
        destino = st.selectbox("Destino da Planilha", ["produtos", "Clientes"])
        arquivo = st.file_uploader("Suba o arquivo EXCEL", type=["xlsx", "csv"])
        
        if arquivo:
            try:
                df = pd.read_excel(arquivo, engine='openpyxl') if arquivo.name.endswith('xlsx') else pd.read_csv(arquivo)
                mapa = mapear_colunas_dinamico(df, destino)
                
                if mapa:
                    df_final = df[list(mapa.keys())].rename(columns=mapa)
                    st.success(f"✅ Identificamos {len(mapa)} colunas para {destino}")
                    st.dataframe(df_final.head())
                    
                    if st.button(f"🚀 Importar para {destino}"):
                        with st.spinner("Processando banco de dados..."):
                            for _, row in df_final.iterrows():
                                dados = {k: v for k, v in row.to_dict().items() if pd.notnull(v)}
                                supabase.table(destino).upsert(dados).execute()
                        st.success("Importação concluída!"); st.balloons()
                else:
                    st.error("⚠️ As colunas deste arquivo não batem com o destino selecionado.")
            except Exception as e: st.error(f"Erro: {e}")

    # --- ABA ESTOQUE ---
    elif menu == f"📦 {T['estoque']}":
        st.header("📦 Gestão de Estoque")
        res = supabase.table("produtos").select("*").execute().data
        if res:
            df_v = pd.DataFrame(res)
            if 'preco_venda' in df_v.columns: df_v['Valor'] = df_v['preco_venda'].apply(formato_br)
            cols = [c for c in ['ean13', 'descricao', 'unidade', 'Valor'] if c in df_v.columns]
            st.dataframe(df_v[cols], use_container_width=True)
        else: st.info("Estoque vazio.")

    # --- ABA CLIENTES ---
    elif menu == f"👥 {T['clientes']}":
        st.header("👥 Clientes")
        res = supabase.table("Clientes").select("*").execute().data
        if res: st.dataframe(pd.DataFrame(res), use_container_width=True)
        else: st.info("Nenhum cliente cadastrado.")

    # --- ABA CONFIGURAÇÕES (LIBERDADE DE DADOS) ---
    elif menu == f"⚙️ {T['config']}":
        st.header("⚙️ Controle do Sistema")
        st.warning("⚠️ CUIDADO: Estas ações não podem ser desfeitas.")
        
        tab_limpar = st.selectbox("Escolha uma tabela para ZERAR (Apagar tudo)", ["Nenhuma", "produtos", "Clientes"])
        if tab_limpar != "Nenhuma":
            if st.button(f"🔥 APAGAR TODOS OS DADOS DE {tab_limpar.upper()}"):
                # No Supabase, para apagar tudo, deletamos onde o ID é maior que 0
                supabase.table(tab_limpar).delete().neq("id", -1).execute()
                st.success(f"Tabela {tab_limpar} zerada!"); time.sleep(1); st.rerun()

        if st.button("🚪 Sair do Sistema"):
            st.session_state.autenticado = False; st.rerun()
