import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# --- 2. FUNÇÃO DE MAPEAMENTO INTELIGENTE POR TABELA ---
def mapear_por_destino(df, destino):
    # Se for PRODUTOS, procure estas colunas
    if destino == "produtos":
        sinonimos = {
            "ean13": ["ean", "codigo", "referencia", "ref", "cod"],
            "descricao": ["nome", "produto", "descricao", "item"],
            "preco_venda": ["preco", "valor", "venda", "unitario"],
            "unidade": ["un", "unid", "unidade"]
        }
    # Se for CLIENTES, procure estas outras
    else:
        sinonimos = {
            "nome_completo": ["nome", "cliente", "nome completo", "razao social"],
            "cpf_cnpj": ["cpf", "cnpj", "documento", "doc"],
            "telefone": ["fone", "celular", "tel", "whatsapp"],
            "cidade": ["cidade", "municipio"]
        }
    
    mapeado = {}
    for alvo, lista in sinonimos.items():
        for col in df.columns:
            if str(col).lower().strip() in lista:
                mapeado[col] = alvo
                break
    return mapeado

# --- 3. INTERFACE ---
if not st.session_state.get("autenticado"):
    st.title("🔒 Login")
    if st.text_input("Senha", type="password") == "Naksu@6026" and st.button("Entrar"):
        st.session_state.autenticado = True; st.rerun()
else:
    menu = st.sidebar.radio("Navegação", ["📦 Estoque", "👥 Clientes", "📑 Importar Dados"])

    if menu == "📑 Importar Dados":
        st.header("📑 Importação por Destino")
        destino = st.selectbox("Para onde vão esses dados?", ["produtos", "Clientes"])
        arquivo = st.file_uploader("Suba o arquivo", type=["xlsx", "csv"])
        
        if arquivo:
            try:
                df = pd.read_excel(arquivo, engine='openpyxl') if arquivo.name.endswith('xlsx') else pd.read_csv(arquivo)
                # AQUI ESTÁ A CORREÇÃO: Passamos o 'destino' para a função
                mapa = mapear_por_destino(df, destino)
                
                if mapa:
                    df_final = df[list(mapa.keys())].rename(columns=mapa)
                    st.write(f"✅ Colunas identificadas para **{destino}**:")
                    st.dataframe(df_final.head())
                    
                    if st.button(f"🚀 Confirmar Importação em {destino}"):
                        for _, row in df_final.iterrows():
                            # Limpa valores nulos para não dar erro no Supabase
                            dados = {k: v for k, v in row.to_dict().items() if pd.notnull(v)}
                            supabase.table(destino).upsert(dados).execute()
                        st.success(f"Sucesso! Dados enviados para {destino}.")
                        st.balloons()
                else:
                    st.error(f"Erro: O arquivo não parece conter colunas de {destino}.")
            except Exception as e:
                st.error(f"Erro técnico: {e}")

    elif menu == "📦 Estoque":
        st.header("📦 Estoque Atual")
        res = supabase.table("produtos").select("*").execute()
        if res.data: st.dataframe(pd.DataFrame(res.data))
        else: st.info("Estoque vazio.")

    elif menu == "👥 Clientes":
        st.header("👥 Lista de Clientes")
        res = supabase.table("Clientes").select("*").execute()
        if res.data: st.dataframe(pd.DataFrame(res.data))
        else: st.info("Nenhum cliente cadastrado.")
