import streamlit as st
from supabase import create_client
import pandas as pd
import time

# 1. CONEXÃO
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# 2. FORMATAÇÃO BRASILEIRA
def formato_br(valor):
    try:
        return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00"

# 3. INTELIGÊNCIA DE MAPEAMENTO (O SEGREDO DO "OPERADOR SIMPLES")
def mapear_colunas(df, tipo):
    # Dicionário de sinônimos para as colunas do banco
    sinonimos = {
        "ean13": ["ean", "codigo", "referencia", "ref", "ean13", "cod"],
        "descricao": ["nome", "produto", "descricao", "item", "nome do produto"],
        "preco_venda": ["preco", "valor", "venda", "preço", "preco_venda", "unitario"],
        "unidade": ["un", "unid", "unidade", "medida"],
        "nome_completo": ["cliente", "nome", "nome completo", "razao social", "contato"],
        "cpf_cnpj": ["cpf", "cnpj", "documento", "doc"],
        "telefone": ["fone", "celular", "tel", "whatsapp"]
    }
    
    mapeado = {}
    colunas_arquivo = [str(c).lower().strip() for c in df.columns]
    
    # Busca qual coluna do arquivo combina com os sinônimos do banco
    chaves_alvo = sinonimos.keys()
    for alvo in chaves_alvo:
        for original in df.columns:
            if str(original).lower().strip() in sinonimos[alvo]:
                mapeado[original] = alvo
                break
    return mapeado

# --- INTERFACE ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

menu = st.sidebar.radio("Navegação", ["🛒 Vendas", "📦 Estoque", "👥 Clientes", "📑 Importar Dados"])

if menu == "📑 Importar Dados":
    st.header("📑 Importação Inteligente")
    tipo = st.selectbox("O que você está subindo?", ["produtos", "Clientes"])
    
    arquivo = st.file_uploader("Suba qualquer arquivo Excel ou CSV", type=["xlsx", "csv"])
    
    if arquivo:
        df = pd.read_excel(arquivo) if arquivo.name.endswith('xlsx') else pd.read_csv(arquivo)
        
        # Tenta mapear as colunas automaticamente
        mapa = mapear_colunas(df, tipo)
        
        if mapa:
            st.success(f"🔍 Detectei {len(mapa)} colunas compatíveis!")
            df_final = df[list(mapa.keys())].rename(columns=mapa)
            st.write("Prévia de como os dados serão salvos no banco:")
            st.dataframe(df_final.head())
            
            if st.button("🚀 Confirmar Importação"):
                total = len(df_final)
                progresso = st.progress(0)
                for i, row in df_final.iterrows():
                    supabase.table(tipo).upsert(row.to_dict()).execute()
                    progresso.progress((i + 1) / total)
                st.success(f"✅ Finalizado! {total} itens processados.")
        else:
            st.error("Não consegui identificar as colunas. Verifique os nomes no seu Excel.")

elif menu == "📦 Estoque":
    st.header("📦 Estoque")
    res = supabase.table("produtos").select("*").execute().data
    if res:
        df_view = pd.DataFrame(res)
        # Formata o preço na visualização da tabela
        df_view['Preço de Venda'] = df_view['preco_venda'].apply(formato_br)
        st.dataframe(df_view[['ean13', 'descricao', 'Preço de Venda']], use_container_width=True)
