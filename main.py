import streamlit as st
from supabase import create_client

# 1. Configurações de Segurança e Conexão
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
# Nota: A chave 'anon' você encontra no seu painel do Supabase em Settings > API
CHAVE_SUPABASE = "SUA_CHAVE_ANON_AQUI" 

supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# 2. Função de Login Simples
def login():
    st.title("🔐 SGV Nuvem - Acesso Restrito")
    senha = st.text_input("Introduza a Senha Master", type="password")
    if senha == "1234": # Pode mudar para a senha que quiser
        return True
    return False

# 3. Interface do Sistema
if login():
    st.success("Acesso Autorizado!")
    st.sidebar.title("Menu de Gestão")
    opcao = st.sidebar.selectbox("Escolha uma opção", ["Resumo", "Produtos", "Configurações"])

    if opcao == "Resumo":
        st.subheader("📊 Painel de Vendas")
        st.info("Aqui aparecerão os totais de vendas do dia.")

    if opcao == "Configurações":
        st.subheader("⚙️ Zona de Perigo")
        if st.button("🔴 ZERAR ESTOQUE"):
            st.warning("Tem certeza? Esta ação é irreversível.")
        if st.button("💰 ZERAR VENDAS"):
            st.error("Isto apagará todo o histórico de vendas.")
