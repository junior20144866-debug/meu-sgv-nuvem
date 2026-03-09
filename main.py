import streamlit as st
from supabase import create_client
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# 1. Configurações de Conexão
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# Função para Gerar PDF do Pedido
def gerar_pdf(dados_venda):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "DERLYANA ALIMENTOS - PEDIDO", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(190, 10, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.cell(190, 10, f"Cliente: {dados_venda['cliente']}", ln=True)
    pdf.line(10, 50, 200, 50)
    pdf.ln(5)
    pdf.cell(100, 10, "Produto")
    pdf.cell(30, 10, "Qtd")
    pdf.cell(30, 10, "Unit.")
    pdf.cell(30, 10, "Total", ln=True)
    pdf.cell(100, 10, f"{dados_venda['produto']}")
    pdf.cell(30, 10, f"{dados_venda['quantidade']}")
    pdf.cell(30, 10, f"R$ {dados_venda['valor_unitario']:.2f}")
    pdf.cell(30, 10, f"R$ {dados_venda['total']:.2f}", ln=True)
    pdf.ln(20)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, f"TOTAL DO PEDIDO: R$ {dados_venda['total']:.2f}", ln=True, align="R")
    return pdf.output(dest='S')

def login():
    st.set_page_config(page_title="Derlyana Alimentos", layout="wide")
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if not st.session_state.autenticado:
        st.title("🍎 Derlyana Alimentos - SGV")
        senha = st.text_input("Senha Master", type="password")
        if st.button("Entrar"):
            if senha == "1234":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta")
        return False
    return True

if login():
    st.sidebar.title("MENU")
    menu = st.sidebar.radio("Navegação:", ["🛒 PDV (Vendas)", "👥 Clientes", "📦 Estoque", "📊 Histórico"])

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
                    dados_prod = {"descricao": desc_in, "unidade": uni_in, "preco_venda": prc_in, "estoque_atual": est_in}
                    supabase.table("produtos").insert(dados_prod).execute()
                    st.success("Produto salvo!")
                    st.rerun()
        res_p = supabase.table("produtos").select("*").execute()
        if res_p.data: st.dataframe(pd.DataFrame(res_p.data), use_container_width=True)

    # --- ABA DE CLIENTES ---
    elif menu == "👥 Clientes":
        st.header("👥 Clientes")
        with st.expander("➕ Novo Cadastro"):
            with st.form("form_cli"):
                n_in = st.text_input("Nome/Razão Social")
                a_in = st.text_input("Apelido")
                doc_in = st.text_input("CPF/CNPJ")
                tel_in = st.text_input("Telefone")
                if st.form_submit_button("Cadastrar"):
                    dados_cli = {"nome_completo": n_in, "apelido_fantasia": a_in, "cpf_cnpj": doc_in, "telefone": tel_in}
                    supabase.table("Clientes").insert(dados_cli).execute()
                    st.success("Cliente salvo!")
                    st.rerun()
        res_c = supabase.table("Clientes").select("*").execute()
        if res_c.data: st.dataframe(pd.DataFrame(res_c.data), use_container_width=True)

    # --- PDV COM VENDA REAL E IMPRESSÃO ---
    elif menu == "🛒 PDV (Vendas)":
        st.header("🛒 Lançar Pedido")
        c_list = supabase.table("Clientes").select("nome_completo").execute()
        p_list = supabase.table("produtos").select("descricao, preco_venda, estoque_atual").execute()
        
        nomes_c = [c['nome_completo'] for c in c_list.data] if c_list.data else []
        nomes_p = [p['descricao'] for p in p_list.data] if p_list.data else []

        col_c, col_p = st.columns(2)
        cli_sel = col_c.selectbox("Selecione o Cliente", [""] + nomes_c)
        prod_sel = col_p.selectbox("Selecione o Produto", [""] + nomes_p)
        
        if prod_sel:
            det_p = next(p for p in p_list.data if p['descricao'] == prod_sel)
            st.info(f"📊 Estoque disponível: {det_p['estoque_atual']}")
            
            v_unit = st.number_input("Preço Unitário", value=float(det_p['preco_venda']))
            quant = st.number_input("Quantidade", min_value=0.1, step=0.1)
            total = v_unit * quant
            st.subheader(f"Total: R$ {total:.2f}")
            
            if st.button("Finalizar e Gerar Pedido"):
                if quant <= det_p['estoque_atual']:
                    # 1. Salvar na tabela de pedidos
                    dados_venda = {
                        "cliente": cli_sel, "produto": prod_sel, 
                        "quantidade": quant, "valor_unitario": v_unit, "total": total
                    }
                    supabase.table("pedidos").insert(dados_venda).execute()
                    
                    # 2. Baixar estoque
                    novo_estoque = det_p['estoque_atual'] - quant
                    supabase.table("produtos").update({"estoque_atual": novo_estoque}).eq("descricao", prod_sel).execute()
                    
                    st.success("Venda registrada com sucesso!")
                    
                    # 3. Gerar PDF para Download
                    pdf_bytes = gerar_pdf(dados_venda)
                    st.download_button(label="📄 Baixar/Imprimir Pedido", data=pdf_bytes, file_name=f"pedido_{cli_sel}.pdf", mime="application/pdf")
                else:
                    st.error("Estoque insuficiente!")

    # --- ABA DE HISTÓRICO ---
    elif menu == "📊 Histórico":
        st.header("📊 Últimas Vendas")
        res_ped = supabase.table("pedidos").select("*").order("data", desc=True).execute()
        if res_ped.data: st.dataframe(pd.DataFrame(res_ped.data), use_container_width=True)
