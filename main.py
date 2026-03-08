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
            if senha == "Naksu@6026": # <--- TROQUE SUA SENHA AQUI
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta")
        return False
    return True

# 3. Execução do Sistema
if login():
    st.sidebar.title("Navegação")
    menu = st.sidebar.radio("Ir para:", ["🛒 PDV (Vendas)", "👥 Gerenciar Clientes", "📦 Gerenciar Estoque"])

    # --- ABA DE CLIENTES ---
    if menu == "👥 Gerenciar Clientes":
        st.header("👥 Gestão de Clientes")
        
        # Formulário para Adicionar
        with st.expander("➕ Adicionar Novo Cliente", expanded=False):
            with st.form("form_cliente"):
                nome = st.text_input("Nome Completo / Razão Social")
                apelido = st.text_input("Apelido / Nome Fantasia")
                col1, col2, col3 = st.columns([2, 2, 1])
                cpf_cnpj = col1.text_input("CPF / CNPJ")
                tel = col2.text_input("Telefone")
                cep = col3.text_input("CEP")
                
                end = st.text_input("Endereço (Rua, Nº)")
                c1, c2, c3 = st.columns([2, 2, 1])
                bairro = c1.text_input("Bairro")
                cidade = c2.text_input("Cidade")
                uf = c3.text_input("UF", value="CE")

                if st.form_submit_button("Salvar Cliente"):
                    dados = {
                        "nome_completo": nome, "apelido_fantasia": apelido,
                        "cpf_cnpj": cpf_cnpj, "telefone": tel, "cep": cep,
                        "endereco": end, "bairro": bairro, "cidade": cidade
                    }
                    supabase.table("clientes").insert(dados).execute()
                    st.success("Cliente cadastrado!")
                    st.rerun()

        # Listagem e Exclusão
        st.subheader("Lista de Clientes")
        res = supabase.table("clientes").select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df, use_container_width=True)
            
            cliente_para_excluir = st.selectbox("Selecione para excluir", df['nome_completo'].tolist())
            if st.button("🗑️ Excluir Cliente"):
                supabase.table("clientes").delete().eq("nome_completo", cliente_para_excluir).execute()
                st.warning("Cliente removido.")
                st.rerun()

    # --- ABA DE ESTOQUE ---
    elif menu == "📦 Gerenciar Estoque":
        st.header("📦 Controle de Estoque")
        
        with st.expander("➕ Adicionar Novo Produto"):
            with st.form("form_prod"):
                desc = st.text_input("Descrição do Produto")
                c1, c2, c3 = st.columns(3)
                uni = c1.selectbox("Unidade", ["KG", "PC", "CX", "UNI"])
                prc = c2.number_input("Preço de Venda", min_value=0.0)
                est = c3.number_input("Estoque Atual", min_value=0.0)
                if st.form_submit_button("Salvar"):
                    supabase.table("produtos").insert({"descricao": desc, "unidade": uni, "preco_venda": prc, "estoque_atual": est}).execute()
                    st.success("Produto salvo!")
                    st.rerun()

        res_p = supabase.table("produtos").select("*").execute()
        if res_p.data:
            df_p = pd.DataFrame(res_p.data)
            st.dataframe(df_p, use_container_width=True)
            
            prod_del = st.selectbox("Selecione para excluir", df_p['descricao'].tolist())
            if st.button("🗑️ Excluir Produto"):
                supabase.table("produtos").delete().eq("descricao", prod_del).execute()
                st.rerun()

    # --- ABA DE VENDAS (PDV) ---
    elif menu == "🛒 PDV (Vendas)":
        st.header("🛒 Lançar Pedido")
        
        # Puxar dados para os menus de seleção
        c_data = supabase.table("clientes").select("nome_completo, endereco, bairro, cep").execute()
        p_data = supabase.table("produtos").select("descricao, preco_venda").execute()
        
        lista_c = [c['nome_completo'] for c in c_data.data] if c_data.data else []
        lista_p = [p['descricao'] for p in p_data.data] if p_data.data else []

        c_sel = st.selectbox("Cliente", [""] + lista_c)
        if c_sel:
            detalhe = next(c for c in c_data.data if c['nome_completo'] == c_sel)
            st.caption(f"📍 Entrega: {detalhe['endereco']}, {detalhe['bairro']} - CEP: {detalhe['cep']}")

        p_sel = st.selectbox("Produto", [""] + lista_p)
        if p_sel:
            detalhe_p = next(p for p in p_data.data if p['descricao'] == p_sel)
            col_v, col_q = st.columns(2)
            preco = col_v.number_input("Preço Unit.", value=float(detalhe_p['preco_venda']))
            qtd = col_q.number_input("Qtd", min_value=1)
            st.subheader(f"Total: R$ {preco * qtd:.2f}")
            
            if st.button("✅ Finalizar Venda"):
                st.success("Venda registrada com sucesso!")
