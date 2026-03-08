import streamlit as st
from supabase import create_client
import pandas as pd

# Conexão
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "sb_publishable_GM3H4uSu3iNDP-dOd1wl8Q_FXp5rTHWI" 
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# Login
def login():
    st.title("🍎 Derlyana Alimentos - SGV")
    senha = st.text_input("Senha Master", type="password")
    if senha == "Naksu@6026": 
        return True
    return False

if login():
    st.sidebar.title("Navegação")
    menu = st.sidebar.radio("Ir para:", ["PDV (Vendas)", "Gerenciar Clientes", "Gerenciar Estoque"])

    # --- ABA DE ESTOQUE (PRODUTOS) ---
    if menu == "Gerenciar Estoque":
        st.header("📦 Controle de Produtos")
        
        # Formulário para Adicionar Novo
        with st.expander("➕ Adicionar Novo Produto"):
            with st.form("form_produto"):
                desc = st.text_input("Descrição do Produto")
                col1, col2, col3 = st.columns(3)
                uni = col1.selectbox("Unidade", ["KG", "PC", "CX", "UNI"])
                prc = col2.number_input("Preço de Venda", min_value=0.0)
                est = col3.number_input("Estoque Inicial", min_value=0.0)
                if st.form_submit_button("Salvar Produto"):
                    supabase.table("produtos").insert({"descricao": desc, "unidade": uni, "preco_venda": prc, "estoque_atual": est}).execute()
                    st.success("Produto cadastrado!")
                    st.rerun()

        # Listagem com opção de Excluir
        st.subheader("Produtos Cadastrados")
        res = supabase.table("produtos").select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df[["descricao", "unidade", "preco_venda", "estoque_atual"]], use_container_width=True)
            
            produto_del = st.selectbox("Selecione um produto para excluir", df['descricao'].tolist())
            if st.button("🗑️ Excluir Produto Selecionado"):
                supabase.table("produtos").delete().eq("descricao", produto_del).execute()
                st.warning(f"Produto {produto_del} removido.")
                st.rerun()

    # --- ABA DE CLIENTES ---
    elif menu == "Gerenciar Clientes":
        st.header("👥 Cadastro de Clientes")
        # Segue a mesma lógica acima, mas para a tabela de clientes
        st.info("Aqui você poderá editar os clientes do PDF.")
        
    elif menu == "PDV (Vendas)":
        st.header("🛒 Ponto de Venda")
        # Aqui vamos buscar os produtos do banco para você apenas selecionar
        st.write("Selecione o produto e o cliente já cadastrados.")
