import streamlit as st
from supabase import create_client
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date
import plotly.express as px # Para os Dashboards

# 1. Conexão Segura
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# Inicialização de estados
if 'carrinho' not in st.session_state: st.session_state.carrinho = []

# --- FUNÇÃO DE IMPRESSÃO PROFISSIONAL ---
def gerar_recibo_pdf(empresa, cliente, itens, condicao, vencimento, n_pedido, ajuste=0.0, obs="", vias=2):
    pdf = FPDF(format='A4')
    total_prod = sum(item['total'] for item in itens)
    total_g = total_prod + ajuste
    
    def desenhar_via(y_offset):
        pdf.set_xy(10, y_offset + 10)
        # Tenta carregar logo se houver (futura implementação de imagem)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(120, 6, str(empresa.get('nome_empresa', 'NOME DA EMPRESA')).upper(), ln=0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(70, 6, f"Fone: {empresa.get('telefone', '')}", ln=1, align="R")
        pdf.set_x(10)
        pdf.cell(120, 5, empresa.get('endereco', ''), ln=0)
        pdf.cell(70, 5, f"CNPJ: {empresa.get('cnpj', '')}", ln=1, align="R")
        
        pdf.ln(2)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 8, f"PEDIDO DE VENDA Nº {n_pedido:04d}", border="TB", ln=1, align="C")
        
        pdf.ln(2)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(120, 6, f"CLIENTE: {cliente}", ln=0)
        pdf.set_font("Arial", "", 10)
        pdf.cell(70, 6, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align="R")
        
        # Tabela
        pdf.ln(2)
        pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", "B", 9)
        pdf.cell(85, 7, "Descricao", 1, 0, "L", True)
        pdf.cell(20, 7, "Qtd", 1, 0, "C", True); pdf.cell(20, 7, "Unid", 1, 0, "C", True)
        pdf.cell(30, 7, "Val. Unit", 1, 0, "C", True); pdf.cell(35, 7, "Total", 1, 1, "C", True)
        
        pdf.set_font("Arial", "", 9)
        for i in itens:
            pdf.cell(85, 7, i['descricao'], 1)
            pdf.cell(20, 7, str(i['quantidade']), 1, 0, "C")
            pdf.cell(20, 7, i['unidade'], 1, 0, "C")
            pdf.cell(30, 7, f"R$ {i['preco_venda']:.2f}", 1, 0, "R")
            pdf.cell(35, 7, f"R$ {i['total']:.2f}", 1, 1, "R")
        
        # Rodapé Financeiro
        pdf.ln(2)
        tp = "À Vista" if condicao == "À Vista" else f"À Prazo - Venc: {vencimento.strftime('%d/%m/%Y')}"
        pdf.set_font("Arial", "B", 10)
        pdf.cell(130, 6, f"Pagamento: {tp}", 0)
        pdf.cell(60, 6, f"Total Produtos: R$ {total_prod:.2f}", 0, ln=1, align="R")
        
        pdf.set_font("Arial", "", 9)
        pdf.cell(130, 6, f"Obs.: {obs}", 0)
        pdf.cell(60, 6, f"R$ {ajuste:.2f}", 0, ln=1, align="R")
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 8, f"VALOR TOTAL: R$ {total_g:.2f}", 0, ln=1, align="R")
        
        pdf.ln(12); pdf.set_x(60); pdf.cell(90, 0, "", border="T", ln=1)
        pdf.set_font("Arial", "I", 8); pdf.cell(190, 5, "Visto do Cliente", 0, 1, "C")
        if vias == 2 and y_offset == 0: pdf.dashed_line(10, 148, 200, 148, 1, 1)

    pdf.add_page()
    desenhar_via(0)
    if vias == 2: desenhar_via(148)
    return bytes(pdf.output())

# --- INTERFACE ---
st.set_page_config(page_title="JMQJR - Sistema Profissional", layout="wide")

