import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Configurações de Conexão
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "sb_publishable_GM3H4uSu3iNDP-dOd1wl8Q_FXp5rTHWI" 
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# 2. Função de Login
def login():
    st.title("🍎 Derlyana Alimentos - SGV")
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if not st.session_state.autenticado:
        senha = st.text_input("Senha Master", type="password")
        if st.button("Entrar"):
            if senha == "Naksu@6026": 
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta")
        return False
    return True

if login():
    st.sidebar.title("Navegação")
    menu = st.sidebar.radio("Ir para:", ["🛒 PDV (Vendas)", "👥 Gerenciar Clientes", "📦 Gerenciar Estoque"])

    # --- ABA DE ESTOQUE (Tabela: produtos) ---
    if menu == "📦 Gerenciar Estoque":
        st.header("📦 Controle de Produtos")
        
        with st.expander("➕ Adicionar Novo Produto"):
            with st.form("form_prod"):
                desc = st.text_input("Descrição do Produto")
                c1, c2, c3 = st.columns(3)
                uni = c1.selectbox("Unidade", ["KG", "PC", "CX", "UNI"])
                prc = c2.number_input("Preço de Venda", min_value=0.0)
                est = c3.number_input("Estoque Atual", min_value=0.0)
                if st.form_submit_button("Salvar"):
                    dados_prod = {
                        "Descrição": desc, 
                        "Unidade": uni, 
                        "Preço de venda": prc, 
                        "Estoque atual": est
                    }
                    supabase.table("produtos").insert(dados_prod).execute()
                    st.success("Produto salvo!")
                    st.rerun()

        res_p = supabase.table("produtos").select("*").execute()
        if res_p.data:
            st.dataframe(pd.DataFrame(res_p.data), use_container_width=True)

    # --- ABA DE CLIENTES (Tabela: Clientes | Coluna: endereco) ---
    elif menu == "👥 Gerenciar Clientes":
        st.header("👥 Gestão de Clientes")
        
        with st.expander("➕ Adicionar Novo Cliente"):
            with st.form("form_cliente"):
                nome = st.text_input("Nome")
                apelido = st.text_input("Apelido")
                col1, col2, col3 = st.columns([2, 2, 1])
                cpf_cnpj = col1.text_input("CPF/CNPJ")
                tel = col2.text_input("Telefone")
                cep = col3.text_input("CEP")
                end = st.text_input("Endereço")
                bairro = st.text_input("Bairro")
                cidade = st.text_input("Cidade")

                if st.form_submit_button("Salvar Cliente"):
                    # AJUSTADO: Tabela 'Clientes' e coluna 'endereco'
                    dados_cli = {
                        "Nome": nome, 
                        "Apelido": apelido,
                        "CPF/CNPJ": cpf_cnpj, 
                        "Telefone": tel, 
                        "CEP": cep,
                        "endereco": end, # <--- Nome exato que você informou
                        "Bairro": bairro, 
                        "Cidade": cidade
                    }
                    supabase.table("Clientes").insert(dados_cli).execute()
                    st.success("Cliente cadastrado!")
                    st.rerun()

        res_c = supabase.table("Clientes").select("*").execute()
        if res_c.data:
            st.dataframe(pd.DataFrame(res_c.data), use_container_width=True)

    # --- ABA DE VENDAS ---
    elif menu == "🛒 PDV (Vendas)":
        st.header("🛒 Lançar Pedido")
        
        # Puxar dados para os menus de seleção
        try:
            c_data = supabase.table("Clientes").select("Nome, endereco, Bairro, CEP").execute()
            p_data = supabase.table("produtos").select("Descrição, \"Preço de venda\"").execute()
            
            lista_c = [c['Nome'] for c in c_data.data] if c_data.data else []
            lista_p = [p['Descrição'] for p in p_data.data] if p_data.data else []

            c_sel = st.selectbox("Selecione o Cliente", [""] + lista_c)
            if c_sel:
                detalhe = next(c for c in c_data.data if c['Nome'] == c_sel)
                st.info(f"📍 Entrega: {detalhe['endereco']}, {detalhe['Bairro']} - CEP: {detalhe['CEP']}")

            p_sel = st.selectbox("Selecione o Produto", [""] + lista_p)
            if p_sel:
                detalhe_p = next(p for p in p_data.data if p['Descrição'] == p_sel)
                col_v, col_q = st.columns(2)
                preco = col_v.number_input("Preço Unit.", value=float(detalhe_p['Preço de venda']))
                qtd = col_q.number_input("Quantidade", min_value=1)
                st.subheader(f"Total: R$ {preco * qtd:.2f}")
                
                if st.button("✅ Finalizar Venda"):
                    st.success("Pedido registrado com sucesso!")
        except Exception as e:
            st.error(f"Aguardando cadastro de dados ou erro de coluna: {e}")
