import streamlit as st
from supabase import create_client

# 1. Conexão
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "sb_publishable_GM3H4uSu3iNDP-dOd1wl8Q_FXp5rTHWI" 
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# 2. Login
def login():
    st.title("🔐 SGV Nuvem - Derlyana Alimentos")
    senha = st.text_input("Senha Master", type="password")
    if senha == "Naksu@6026": # <--- Troque pela sua nova senha aqui
        return True
    return False

if login():
    st.sidebar.title("Menu de Gestão")
    opcao = st.sidebar.selectbox("Opção", ["Lançar Venda", "Cadastro de Clientes", "Estoque"])

    if opcao == "Lançar Venda":
        st.subheader("📝 Novo Pedido de Venda")
        
        # Dados do Cliente (Baseado no seu modelo)
        with st.expander("👤 Dados do Cliente", expanded=True):
            cliente = st.text_input("Cliente / Razão Social")
            col1, col2 = st.columns(2)
            cpf_cnpj = col1.text_input("CPF/CNPJ")
            telefone = col2.text_input("Telefone")
            
            endereco = st.text_input("Endereço (Rua, Nº)")
            c1, c2, c3 = st.columns([2, 2, 1])
            bairro = c1.text_input("Bairro")
            cidade = c2.text_input("Cidade")
            uf = c3.text_input("UF", value="CE")

        # Itens do Pedido
        with st.expander("📦 Itens do Pedido", expanded=True):
            col_item, col_uni, col_val, col_qtd = st.columns([3, 1, 1, 1])
            item = col_item.text_input("Descrição do Item")
            uni = col_uni.selectbox("Uni", ["KG", "UNI", "CX", "PT"])
            valor_un = col_val.number_input("Valor Unit.", min_value=0.0)
            qtd = col_qtd.number_input("Quantia", min_value=0.0)
            
            total_item = valor_un * qtd
            st.write(f"**Total do Item: R$ {total_item:.2f}**")

        if st.button("💾 Finalizar e Gravar Pedido"):
            st.success("Pedido gravado! (Pronto para conectar ao banco)")

    elif opcao == "Cadastro de Clientes":
        st.subheader("👥 Banco de Dados de Clientes")
        st.info("Aqui vamos importar sua lista do FpqSystem.")

    elif opcao == "Estoque":
        st.subheader("🍎 Controle de Produtos")
        st.write("Lista de polpas e produtos cadastrados.")
