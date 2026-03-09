import streamlit as st
from supabase import create_client
import pandas as pd

# 1. Configurações de Conexão
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"

supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

def login():
    st.set_page_config(page_title="Derlyana Alimentos", layout="wide")
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.title("JMQJR - SGV")
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
    st.sidebar.title("MENU")
    menu = st.sidebar.radio("Navegação:", ["🛒 PDV (Vendas)", "👥 Clientes", "📦 Estoque"])

    # --- ABA DE ESTOQUE ---
    if menu == "📦 Estoque":
        st.header("📦 Gerenciar Estoque")
        with st.expander("➕ Adicionar Novo Produto"):
            with st.form("form_prod"):
                desc_in = st.text_input("Descrição do Produto")
                c1, c2, c3 = st.columns(3)
                uni_in = c1.selectbox("Unidade", ["KG", "PC", "CX", "UNI"])
                prc_in = c2.number_input("Preço de Venda", min_value=0.0)
                est_in = c3.number_input("Estoque Inicial", min_value=0.0)
                if st.form_submit_button("Salvar Produto"):
                    # AJUSTADO: Nomes das colunas exatamente como na sua tabela
                    dados_prod = {
                        "descricao": desc_in, 
                        "unidade": uni_in, 
                        "preco_venda": prc_in, 
                        "estoque_atual": est_in
                    }
                    try:
                        supabase.table("produtos").insert(dados_prod).execute()
                        st.success("Produto salvo com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro no estoque: {e}")

        try:
            # Lista os produtos buscando as colunas corretas
            res_p = supabase.table("produtos").select("descricao, unidade, preco_venda, estoque_atual").execute()
            if res_p.data:
                st.dataframe(pd.DataFrame(res_p.data), use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao carregar produtos: {e}")

    # --- ABA DE CLIENTES ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        with st.expander("➕ Novo Cadastro"):
            with st.form("form_cli"):
                n_in = st.text_input("Nome/Razão Social")
                a_in = st.text_input("Apelido / Nome Fantasia")
                c1, c2, c3 = st.columns([2, 2, 1])
                d_in = c1.text_input("CPF/CNPJ")
                t_in = c2.text_input("Telefone")
                cp_in = c3.text_input("CEP")
                e_in = st.text_input("Endereço")
                b_in = st.text_input("Bairro")
                ci_in = st.text_input("Cidade")
                
                if st.form_submit_button("Cadastrar Cliente"):
                    dados_cli = {
                        "nome_completo": n_in, "apelido_fantasia": a_in, 
                        "cpf_cnpj": d_in, "telefone": t_in, "cep": cp_in, 
                        "endereco": e_in, "bairro": b_in, "cidade": ci_in
                    }
                    try:
                        supabase.table("Clientes").insert(dados_cli).execute()
                        st.success("Cliente cadastrado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao cadastrar: {e}")

        try:
            res_c = supabase.table("Clientes").select("*").execute()
            if res_c.data:
                st.dataframe(pd.DataFrame(res_c.data), use_container_width=True)
        except:
            st.info("Nenhum cliente cadastrado.")

    # --- ABA DE VENDAS ---
    elif menu == "🛒 PDV (Vendas)":
        st.header("🛒 Lançar Pedido")
        try:
            # Busca respeitando os nomes corrigidos
            c_list = supabase.table("Clientes").select("nome_completo, endereco, bairro").execute()
            p_list = supabase.table("produtos").select("descricao, preco_venda").execute()
            
            nomes_c = [c['nome_completo'] for c in c_list.data] if c_list.data else []
            nomes_p = [p['descricao'] for p in p_list.data] if p_list.data else []

            col_c, col_p = st.columns(2)
            cli_sel = col_c.selectbox("Selecione o Cliente", [""] + nomes_c)
            prod_sel = col_p.selectbox("Selecione o Produto", [""] + nomes_p)
            
            if prod_sel:
                det_p = next(p for p in p_list.data if p['descricao'] == prod_sel)
                c_v, c_q = st.columns(2)
                valor = c_v.number_input("Preço Unitário", value=float(det_p['preco_venda']))
                quant = c_q.number_input("Quantidade", min_value=1)
                st.subheader(f"Total: R$ {valor * quant:.2f}")
                
                if st.button("Finalizar Venda"):
                    st.balloons()
                    st.success("Pedido simulado com sucesso!")
        except Exception as e:
            st.warning(f"Aguardando dados: {e}")
