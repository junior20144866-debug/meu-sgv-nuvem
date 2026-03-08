import streamlit as st
from supabase import create_client

# 1. Configurações de Segurança e Conexão
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
# Nota: Lembre-se de colocar sua chave real entre as aspas abaixo
CHAVE_SUPABASE = "sb_publishable_GM3H4uSu3iNDP-dOd1wl8Q_FXp5rTHWI" 

supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# 2. Função de Login
def login():
    st.title("🔐 SGV Nuvem - Acesso")
    senha = st.text_input("Senha Master", type="password")
    if senha == "1234":
        return True
# 3. Interface (O que acontece APÓS o login)
if login():
    st.success("Acesso Autorizado!")
    
    # Criando o menu lateral
    st.sidebar.title("Menu de Gestão")
    opcao = st.sidebar.selectbox("Escolha uma Opção", ["Resumo de Vendas", "Estoque"])

    if opcao == "Resumo de Vendas":
        st.subheader("🛒 Lançar Nova Venda")
        
        # Campos para preencher
        produto = st.text_input("Nome do Produto")
        valor = st.number_input("Valor da Venda (R$)", min_value=0.0, format="%.2f")
        quantidade = st.number_input("Quantidade", min_value=1, step=1)
        
        if st.button("Gravar Venda"):
            if produto:
                # Envia para o banco de dados
                dados = {"item": produto, "preco": valor, "qtd": quantidade}
                try:
                    supabase.table("vendas").insert(dados).execute()
                    st.success(f"Venda de {produto} gravada com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
            else:
                st.error("Por favor, digite o nome do produto.")

    elif opcao == "Estoque":
        st.write("Visualização do estoque em breve...")
