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

# --- FUNÇÃO DE IMPRESSÃO (LAYOUT PEDIDO_1.PDF) ---
def gerar_recibo_pdf(empresa, cliente, itens, condicao, vencimento, n_pedido, ajuste=0.0, obs="", vias=2):
    pdf = FPDF(format='A4')
    total_prod = sum(item['total'] for item in itens)
    total_g = total_prod + ajuste
    
    def desenhar_via(y_offset):
        pdf.set_xy(10, y_offset + 10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(120, 6, empresa.get('nome_empresa', 'EMPRESA'), ln=0)
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
        
        # Rodapé
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
st.set_page_config(page_title="JMQJR - SGV", layout="wide")

if not st.session_state.get("autenticado"):
    st.title("JMQJR - SGV - Sales system")
    if st.text_input("Senha", type="password") == "Naksu@6026" and st.button("Entrar"):
        st.session_state.autenticado = True; st.rerun()
else:
    menu = st.sidebar.radio("Navegação", ["🛒 PDV", "📥 Reposição", "👥 Clientes", "📦 Estoque", "📊 Relatórios", "⚙️ Configurações"])

    # --- ABA RELATÓRIOS (CORRIGIDA) ---
    if menu == "📊 Relatórios":
        st.header("📊 Relatórios Gerenciais")
        try:
            res_p = supabase.table("produtos").select("descricao, unidade, preco_venda, estoque_atual").execute().data
            res_c = supabase.table("Clientes").select("nome_completo, cpf_cnpj").execute().data
            
            t1, t2 = st.tabs(["📦 Estoque e Preços", "👥 Lista de Clientes"])
            with t1:
                if res_p:
                    dfp = pd.DataFrame(res_p)
                    dfp.columns = ["Produto", "Unid", "Preço Venda", "Estoque"]
                    st.table(dfp) # Usando table para garantir que apareça
                else: st.warning("Nenhum produto cadastrado.")
            with t2:
                if res_c:
                    dfc = pd.DataFrame(res_c)
                    dfc.columns = ["Nome", "Documento"]
                    st.table(dfc)
                else: st.warning("Nenhum cliente cadastrado.")
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            if st.button("🔄 Tentar Novamente"): st.rerun()

    # --- ABA PDV ---
    elif menu == "🛒 PDV":
        st.header("🛒 Novo Pedido")
        # Busca segura de dados
        try:
            c_data = supabase.table("Clientes").select("nome_completo").execute().data
            p_data = supabase.table("produtos").select("*").execute().data
            clis = [c['nome_completo'] for c in c_data] if c_data else []
            pros = {p['descricao']: p for p in p_data} if p_data else {}
        except: clis, pros = [], {}

        cli_sel = st.selectbox("Cliente", [""] + clis)
        st.divider()
        c_p, c_q, c_b = st.columns([3, 1, 1])
        p_sel = c_p.selectbox("Produto", [""] + list(pros.keys()))
        q_val = c_q.number_input("Qtd", min_value=0.1)
        if c_b.button("➕"):
            if p_sel:
                p = pros[p_sel]
                st.session_state.carrinho.append({"descricao": p_sel, "quantidade": q_val, "unidade": p['unidade'], "preco_venda": p['preco_venda'], "total": q_val * p['preco_venda']})
                st.rerun()

        if st.session_state.carrinho:
            st.table(pd.DataFrame(st.session_state.carrinho))
            if st.button("🗑️ Limpar"): st.session_state.carrinho = []; st.rerun()
            st.divider()
            f1, f2, f3, f4 = st.columns([2, 2, 1, 1])
            cond = f1.selectbox("Pagamento", ["À Vista", "À Prazo"])
            venc = f2.date_input("Vencimento") if cond == "À Prazo" else date.today()
            ajust = f3.number_input("Ajuste (R$)", value=0.0)
            vias_sel = f4.radio("Vias", [1, 2], index=1)
            obs_txt = st.text_input("Obs.:")
            
            if st.button("✅ FINALIZAR"):
                try:
                    res_n = supabase.table("controle_pedidos").select("ultimo_numero").eq("id", 1).execute().data[0]
                    novo_n = res_n['ultimo_numero'] + 1
                    supabase.table("controle_pedidos").update({"ultimo_numero": novo_n}).eq("id", 1).execute()
                except: novo_n = 1
                try: emp = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
                except: emp = {}
                pdf_bytes = gerar_recibo_pdf(emp, cli_sel, st.session_state.carrinho, cond, venc, novo_n, ajust, obs_txt, vias_sel)
                st.download_button("📄 Baixar Pedido", pdf_bytes, f"Pedido_{novo_n:04d}.pdf", "application/pdf")
                st.session_state.carrinho = []

    # --- DEMAIS ABAS (CLIENTES, ESTOQUE, REPOSIÇÃO, CONFIG) ---
    elif menu == "👥 Clientes":
        st.header("👥 Clientes")
        with st.form("add_cli"):
            n, d = st.text_input("Nome"), st.text_input("Doc")
            if st.form_submit_button("Salvar"):
                supabase.table("Clientes").insert({"nome_completo": n, "cpf_cnpj": d}).execute()
                st.success("Salvo!"); st.rerun()
    elif menu == "📦 Estoque":
        st.header("📦 Produtos")
        with st.form("add_p"):
            d, p, u = st.text_input("Desc"), st.number_input("Preço"), st.selectbox("Un", ["KG", "UNI", "CX"])
            if st.form_submit_button("Salvar"):
                supabase.table("produtos").insert({"descricao": d, "preco_venda": p, "unidade": u, "estoque_atual": 0}).execute()
                st.success("Salvo!"); st.rerun()
    elif menu == "📥 Reposição":
        st.header("📥 Reposição")
        try:
            items = supabase.table("produtos").select("*").execute().data
            p_dict = {i['descricao']: i for i in items}
            with st.form("rep"):
                p_s = st.selectbox("Produto", list(p_dict.keys()))
                q_a = st.number_input("Qtd", min_value=0.1)
                if st.form_submit_button("Atualizar"):
                    n_q = p_dict[p_s]['estoque_atual'] + q_a
                    supabase.table("produtos").update({"estoque_atual": n_q}).eq("descricao", p_s).execute()
                    st.success("Ok!"); st.rerun()
        except: st.info("Sem produtos.")
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Configurações")
        try: d_e = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
        except: d_e = {"nome_empresa":"","endereco":"","telefone":"","cnpj":""}
        with st.form("c"):
            n = st.text_input("Empresa", value=d_e['nome_empresa'])
            e = st.text_input("Endereço", value=d_e['endereco'])
            t = st.text_input("Fone", value=d_e['telefone'])
            c = st.text_input("CNPJ", value=d_e['cnpj'])
            if st.form_submit_button("Salvar"):
                supabase.table("config_empresa").upsert({"id":1, "nome_empresa":n,"endereco":e,"telefone":t,"cnpj":c}).execute()
                st.success("Salvo!"); st.rerun()
