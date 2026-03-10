import streamlit as st
from supabase import create_client
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# 1. Conexão
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- FUNÇÃO DE IMPRESSÃO ---
def gerar_recibo_pdf(empresa, cliente_nome, itens, condicao, vencimento, vias=1):
    pdf = FPDF(format='A4')
    total_geral = sum(item['total'] for item in itens)
    data_venc_br = vencimento.strftime('%d/%m/%Y')
    data_hoje_br = datetime.now().strftime('%d/%m/%Y')
    
    def desenhar_via(y_offset):
        pdf.set_xy(10, y_offset + 10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(130, 6, empresa['nome_empresa'], ln=0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(50, 6, f"Fone: {empresa['telefone']}", ln=1, align="R")
        pdf.set_x(10)
        pdf.cell(130, 5, empresa.get('endereco', ''), ln=0)
        pdf.cell(50, 5, f"CNPJ: {empresa.get('cnpj', '')}", ln=1, align="R")
        pdf.ln(2)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(190, 7, "PEDIDO DE VENDA", border="TB", ln=1, align="C")
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(120, 5, f"CLIENTE: {cliente_nome}", ln=0)
        pdf.cell(70, 5, f"DATA: {data_hoje_br}", ln=1, align="R")
        pdf.ln(3)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 8)
        pdf.cell(90, 6, "Descricao", 1, 0, "L", True)
        pdf.cell(20, 6, "Qtd", 1, 0, "C", True)
        pdf.cell(20, 6, "Unid", 1, 0, "C", True)
        pdf.cell(30, 6, "Val. Unit", 1, 0, "C", True)
        pdf.cell(30, 6, "Total", 1, 1, "C", True)
        pdf.set_font("Arial", "", 8)
        for item in itens:
            pdf.cell(90, 6, item['descricao'], 1)
            pdf.cell(20, 6, str(item['quantidade']), 1, 0, "C")
            pdf.cell(20, 6, item['unidade'], 1, 0, "C")
            pdf.cell(30, 6, f"R$ {item['preco_venda']:.2f}", 1, 0, "R")
            pdf.cell(30, 6, f"R$ {item['total']:.2f}", 1, 1, "R")
        pdf.set_font("Arial", "B", 10)
        pdf.cell(160, 8, "VALOR TOTAL:", 0, 0, "R")
        pdf.cell(30, 8, f"R$ {total_geral:.2f}", 0, 1, "R")
        if vias == 2 and y_offset == 0:
            pdf.dashed_line(10, 148, 200, 148, 1, 1)

    pdf.add_page()
    desenhar_via(0)
    if vias == 2: desenhar_via(148)
    return bytes(pdf.output())

# --- LOGIN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("JMQJR - SGV - Sales system") # NOME ALTERADO
    senha_input = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if senha_input == "Naksu@6026": # SENHA ALTERADA
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta")
else:
    # MENU COMPLETO REATIVADO
    menu = st.sidebar.radio("Navegação", ["🛒 PDV", "👥 Clientes", "📦 Estoque", "⚙️ Configurações"])

    # --- ABA CONFIGURAÇÕES ---
    if menu == "⚙️ Configurações":
        st.header("⚙️ Configurações do Sistema")
        dados_emp = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
        with st.form("conf"):
            n = st.text_input("Nome Empresa", value=dados_emp['nome_empresa'])
            e = st.text_input("Endereço", value=dados_emp['endereco'])
            t = st.text_input("Telefone", value=dados_emp['telefone'])
            c = st.text_input("CNPJ", value=dados_emp['cnpj'])
            em = st.text_input("Email", value=dados_emp['email'])
            if st.form_submit_button("Atualizar Dados"):
                supabase.table("config_empresa").update({"nome_empresa":n,"endereco":e,"telefone":t,"cnpj":c,"email":em}).eq("id",1).execute()
                st.success("Dados atualizados!")

    # --- ABA CLIENTES ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        res_c = supabase.table("Clientes").select("*").execute()
        df_c = pd.DataFrame(res_c.data)
        if not df_c.empty:
            sel = st.selectbox("Selecione para Editar/Excluir", df_c['nome_completo'])
            item = df_c[df_c['nome_completo'] == sel].iloc[0]
            if st.button("🗑️ Excluir Cliente"):
                supabase.table("Clientes").delete().eq("id", item['id']).execute()
                st.rerun()
        st.dataframe(df_c)

    # --- ABA ESTOQUE ---
    elif menu == "📦 Estoque":
        st.header("📦 Estoque")
        res_p = supabase.table("produtos").select("*").execute()
        df_p = pd.DataFrame(res_p.data)
        if not df_p.empty:
            sel_p = st.selectbox("Produto", df_p['descricao'])
            p_item = df_p[df_p['descricao'] == sel_p].iloc[0]
            if st.button("🗑️ Excluir Produto"):
                supabase.table("produtos").delete().eq("id", p_item['id']).execute()
                st.rerun()
        st.dataframe(df_p)

    # --- ABA PDV ---
    elif menu == "🛒 PDV":
        st.header("🛒 Novo Pedido")
        # Interface do Carrinho
        res_c = supabase.table("Clientes").select("nome_completo").execute()
        clientes = [c['nome_completo'] for c in res_c.data]
        cliente_sel = st.selectbox("Cliente", [""] + clientes)
        
        st.divider()
        col1, col2, col3 = st.columns([3,1,1])
        res_p = supabase.table("produtos").select("*").execute()
        prod_dict = {p['descricao']: p for p in res_p.data}
        p_sel = col1.selectbox("Produto", [""] + list(prod_dict.keys()))
        qtd = col2.number_input("Qtd", min_value=0.1, step=0.1)
        
        if col3.button("➕"):
            if p_sel:
                p = prod_dict[p_sel]
                st.session_state.carrinho.append({"descricao":p_sel, "quantidade":qtd, "unidade":p['unidade'], "preco_venda":p['preco_venda'], "total":qtd*p['preco_venda']})
                st.rerun()

        if st.session_state.carrinho:
            st.table(pd.DataFrame(st.session_state.carrinho))
            if st.button("🗑️ Limpar"): st.session_state.carrinho = []; st.rerun()
            
            c1, c2, c3 = st.columns(3)
            cond = c1.selectbox("Pagamento", ["À Vista", "À Prazo"])
            venc = c2.date_input("Vencimento", format="DD/MM/YYYY")
            vias = c3.radio("Vias", [1, 2])

            if st.button("✅ FINALIZAR"):
                emp = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
                pdf = gerar_recibo_pdf(emp, cliente_sel, st.session_state.carrinho, cond, venc, vias)
                st.download_button("📄 Baixar PDF", pdf, "pedido.pdf", "application/pdf")
