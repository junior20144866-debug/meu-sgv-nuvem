import streamlit as st
from supabase import create_client
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# 1. Conexão
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

if 'carrinho' not in st.session_state: st.session_state.carrinho = []

# --- FUNÇÃO DE IMPRESSÃO (CONFORME PEDIDO_1.PDF) ---
def gerar_recibo_pdf(empresa, cliente, itens, condicao, vencimento, n_pedido, ajuste_financeiro=0.0, obs="", vias=2):
    pdf = FPDF(format='A4')
    total_produtos = sum(item['total'] for item in itens)
    total_geral = total_produtos + ajuste_financeiro
    
    def desenhar_via(y_offset):
        pdf.set_xy(10, y_offset + 10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(120, 6, empresa.get('nome_empresa', 'NOME DA EMPRESA'), ln=0)
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
        
        # Tabela de Itens
        pdf.ln(2)
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(85, 7, "Descricao", 1, 0, "L", True)
        pdf.cell(20, 7, "Qtd", 1, 0, "C", True)
        pdf.cell(20, 7, "Unid", 1, 0, "C", True)
        pdf.cell(30, 7, "Val. Unit", 1, 0, "C", True)
        pdf.cell(35, 7, "Total", 1, 1, "C", True)
        
        pdf.set_font("Arial", "", 9)
        for i in itens:
            pdf.cell(85, 7, i['descricao'], 1)
            pdf.cell(20, 7, str(i['quantidade']), 1, 0, "C")
            pdf.cell(20, 7, i['unidade'], 1, 0, "C")
            pdf.cell(30, 7, f"R$ {i['preco_venda']:.2f}", 1, 0, "R")
            pdf.cell(35, 7, f"R$ {i['total']:.2f}", 1, 1, "R")
        
        # Rodapé Financeiro
        pdf.ln(2)
        txt_pgto = "À Vista" if condicao == "À Vista" else f"À Prazo - Venc: {vencimento.strftime('%d/%m/%Y')}"
        pdf.set_font("Arial", "B", 10)
        pdf.cell(130, 6, f"Pagamento: {txt_pgto}", 0)
        pdf.cell(60, 6, f"Total Produtos: R$ {total_produtos:.2f}", 0, ln=1, align="R")
        
        pdf.set_font("Arial", "", 9)
        pdf.cell(130, 6, f"Obs.: {obs}", 0)
        pdf.set_font("Arial", "", 10)
        # Exibe apenas o valor do ajuste (pode ser positivo ou negativo)
        pdf.cell(60, 6, f"R$ {ajuste_financeiro:.2f}", 0, ln=1, align="R")
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 8, f"VALOR TOTAL: R$ {total_geral:.2f}", 0, ln=1, align="R")
        
        # Assinatura do Cliente
        pdf.ln(12)
        pdf.set_x(60)
        pdf.cell(90, 0, "", border="T", ln=1)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(190, 5, "Visto do Cliente", 0, 1, "C")

        if vias == 2 and y_offset == 0:
            pdf.dashed_line(10, 148, 200, 148, 1, 1)

    pdf.add_page()
    desenhar_via(0)
    if vias == 2: desenhar_via(148)
    return bytes(pdf.output())

# --- INTERFACE ---
st.set_page_config(page_title="JMQJR - SGV", layout="wide")

if "autenticado" not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("JMQJR - SGV - Sales system")
    pwd = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if pwd == "Naksu@6026":
            st.session_state.autenticado = True
            st.rerun()
else:
    menu = st.sidebar.radio("Navegação", ["🛒 PDV", "📥 Reposição", "👥 Clientes", "📦 Estoque", "📊 Relatórios", "⚙️ Configurações"])

    # --- ABA RELATÓRIOS (CORRIGIDA) ---
    if menu == "📊 Relatórios":
        st.header("📊 Relatórios do Sistema")
        
        try:
            # Obter nome da empresa para o cabeçalho
            emp_info = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
            st.subheader(f"Relatórios: {emp_info['nome_empresa']}")
        except: st.subheader("Relatórios Gerais")

        tab_p, tab_c = st.tabs(["Produtos e Estoque", "Lista de Clientes"])
        
        with tab_p:
            res_p = supabase.table("produtos").select("descricao, unidade, preco_venda, estoque_atual").execute().data
            if res_p:
                df_p = pd.DataFrame(res_p)
                df_p.columns = ["Descrição", "Unid.", "Preço (R$)", "Estoque Atual"]
                st.dataframe(df_p, use_container_width=True)
            else: st.info("Sem produtos para listar.")

        with tab_c:
            res_c = supabase.table("Clientes").select("nome_completo, cpf_cnpj").execute().data
            if res_c:
                df_c = pd.DataFrame(res_c)
                df_c.columns = ["Nome do Cliente", "Documento (CPF/CNPJ)"]
                st.dataframe(df_c, use_container_width=True)
            else: st.info("Sem clientes cadastrados.")

    # --- ABA PDV ---
    elif menu == "🛒 PDV":
        st.header("🛒 Novo Pedido")
        # Busca dados do Supabase para os selects
        clis_data = supabase.table("Clientes").select("nome_completo").execute().data
        prods_data = supabase.table("produtos").select("*").execute().data
        
        clis = [c['nome_completo'] for c in clis_data] if clis_data else []
        pros = {p['descricao']: p for p in prods_data} if prods_data else {}
        
        cli_v = st.selectbox("Selecione o Cliente", [""] + clis)
        
        st.divider()
        cp, cq, cb = st.columns([3, 1, 1])
        p_sel = cp.selectbox("Produto", [""] + list(pros.keys()))
        q_sel = cq.number_input("Qtd", min_value=0.1, step=0.1)
        if cb.button("➕ Adicionar"):
            if p_sel:
                p_inf = pros[p_sel]
                st.session_state.carrinho.append({"descricao": p_sel, "quantidade": q_sel, "unidade": p_inf['unidade'], "preco_venda": p_inf['preco_venda'], "total": q_sel * p_inf['preco_venda']})
                st.rerun()

        if st.session_state.carrinho:
            st.table(pd.DataFrame(st.session_state.carrinho))
            if st.button("🗑️ Limpar Carrinho"): st.session_state.carrinho = []; st.rerun()
            
            st.divider()
            f1, f2, f3 = st.columns(3)
            cond_v = f1.selectbox("Pagamento", ["À Vista", "À Prazo"])
            venc_v = f2.date_input("Vencimento") if cond_v == "À Prazo" else date.today()
            # AGORA ACEITA VALORES NEGATIVOS PARA DESCONTOS
            ajuste_v = f3.number_input("Taxa (+) ou Desconto (-)", value=0.0, step=0.50)
            obs_v = st.text_input("Observações do Pedido (Aparece no PDF)")
            
            if st.button("✅ FINALIZAR PEDIDO"):
                try:
                    res_n = supabase.table("controle_pedidos").select("ultimo_numero").eq("id", 1).execute().data[0]
                    novo_n = res_n['ultimo_numero'] + 1
                    supabase.table("controle_pedidos").update({"ultimo_numero": novo_n}).eq("id", 1).execute()
                except: novo_n = 1
                
                try: emp = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
                except: emp = {}
                
                pdf = gerar_recibo_pdf(emp, cli_v, st.session_state.carrinho, cond_v, venc_v, novo_n, ajuste_v, obs_v)
                st.download_button("📄 Baixar Pedido", pdf, f"Pedido_{novo_n:04d}.pdf", "application/pdf")
                st.session_state.carrinho = []

    # (Mantenha o restante das abas: Reposição, Clientes, Estoque e Configurações como no código anterior)
