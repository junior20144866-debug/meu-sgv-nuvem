import streamlit as st
from supabase import create_client
import pandas as pd
import time

# --- 1. CONEXÃO ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="SGV Evolution Pro", layout="wide")

# --- 2. FUNÇÕES DE APOIO ---
def formato_br(valor):
    try: return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return "R$ 0,00"

# --- 3. AUTENTICAÇÃO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔒 Acesso Restrito")
    if st.text_input("Senha Mestra", type="password") == "Naksu@6026":
        if st.button("Liberar Sistema"):
            st.session_state.auth = True
            st.rerun()
else:
    menu = st.sidebar.radio("Navegação", ["🛒 Vendas (PDV)", "📦 Estoque", "👥 Clientes", "📑 Importação Inteligente", "⚙️ Sistema"])

    # --- ABA CLIENTES (COM EDIÇÃO E EXCLUSÃO) ---
    if menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        
        with st.expander("➕ Adicionar Novo Cliente"):
            with st.form("add_cli"):
                n = st.text_input("Nome")
                d = st.text_input("CPF/CNPJ")
                if st.form_submit_button("Salvar"):
                    supabase.table("Clientes").insert({"nome_completo": n, "cpf_cnpj": d}).execute()
                    st.rerun()

        res = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        if res:
            for c in res:
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(f"**{c['nome_completo']}** ({c.get('cpf_cnpj', 'S/D')})")
                if col2.button("📝 Editar", key=f"ed_{c['id']}"):
                    st.info("Função de edição rápida em desenvolvimento")
                if col3.button("🗑️ Excluir", key=f"del_{c['id']}"):
                    supabase.table("Clientes").delete().eq("id", c['id']).execute()
                    st.warning(f"Cliente {c['nome_completo']} removido.")
                    st.rerun()
        else: st.info("Nenhum cliente.")

    # --- ABA ESTOQUE (FIX: MOSTRANDO TUDO) ---
    elif menu == "📦 Estoque":
        st.header("📦 Controle de Estoque")
        
        prods = supabase.table("produtos").select("*").order("descricao").execute().data
        if prods:
            df_p = pd.DataFrame(prods)
            # Normalização de nomes para exibição
            display_cols = []
            if 'ean13' in df_p.columns: display_cols.append('ean13')
            if 'descricao' in df_p.columns: display_cols.append('descricao')
            if 'preco_venda' in df_p.columns:
                df_p['Preço'] = df_p['preco_venda'].apply(formato_br)
                display_cols.append('Preço')
            
            st.dataframe(df_p[display_cols], use_container_width=True)
            
            # Controle de exclusão rápida
            sel_p = st.selectbox("Selecione um produto para remover", ["---"] + [p['descricao'] for p in prods])
            if sel_p != "---" and st.button("Remover Produto"):
                supabase.table("produtos").delete().eq("descricao", sel_p).execute()
                st.rerun()
        else: st.info("Estoque vazio. Vá em Importação.")

    # --- ABA IMPORTAÇÃO (RECONHECIMENTO BAGUNÇADO) ---
    elif menu == "📑 Importação Inteligente":
        st.header("📑 Motor de Reconhecimento de Dados")
        tipo = st.selectbox("O que deseja importar?", ["produtos", "Clientes"])
        arq = st.file_uploader("Suba sua planilha (mesmo que esteja bagunçada)", type=["xlsx"])
        
        if arq:
            df = pd.read_excel(arq)
            st.write("🔍 Analisando colunas do seu arquivo...")
            
            # Mapeamento dinâmico (O segredo da maravilha)
            mapeamento = {
                "produtos": {"ean13": ["CODIGO", "EAN", "REF"], "descricao": ["DESCRICAO", "NOME", "ITEM"], "preco_venda": ["P_VENDA", "PRECO", "VALOR"]},
                "Clientes": {"nome_completo": ["NOM", "NOME", "CLIENTE"], "cpf_cnpj": ["CGC", "CPF", "CNPJ"]}
            }
            
            final_data = {}
            for campo_bd, sinonimos in mapeamento[tipo].items():
                for col_excel in df.columns:
                    if col_excel.upper() in sinonimos:
                        final_data[campo_bd] = df[col_excel]
                        break
            
            if final_data:
                df_import = pd.DataFrame(final_data)
                st.write("✅ Reconheci estes dados:")
                st.dataframe(df_import.head())
                
                if st.button("🚀 Confirmar e Operar"):
                    for _, row in df_import.iterrows():
                        dados = {k: str(v) for k, v in row.to_dict().items() if pd.notnull(v)}
                        supabase.table(tipo).insert(dados).execute()
                    st.success("Tudo organizado e operando!"); st.balloons()
            else:
                st.error("Não consegui reconhecer as colunas automaticamente.")

    # --- ABA VENDAS (DINÂMICA) ---
    elif menu == "🛒 Vendas (PDV)":
        st.header("🛒 Ponto de Venda Dinâmico")
        
        # Busca clientes e produtos para o seletor
        clis = supabase.table("Clientes").select("nome_completo").execute().data
        prods = supabase.table("produtos").select("descricao", "preco_venda").execute().data
        
        if clis and prods:
            c_venda = st.selectbox("Selecione o Cliente", [c['nome_completo'] for c in clis])
            p_venda = st.multiselect("Adicionar Produtos", [p['descricao'] for p in prods])
            
            total = 0
            for item in p_venda:
                preco = next(p['preco_venda'] for p in prods if p['descricao'] == item)
                total += float(preco)
                st.write(f"🔹 {item} - {formato_br(preco)}")
            
            st.divider()
            st.subheader(f"Total da Venda: {formato_br(total)}")
            if st.button("Finalizar Venda"):
                st.success(f"Venda para {c_venda} registrada!")
        else:
            st.warning("Cadastre clientes e produtos antes de vender.")

    # --- ABA SISTEMA ---
    elif menu == "⚙️ Sistema":
        if st.button("🔥 ZERAR TODO O BANCO"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            st.success("Tabelas limpas!"); st.rerun()
