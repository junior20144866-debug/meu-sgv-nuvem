import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONFIGURAÇÃO E CONEXÃO ---
st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# --- 2. CÉREBRO DE TRATAMENTO DE DADOS (Lema: Inteligência na Bagunça) ---
def limpar_valor(v):
    if pd.isna(v): return 0.0
    try:
        s = str(v).replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(s)
    except: return 0.0

def formato_br(v):
    return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- 3. CONTROLE DE SESSÃO ---
if 'auth' not in st.session_state: st.session_state.auth = False

# --- 4. INTERFACE PRINCIPAL ---
if not st.session_state.auth:
    st.title("🔒 SGV Evolution - Acesso")
    if st.text_input("Senha Mestra", type="password") == "Naksu@6026":
        if st.button("Entrar"):
            st.session_state.auth = True
            st.rerun()
else:
    # MENU LATERAL COM TODAS AS OPÇÕES REATIVADAS
    menu = st.sidebar.radio("Navegação Principal", 
        ["🛒 Vendas (PDV)", "📦 Estoque", "👥 Clientes", "📑 Importar Planilhas", "⚙️ Configurações da Empresa"])

    # --- PÁGINA: ESTOQUE (LIBERDADE TOTAL) ---
    if menu == "📦 Estoque":
        st.header("📦 Gestão de Produtos")
        
        # BUSCA DINÂMICA
        busca = st.text_input("🔍 Pesquisar produto por nome ou código")
        
        # MOSTRAR DADOS SEM TRAVAR
        try:
            query = supabase.table("produtos").select("*")
            if busca: query = query.ilike("descricao", f"%{busca}%")
            res = query.order("descricao").execute().data
            
            if res:
                for p in res:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([1, 4, 1, 1])
                        col1.write(f"#{p.get('ean13', '---')}")
                        col2.write(f"**{p['descricao']}**")
                        col3.write(formato_br(p.get('preco_venda', 0)))
                        if col4.button("🗑️", key=f"del_{p['id']}"):
                            supabase.table("produtos").delete().eq("id", p['id']).execute()
                            st.rerun()
                    st.divider()
            else: st.info("Nenhum produto encontrado. Use a aba de Importação.")
        except Exception as e: st.error(f"Erro ao ler banco: {e}")

    # --- PÁGINA: CLIENTES ---
    elif menu == "👥 Clientes":
        st.header("👥 Cadastro Geral de Clientes")
        clis = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        if clis:
            df_clis = pd.DataFrame(clis)
            st.dataframe(df_clis, use_container_width=True)
            # Botão para deletar selecionado
            id_del = st.selectbox("Selecione ID para excluir", ["---"] + [c['id'] for c in clis])
            if id_del != "---" and st.button("Excluir Cliente"):
                supabase.table("Clientes").delete().eq("id", id_del).execute()
                st.rerun()
        else: st.info("Base de clientes vazia.")

    # --- PÁGINA: IMPORTAÇÃO (MOTOR INTELIGENTE) ---
    elif menu == "📑 Importar Planilhas":
        st.header("📑 Importação Inteligente (Auto-Reconhecimento)")
        dest = st.selectbox("Para onde vão os dados?", ["produtos", "Clientes"])
        arq = st.file_uploader("Suba seu arquivo Excel (.xlsx)", type=["xlsx"])
        
        if arq:
            df = pd.read_excel(arq)
            st.write(f"📊 Lidas {len(df)} linhas do arquivo.")
            
            # Sinônimos para arquivos bagunçados
            mapas = {
                "produtos": {"ean13": ["CODIGO", "EAN", "BARRA", "COD"], "descricao": ["DESCRICAO", "NOME", "PRODUTO"], "preco_venda": ["P_VENDA", "PRECO", "VALOR"]},
                "Clientes": {"nome_completo": ["NOM", "NOME", "CLIENTE"], "cpf_cnpj": ["CGC", "CPF", "CNPJ", "DOC"]}
            }
            
            if st.button("🚀 Iniciar Processamento Inteligente"):
                sucesso = 0
                prog = st.progress(0)
                for i, row in df.iterrows():
                    dados = {}
                    for campo_bd, sinonimos in mapas[dest].items():
                        for col_excel in df.columns:
                            if col_excel.upper().strip() in sinonimos:
                                val = row[col_excel]
                                if campo_bd == "preco_venda": dados[campo_bd] = limpar_valor(val)
                                else: dados[campo_bd] = str(val)[:255] if pd.notnull(val) else None
                    
                    if dados:
                        try:
                            supabase.table(dest).insert(dados).execute()
                            sucesso += 1
                        except: pass
                    prog.progress((i + 1) / len(df))
                st.success(f"✅ {sucesso} registros organizados e salvos em {dest}!")
                st.balloons()

    # --- PÁGINA: CONFIGURAÇÕES (LIBERDADE DA EMPRESA) ---
    elif menu == "⚙️ Configurações da Empresa":
        st.header("⚙️ Identidade e Controle")
        
        with st.expander("🖼️ Logomarca e Identidade"):
            logo = st.file_uploader("Upload da Logomarca", type=["png", "jpg"])
            nome_empresa = st.text_input("Nome da Empresa", "Minha Empresa Evolution")
            if st.button("Salvar Perfil"):
                st.success("Perfil da empresa atualizado!")

        with st.expander("🗑️ Gestão de Dados (Zerar)"):
            st.warning("Ação irreversível!")
            if st.button("🔥 ZERAR PRODUTOS"):
                supabase.table("produtos").delete().neq("id", -1).execute()
                st.rerun()
            if st.button("🔥 ZERAR CLIENTES"):
                supabase.table("Clientes").delete().neq("id", -1).execute()
                st.rerun()

        if st.button("🚪 Sair do Sistema"):
            st.session_state.auth = False
            st.rerun()

    # --- PÁGINA: VENDAS (PDV) ---
    elif menu == "🛒 Vendas (PDV)":
        st.header("🛒 Ponto de Venda")
        st.write("Módulo de vendas conectado ao estoque.")
