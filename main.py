import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# --- 2. IDIOMAS ---
texts = {
    "Português": {"vendas": "Vendas", "estoque": "Estoque", "clientes": "Clientes", "import": "Importar Dados", "config": "Configurações"},
    "English": {"vendas": "Sales", "estoque": "Inventory", "clientes": "Customers", "import": "Import Data", "config": "Settings"}
}
if 'lang' not in st.session_state: st.session_state.lang = "Português"
T = texts[st.session_state.lang]

# --- 3. FUNÇÕES UTILITÁRIAS ---
def formato_br(valor):
    try: return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "0,00"

def mapear_colunas_dinamico(df, destino):
    if destino == "produtos":
        referencias = {
            "ean13": ["codigo", "referencia", "ean", "ean13", "cod"],
            "descricao": ["descricao", "nome", "produto", "item"],
            "preco_venda": ["p_venda", "preco", "valor", "venda"],
            "unidade": ["unidade", "un", "unid"]
        }
    else: # Clientes
        referencias = {
            "nome_completo": ["nom", "nome", "cliente", "razao social"],
            "cpf_cnpj": ["cgc", "cpf", "cnpj", "documento"],
            "telefone": ["tel1", "telefone", "fone"],
            "cidade": ["cid", "cidade"]
        }
    mapeado = {col: alvo for alvo, lista in referencias.items() for col in df.columns if str(col).lower().strip() in lista}
    return mapeado

# --- 4. INTERFACE ---
if not st.session_state.get("autenticado"):
    st.title("🔒 Login")
    if st.text_input("Senha", type="password") == "Naksu@6026" and st.button("Acessar"):
        st.session_state.autenticado = True; st.rerun()
else:
    menu = st.sidebar.radio("Navegação", [f"🛒 {T['vendas']}", f"📦 {T['estoque']}", f"👥 {T['clientes']}", f"📑 {T['import']}", f"⚙️ {T['config']}"])

    # --- ESTOQUE (COM GESTÃO MANUAL DE VOLTA) ---
    if menu == f"📦 {T['estoque']}":
        st.header("📦 Gestão de Estoque")
        
        # Botões de Ação
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1.expander("➕ Cadastrar Novo Produto"):
            with st.form("novo_p", clear_on_submit=True):
                d = st.text_input("Descrição")
                e = st.text_input("EAN/Código")
                p = st.number_input("Preço", min_value=0.0)
                if st.form_submit_button("Salvar"):
                    supabase.table("produtos").insert({"descricao": d, "ean13": e, "preco_venda": p}).execute()
                    st.success("Produto inserido!"); time.sleep(1); st.rerun()

        # Listagem
        res = supabase.table("produtos").select("*").order("descricao").execute().data
        if res:
            df_p = pd.DataFrame(res)
            if 'preco_venda' in df_p.columns: df_p['Preço (R$)'] = df_p['preco_venda'].apply(formato_br)
            st.dataframe(df_p[['ean13', 'descricao', 'Preço (R$)']], use_container_width=True)
        else: st.info("Estoque vazio.")

    # --- CLIENTES ---
    elif menu == f"👥 {T['clientes']}":
        st.header("👥 Cadastro de Clientes")
        res = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        if res: st.dataframe(pd.DataFrame(res), use_container_width=True)
        else: st.info("Nenhum cliente.")

    # --- IMPORTAÇÃO (BLINDADA PARA IMPORTAR TODOS) ---
    elif menu == f"📑 {T['import']}":
        st.header("📑 Importação em Massa")
        destino = st.selectbox("Destino", ["produtos", "Clientes"])
        arquivo = st.file_uploader("Arquivo Excel", type=["xlsx", "csv"])
        
        if arquivo:
            df = pd.read_excel(arquivo) if arquivo.name.endswith('xlsx') else pd.read_csv(arquivo)
            mapa = mapear_colunas_dinamico(df, destino)
            if mapa:
                df_final = df[list(mapa.keys())].rename(columns=mapa)
                st.write("Prévia dos dados:")
                st.dataframe(df_final.head())
                
                if st.button("🚀 Iniciar Importação Total"):
                    progresso = st.progress(0)
                    linhas = df_final.to_dict(orient='records')
                    for i, linha in enumerate(linhas):
                        # Remove campos vazios para não bugar o banco
                        dados = {k: str(v) for k, v in linha.items() if pd.notnull(v)}
                        supabase.table(destino).insert(dados).execute()
                        progresso.progress((i + 1) / len(linhas))
                    st.success(f"✅ {len(linhas)} registros importados!"); st.balloons()
            else: st.error("Colunas não compatíveis.")

    # --- CONFIGURAÇÕES ---
    elif menu == f"⚙️ {T['config']}":
        st.header("⚙️ Configurações")
        if st.button("🔥 ZERAR TUDO (CUIDADO)"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.success("Sistema limpo!"); time.sleep(1); st.rerun()
        if st.button("🚪 Sair"):
            st.session_state.autenticado = False; st.rerun()
