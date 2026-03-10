import streamlit as st
from supabase import create_client
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import io

# 1. Conexão
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# --- FUNÇÃO DE IMPRESSÃO PROFISSIONAL ---
def gerar_recibo_pdf(empresa, pedido, vias=1):
    pdf = FPDF(format='A4')
    
    def desenhar_via(y_offset):
        # Cabeçalho
        pdf.set_xy(10, y_offset + 10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(130, 6, empresa['nome_empresa'], ln=0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(50, 6, f"Fone: {empresa['telefone']}", ln=1, align="R")
        
        pdf.set_x(10)
        pdf.cell(130, 5, empresa['endereco'], ln=0)
        pdf.cell(50, 5, f"CNPJ: {empresa['cnpj']}", ln=1, align="R")
        
        pdf.set_x(10)
        pdf.cell(190, 5, f"E-mail: {empresa['email']}", ln=1)
        
        pdf.ln(2)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 7, f"PEDIDO DE VENDA Nº {pedido.get('id', 'S/N')}", border="TB", ln=1, align="C")
        
        # Dados do Cliente
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(190, 5, f"CLIENTE: {pedido['cliente']}", ln=1)
        pdf.set_font("Arial", "", 9)
        pdf.cell(190, 5, f"ENDEREÇO: {pedido.get('endereco', 'N/A')}", ln=1)
        
        # Tabela de Itens
        pdf.ln(2)
        pdf.set_font("Arial", "B", 8)
        pdf.cell(90, 6, "Descrição", 1)
        pdf.cell(20, 6, "Qtd", 1)
        pdf.cell(25, 6, "Unid", 1)
        pdf.cell(25, 6, "Valor Un.", 1)
        pdf.cell(30, 6, "Total", 1, ln=1)
        
        pdf.set_font("Arial", "", 8)
        pdf.cell(90, 6, pedido['produto'], 1)
        pdf.cell(20, 6, str(pedido['quantidade']), 1)
        pdf.cell(25, 6, pedido.get('unidade', 'UN'), 1)
        pdf.cell(25, 6, f"R$ {pedido['valor_unitario']:.2f}", 1)
        pdf.cell(30, 6, f"R$ {pedido['total']:.2f}", 1, ln=1)
        
        # Rodapé da Via
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(130, 5, f"Pagamento: {pedido['condicao']}", 0)
        pdf.cell(60, 5, f"TOTAL: R$ {pedido['total']:.2f}", 0, ln=1, align="R")
        
        if vias == 2 and y_offset == 0:
            pdf.dashed_line(10, 148, 200, 148, 1, 1) # Linha de corte

    pdf.add_page()
    desenhar_via(0)
    if vias == 2:
        desenhar_via(148) # Inicia a segunda via no meio da folha A4
        
    return pdf.output(dest='S')

if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🍎 Derlyana Alimentos - Login")
    if st.text_input("Senha", type="password") == "1234" and st.button("Entrar"):
        st.session_state.autenticado = True
        st.rerun()
else:
    menu = st.sidebar.radio("Navegação", ["🛒 PDV", "👥 Clientes", "📦 Estoque", "⚙️ Configurações"])

    # --- ABA CONFIGURAÇÕES (EDITAR MINHA EMPRESA) ---
    if menu == "⚙️ Configurações":
        st.header("⚙️ Dados da Minha Empresa")
        dados_emp = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
        
        with st.form("form_empresa"):
            n_e = st.text_input("Nome da Empresa", value=dados_emp['nome_empresa'])
            e_e = st.text_input("Endereço", value=dados_emp['endereco'])
            t_e = st.text_input("Telefone", value=dados_emp['telefone'])
            c_e = st.text_input("CNPJ", value=dados_emp['cnpj'])
            m_e = st.text_input("E-mail", value=dados_emp['email'])
            if st.form_submit_button("Salvar Alterações"):
                supabase.table("config_empresa").update({"nome_empresa":n_e, "endereco":e_e, "telefone":t_e, "cnpj":c_e, "email":m_e}).eq("id", 1).execute()
                st.success("Dados atualizados!")
                st.rerun()

    # --- ABA CLIENTES (EDITAR/EXCLUIR) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        res_c = supabase.table("Clientes").select("*").execute()
        df_c = pd.DataFrame(res_c.data)
        
        tab1, tab2 = st.tabs(["Listar/Editar", "Novo Cadastro"])
        with tab2:
            with st.form("novo_cli"):
                # ... (campos de cadastro aqui) ...
                if st.form_submit_button("Salvar"): st.write("Cadastrado")
        with tab1:
            if not df_c.empty:
                sel_c = st.selectbox("Selecione um cliente para editar/excluir", df_c['nome_completo'])
                item = df_c[df_c['nome_completo'] == sel_c].iloc[0]
                
                with st.expander(f"Editar: {sel_c}"):
                    nome_edit = st.text_input("Nome", value=item['nome_completo'])
                    if st.button("Atualizar Cliente"):
                        supabase.table("Clientes").update({"nome_completo": nome_edit}).eq("id", item['id']).execute()
                        st.rerun()
                    if st.button("❌ EXCLUIR CLIENTE", help="Cuidado! Ação irreversível"):
                        supabase.table("Clientes").delete().eq("id", item['id']).execute()
                        st.rerun()
                st.dataframe(df_c)

    # --- ABA ESTOQUE (EDITAR/EXCLUIR) ---
    elif menu == "📦 Estoque":
        st.header("📦 Gerenciar Estoque")
        res_p = supabase.table("produtos").select("*").execute()
        df_p = pd.DataFrame(res_p.data)
        
        if not df_p.empty:
            sel_p = st.selectbox("Selecione o produto", df_p['descricao'])
            p_item = df_p[df_p['descricao'] == sel_p].iloc[0]
            
            c1, c2 = st.columns(2)
            novo_p = c1.number_input("Preço", value=float(p_item['preco_venda']))
            novo_e = c2.number_input("Estoque", value=float(p_item['estoque_atual']))
            
            if st.button("Salvar Alterações"):
                supabase.table("produtos").update({"preco_venda": novo_p, "estoque_atual": novo_e}).eq("id", p_item['id']).execute()
                st.rerun()
            if st.button("🗑️ Excluir Produto"):
                supabase.table("produtos").delete().eq("id", p_item['id']).execute()
                st.rerun()
        st.dataframe(df_p)

    # --- PDV (VENDAS COM OPÇÃO DE 1 OU 2 VIAS) ---
    elif menu == "🛒 PDV":
        st.header("🛒 Lançar Pedido")
        # ... (Lógica de seleção de cliente e produto igual à anterior) ...
        # Adição de Condição de Pagamento e Vias
        condicao = st.selectbox("Condição de Pagamento", ["À Vista", "À Prazo - 7 dias", "À Prazo - 15 dias", "Cartão"])
        opcao_vias = st.radio("Impressão Ecológica", ["1 Via (Meia Folha A4)", "2 Vias (Folha Inteira A4)"])
        
        if st.button("Finalizar e Gerar PDF"):
            # (Aqui você faz o insert na tabela de pedidos e o update no estoque como fizemos ontem)
            # Simulando dados para o PDF
            dados_pdf = {
                "cliente": "Cliente Exemplo", "produto": "Produto X", "quantidade": 10,
                "valor_unitario": 5.0, "total": 50.0, "condicao": condicao
            }
            vias_num = 1 if "1 Via" in opcao_vias else 2
            emp_info = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
            pdf_bytes = gerar_recibo_pdf(emp_info, dados_pdf, vias=vias_num)
            st.download_button("📄 Baixar Pedido", pdf_bytes, "pedido.pdf", "application/pdf")
