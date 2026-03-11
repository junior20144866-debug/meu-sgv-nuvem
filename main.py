import streamlit as st
from supabase import create_client
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# Tenta importar o Plotly, se falhar (por falta do requirements), o app não quebra
try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# 1. Conexão Segura
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

if 'carrinho' not in st.session_state: st.session_state.carrinho = []

# --- FUNÇÃO DE IMPRESSÃO (ESTILO PEDIDO_1.PDF) ---
def gerar_recibo_pdf(empresa, cliente, itens, condicao, vencimento, n_pedido, ajuste=0.0, obs="", vias=2):
    pdf = FPDF(format='A4')
    total_prod = sum(item['total'] for item in itens)
    total_g = total_prod + ajuste
    
    def desenhar_via(y_offset):
        pdf.set_xy(10, y_offset + 10)
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

# --- INTERFACE PRINCIPAL ---
st.set_page_config(page_title="JMQJR - Sistema Profissional", layout="wide")

if not st.session_state.get("autenticado"):
    st.title("🚀 SGV Profissional")
    pwd = st.text_input("Senha", type="password")
    if st.button("Entrar") and pwd == "Naksu@6026":
        st.session_state.autenticado = True; st.rerun()
else:
    menu = st.sidebar.radio("Navegação", ["📊 Dashboards", "🛒 PDV", "💰 Financeiro", "📥 Reposição", "👥 Clientes", "📦 Estoque", "⚙️ Configurações"])

    # --- DASHBOARDS ---
    if menu == "📊 Dashboards":
        st.header("📊 Painel de Vendas")
        if HAS_PLOTLY:
            c1, c2, c3 = st.columns(3)
            # Valores estáticos por enquanto, em breve puxaremos do histórico de pedidos
            c1.metric("Vendas Hoje", "R$ 0,00")
            c2.metric("Recebimentos Pendentes", "R$ 0,00")
            c3.metric("Lucro Estimado", "R$ 0,00")
            
            df_demo = pd.DataFrame({"Data": ["01/03", "02/03", "03/03"], "Vendas": [100, 250, 180]})
            fig = px.bar(df_demo, x="Data", y="Vendas", title="Vendas por Período")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Adicione 'plotly' ao seu requirements.txt para ver os gráficos.")

    # --- FINANCEIRO ---
    elif menu == "💰 Financeiro":
        st.header("💰 Gestão Financeira")
        t1, t2 = st.tabs(["📈 Contas a Receber (Clientes)", "📉 Contas a Pagar (Despesas)"])
        with t1:
            st.subheader("Pendências de Vendas À Prazo")
            st.info("Aqui serão listadas as parcelas de clientes que ainda não pagaram.")
        with t2:
            st.subheader("Controle de Despesas")
            with st.form("despesa"):
                d = st.text_input("Descrição da Despesa")
                v = st.number_input("Valor", min_value=0.0)
                dt = st.date_input("Vencimento")
                if st.form_submit_button("Lançar"):
                    st.success("Lançado com sucesso!")

    # --- PDV ---
    elif menu == "🛒 PDV":
        st.header("🛒 Novo Pedido")
        # Busca segura (Evita erro se tabelas estiverem vazias)
        try:
            clis_data = supabase.table("Clientes").select("nome_completo").execute().data or []
            clis = [c['nome_completo'] for c in clis_data]
            pros_data = supabase.table("produtos").select("*").execute().data or []
            pros = {p['descricao']: p for p in pros_data}
        except Exception as e:
            st.error(f"Erro ao conectar com o banco: {e}")
            clis, pros = [], {}

        cli_sel = st.selectbox("Selecione o Cliente", [""] + clis)
        st.divider()
        cp, cq, cb = st.columns([3, 1, 1])
        p_sel = cp.selectbox("Produto", [""] + list(pros.keys()))
        q_val = cq.number_input("Qtd", min_value=0.1)
        if cb.button("➕ Adicionar"):
            if p_sel:
                p = pros[p_sel]
                st.session_state.carrinho.append({"descricao": p_sel, "quantidade": q_val, "unidade": p['unidade'], "preco_venda": p['preco_venda'], "total": q_val * p['preco_venda']})
                st.rerun()

        if st.session_state.carrinho:
            st.table(pd.DataFrame(st.session_state.carrinho))
            f1, f2, f3, f4 = st.columns([2, 2, 1, 1])
            cond = f1.selectbox("Pagamento", ["À Vista", "À Prazo"])
            venc = f2.date_input("Vencimento") if cond == "À Prazo" else date.today()
            ajust = f3.number_input("Ajuste (R$)", value=0.0)
            vias = f4.radio("Vias", [1, 2], index=1)
            obs = st.text_input("Observações")
            
            if st.button("✅ FINALIZAR"):
                # Busca Numero Pedido e Dados Empresa
                try:
                    res_n = supabase.table("controle_pedidos").select("ultimo_numero").eq("id", 1).execute().data[0]
                    novo_n = res_n['ultimo_numero'] + 1
                    supabase.table("controle_pedidos").update({"ultimo_numero": novo_n}).eq("id", 1).execute()
                    res_emp = supabase.table("config_empresa").select("*").eq("id", 1).execute().data
                    emp_info = res_emp[0] if res_emp else {}
                except: novo_n = 1; emp_info = {}
                
                pdf_out = gerar_recibo_pdf(emp_info, cli_sel, st.session_state.carrinho, cond, venc, novo_n, ajust, obs, vias)
                st.download_button("📄 Imprimir Pedido", pdf_out, f"Pedido_{novo_n:04d}.pdf")
                st.session_state.carrinho = []

    # --- CONFIGURAÇÕES ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Configurações da Empresa")
        try:
            res_emp = supabase.table("config_empresa").select("*").eq("id", 1).execute().data
            emp_data = res_emp[0] if res_emp else {}
        except: emp_data = {}

        with st.form("cfg"):
            n = st.text_input("Nome Empresa", value=emp_data.get('nome_empresa', ''))
            e = st.text_input("Endereço", value=emp_data.get('endereco', ''))
            t = st.text_input("Telefone", value=emp_data.get('telefone', ''))
            c = st.text_input("CNPJ", value=emp_data.get('cnpj', ''))
            if st.form_submit_button("Salvar"):
                supabase.table("config_empresa").upsert({"id": 1, "nome_empresa": n, "endereco": e, "telefone": t, "cnpj": c}).execute()
                st.success("Salvo!"); st.rerun()

    # --- OUTRAS ABAS ---
    elif menu == "👥 Clientes":
        st.header("👥 Clientes")
        with st.form("add_cli"):
            nc, dc, ec, tc = st.text_input("Nome"), st.text_input("Doc"), st.text_input("Endereço"), st.text_input("Fone")
            if st.form_submit_button("Cadastrar"):
                supabase.table("Clientes").insert({"nome_completo":nc, "cpf_cnpj":dc, "endereco":ec, "telefone":tc}).execute()
                st.rerun()
    elif menu == "📦 Estoque":
        st.header("📦 Estoque")
        res_p = supabase.table("produtos").select("*").execute().data or []
        st.dataframe(pd.DataFrame(res_p), use_container_width=True)