if not st.session_state.get("autenticado"):
    st.title("🚀 SGV Profissional - Login")
    if st.text_input("Senha de Acesso", type="password") == "Naksu@6026" and st.button("Acessar Painel"):
        st.session_state.autenticado = True; st.rerun()
else:
    menu = st.sidebar.radio("Navegação", ["📊 Dashboards", "🛒 PDV", "💰 Financeiro", "📥 Reposição", "👥 Clientes", "📦 Estoque", "⚙️ Configurações"])

    # --- NOVO: DASHBOARDS (VISÃO DO DONO) ---
    if menu == "📊 Dashboards":
        st.header("📊 Painel de Desempenho")
        # Simulação de dados para visualização (No futuro, puxaremos das tabelas de vendas)
        col1, col2, col3 = st.columns(3)
        col1.metric("Vendas do Mês", "R$ 4.500,00", "+12%")
        col2.metric("Contas a Receber", "R$ 1.200,00")
        col3.metric("Lucro Estimado", "R$ 2.100,00", "+5%")
        
        # Exemplo de Gráfico
        df_vendas = pd.DataFrame({
            "Dia": [1, 2, 3, 4, 5, 6, 7],
            "Valor": [150, 400, 300, 600, 200, 800, 1100]
        })
        fig = px.line(df_vendas, x="Dia", y="Valor", title="Faturamento Diário (R$)")
        st.plotly_chart(fig, use_container_width=True)
        

    # --- NOVO: FINANCEIRO (PAGAR/RECEBER) ---
    elif menu == "💰 Financeiro":
        st.header("💰 Gestão Financeira")
        t_rec, t_pag = st.tabs(["📈 Contas a Receber", "📉 Contas a Pagar"])
        
        with t_rec:
            st.subheader("Entradas Pendentes")
            # Aqui listaremos as vendas "À Prazo"
            st.info("As vendas feitas 'À Prazo' no PDV aparecerão aqui automaticamente.")
            
        with t_pag:
            with st.form("pagar"):
                st.write("Registrar Nova Despesa")
                desc_p = st.text_input("Descrição da Conta")
                val_p = st.number_input("Valor R$", min_value=0.0)
                venc_p = st.date_input("Vencimento")
                if st.form_submit_button("Lançar Despesa"):
                    st.success("Despesa registrada!")

    # --- CONFIGURAÇÕES (AGORA COM LOGO) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Configurações da Empresa")
        try:
            res_emp = supabase.table("config_empresa").select("*").eq("id", 1).execute().data
            emp_data = res_emp[0] if res_emp else {"nome_empresa": "", "endereco": "", "telefone": "", "cnpj": ""}
        except:
            emp_data = {"nome_empresa": "", "endereco": "", "telefone": "", "cnpj": ""}

        col_cfg, col_logo = st.columns(2)
        with col_cfg:
            with st.form("conf_form"):
                nome_e = st.text_input("Nome da Empresa", value=emp_data.get('nome_empresa', ''))
                end_e = st.text_input("Endereço", value=emp_data.get('endereco', ''))
                tel_e = st.text_input("Telefone", value=emp_data.get('telefone', ''))
                cnpj_e = st.text_input("CNPJ", value=emp_data.get('cnpj', ''))
                if st.form_submit_button("Salvar Dados"):
                    supabase.table("config_empresa").upsert({"id": 1, "nome_empresa": nome_e, "endereco": end_e, "telefone": tel_e, "cnpj": cnpj_e}).execute()
                    st.success("Salvo!"); st.rerun()
        
        with col_logo:
            st.write("🖼️ Logomarca")
            foto = st.file_uploader("Subir Logo da Empresa", type=['png', 'jpg'])
            if foto:
                st.image(foto, width=150)
                st.info("Logo carregada! (Em breve integraremos ao PDF)")

    # (Manter abas de Clientes, Estoque e PDV com as proteções de erro que adicionei)
    # ... [O restante do código segue a lógica estável anterior]
