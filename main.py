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
    return False

# 3. Interface (O que acontece após o login)
if login():
    st.success("Acesso Autorizado!")
    st.sidebar.title("Menu de Gestão")
    opcao = st.sidebar.selectbox("Escolha uma Opção", ["Resumo de Vendas", "Estoque", "Zerar Sistema"])

    if opcao == "Resumo de Vendas":
        st.write("Aqui aparecerão suas vendas do Supabase.")
    
    elif opcao == "Zerar Sistema":
        if st.button("⚠️ CONFIRMAR: ZERAR TUDO"):
            st.warning("Função em desenvolvimento: Isso apagará os dados no Supabase em breve!")
