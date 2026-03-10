import streamlit as st
from supabase import create_client
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date
import io

# 1. Conexão (Mantenha suas credenciais)
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

# --- Inicializar a Cesta de Compras ---
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# --- FUNÇÃO DE IMPRESSÃO PROFISSIONAL (Suporta múltiplos itens) ---
def gerar_recibo_pdf(empresa, cliente_nome, itens, condicao, vencimento, vias=1):
    pdf = FPDF(format='A4')
    total_geral = sum(item['total'] for item in itens)
    
    def desenhar_via(y_offset):
        # Cabeçalho da Empresa
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
        
        # Dados do Cliente e Pagamento
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(120, 5, f"CLIENTE: {cliente_nome}", ln=0)
        pdf.cell(70, 5, f"DATA: {datetime.now().strftime('%d/%m/%Y')}", ln=1, align="R")
        pdf.set_font("Arial", "", 9)
        pdf.cell(120, 5, f"PAGAMENTO: {condicao}", ln=0)
        pdf.cell(70, 5, f"VENCIMENTO: {vencimento}", ln=1, align="R")
        
        # Tabela de Itens
        pdf.ln(3)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 8)
        pdf.cell(90, 6, "Descrição", 1, 0, "L", True)
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
        
        # Totalizador
        pdf.set_font("Arial", "B", 10)
        pdf.cell(160, 8, "VALOR TOTAL DO PEDIDO:", 0, 0, "R")
        pdf.cell(30, 8, f"R$ {total_geral:.2f}", 0, 1, "R")
        
        if vias == 2 and y_offset == 0:
            pdf.dashed_line(10, 148, 200, 148, 1, 1)

    pdf.add_page()
    desenhar_via(0)
    if vias == 2:
        desenhar_via(148)
    return pdf.output(dest='S')

# --- LÓGICA DE LOGIN ---
if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🍎 Derlyana Alimentos")
    if st.text_input("Senha", type="password") == "1234" and st.button("Entrar"):
        st.session_state.autenticado = True
        st.rerun()
else:
    menu = st.sidebar.radio("Navegação", ["🛒 PDV", "👥 Clientes", "📦 Estoque", "⚙️ Configurações"])

    # (Mantenha as abas de Clientes, Estoque e Configurações como estão)

    # --- ABA PDV (REFORMULADA PARA MÚLTIPLOS ITENS) ---
    if menu == "🛒 PDV":
        st.header("🛒 Novo Pedido")
        
        # 1. Seleção do Cliente
        res_c = supabase.table("Clientes").select("nome_completo").execute()
        clientes = [c['nome_completo'] for c in res_c.data]
        cliente_sel = st.selectbox("Selecione o Cliente", [""] + clientes)
        
        # 2. Adicionar Produtos à Cesta
        st.divider()
        col1, col2, col3, col4 = st.columns([3,1,1,1])
        
        res_p = supabase.table("produtos").select("*").execute()
        prod_dict = {p['descricao']: p for p in res_p.data}
        
        p_sel = col1.selectbox("Produto", [""] + list(prod_dict.keys()))
        qtd = col2.number_input("Qtd", min_value=0.1, step=0.1)
        
        if col4.button("➕ Adicionar"):
            if p_sel:
                p_info = prod_dict[p_sel]
                item = {
                    "descricao": p_sel,
                    "quantidade": qtd,
                    "unidade": p_info['unidade'],
                    "preco_venda": p_info['preco_venda'],
                    "total": qtd * p_info['preco_venda']
                }
                st.session_state.carrinho.append(item)
                st.toast(f"{p_sel} adicionado!")

        # 3. Exibir Cesta
        if st.session_state.carrinho:
            df_cart = pd.DataFrame(st.session_state.carrinho)
            st.table(df_cart)
            if st.button("🗑️ Limpar Carrinho"):
                st.session_state.carrinho = []
                st.rerun()
            
            total_pedido = df_cart['total'].sum()
            st.subheader(f"Total: R$ {total_pedido:.2f}")
            
            # 4. Condições de Pagamento e Vencimento
            st.divider()
            c1, c2, c3 = st.columns(3)
            cond = c1.selectbox("Pagamento", ["À Vista", "À Prazo"])
            
            vencimento = date.today()
            if cond == "À Prazo":
                vencimento = c2.date_input("Data de Vencimento", min_value=date.today())
            
            vias = c3.radio("Vias", [1, 2])

            if st.button("✅ FINALIZAR VENDA"):
                # Aqui você salvaria o pedido no banco (opcional para agora)
                # E daria baixa no estoque de cada item do carrinho
                
                emp_info = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
                pdf_bytes = gerar_recibo_pdf(emp_info, cliente_sel, st.session_state.carrinho, cond, vencimento, vias)
                
                st.download_button("📄 Baixar Pedido em PDF", pdf_bytes, f"pedido_{cliente_sel}.pdf", "application/pdf")
                st.success("Venda processada!")
