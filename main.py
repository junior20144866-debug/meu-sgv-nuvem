import streamlit as st
from supabase import create_client

# 1. Configurações de Segurança e Conexão
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "sb_publishable_GM3H4uSu3iNDP-dOd1wl8Q_FXp5rTHWI" 

supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# 2. Função de Login (SENHA ATUALIZADA AQUI)
def login():
    st.title("🔐 SGV Nuvem - Acesso")
    senha = st.text_input("Senha Master", type="password")
    if senha == "Naksu@6026": # <--- COLOQUE SUA NOVA SENHA AQUI
        return True
    return False

# 3. Interface Principal
if login():
    st.success("Acesso Autorizado!")
    st.sidebar.title("Menu de Gestão")
    
    # Adicionamos "Clientes" e "Estoque" ao menu
    opcao = st.sidebar.selectbox("Escolha uma Opção", 
        ["Resumo de Vendas", "Cadastro de Clientes", "Estoque", "Importar Dados"])

    if opcao == "Resumo de Vendas":
        st.subheader("🛒 Lançar Nova Venda")
        # (O código de vendas que já tínhamos continua aqui...)
        st.info("Área de lançamentos pronta.")

    elif opcao == "Cadastro de Clientes":
        st.subheader("👥 Gestão de Clientes")
        st.write("Aqui vamos listar e cadastrar seus clientes.")

    elif opcao == "Estoque":
        st.subheader("📦 Controle de Estoque")
        st.write("Aqui aparecerão seus produtos vindos do outro programa.")

    elif opcao == "Importar Dados":
        st.subheader("📤 Importar do Programa Antigo")
        st.write("Como os dados estão em outro programa, vamos usar esta área para subir os arquivos.")
