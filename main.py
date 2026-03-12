import streamlit as st
from supabase import create_client
import pandas as pd
from fpdf import FPDF
from datetime import datetime, date

# Tenta importar o Plotly para os Dashboards
try:
    import plotly.express as px
    HAS_PLOTLY = True
except:
    HAS_PLOTLY = False

# 1. Conexão Segura
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

if 'carrinho' not in st.session_state: st.session_state.carrinho = []

# --- FUNÇÃO DE IMPRESSÃO ---
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
        pdf.cell(60, 6, f"Ajuste: R$ {ajuste:.2f}", 0, ln=1, align="R")
        
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
st.set_page_config(page_title="SGV Profissional", layout="wide")

if not st.session_state.get("autenticado"):
    st.title("🚀 SGV Profissional")
    if st.text_input("Senha", type="password") == "Naksu@6026" and st.button("Entrar"):
        st.session_state.autenticado = True; st.rerun()
else:
    menu = st.sidebar.radio("Navegação", ["📊 Dashboards", "🛒 PDV", "💰 Financeiro", "👥 Clientes", "📦 Estoque", "⚙️ Configurações"])

    # --- 📊 DASHBOARDS (BLINDADO) ---
    if menu == "📊 Dashboards":
        st.header("📊 Desempenho do Negócio")
        if HAS_PLOTLY:
            c1, c2, c3 = st.columns(3)
            c1.metric("Vendas Totais", "R$ 0,00")
            c2.metric("Clientes Ativos", "0")
            c3.metric("Itens em Estoque", "0")
            st.info("Gráficos aparecerão aqui assim que houver histórico de vendas.")
        else:
            st.error("Instale 'plotly' para ver os gráficos.")

    # --- 🛒 PDV ---
    elif menu == "🛒 PDV":
        st.header("🛒 Novo Pedido")
        try:
            clis_r = supabase.table("Clientes").select("nome_completo").execute().data or []
            pros_r = supabase.table("produtos").select("*").execute().data or []
            clis = [c['nome_completo'] for c in clis_r]
            pros = {p['descricao']: p for p in pros_r}
        except: clis, pros = [], {}

        cli_sel = st.selectbox("Cliente", [""] + clis)
        st.divider()
        cp, cq, cb = st.columns([3, 1, 1])
        p_sel = cp.selectbox("Produto", [""] + list(pros.keys()))
        q_val = cq.number_input("Qtd", min_value=0.1, value=1.0)
        if cb.button("➕ Adicionar"):
            if p_sel:
                p = pros[p_sel]
                st.session_state.carrinho.append({"descricao": p_sel, "quantidade": q_val, "unidade": p['unidade'], "preco_venda": p['preco_venda'], "total": q_val * p['preco_venda']})
                st.rerun()

        if st.session_state.carrinho:
            st.table(pd.DataFrame(st.session_state.carrinho))
            if st.button("🗑️ Limpar Carrinho"): st.session_state.carrinho = []; st.rerun()
            st.divider()
            f1, f2, f3, f4 = st.columns([2, 2, 1, 1])
            cond = f1.selectbox("Pagamento", ["À Vista", "À Prazo"])
            venc = f2.date_input("Vencimento") if cond == "À Prazo" else date.today()
            ajust = f3.number_input("Ajuste R$ (+/-)", value=0.0)
            vias_sel = f4.radio("Vias", [1, 2], index=1)
            obs_txt = st.text_input("Observações (Taxas, descontos, etc)")
            
            if st.button("✅ FINALIZAR"):
                # Busca numero do pedido e dados empresa
                try:
                    res_n = supabase.table("controle_pedidos").select("ultimo_numero").eq("id", 1).execute().data
                    n_ped = (res_n[0]['ultimo_numero'] + 1) if res_n else 1
                    supabase.table("controle_pedidos").upsert({"id":1, "ultimo_numero": n_ped}).execute()
                    res_e = supabase.table("config_empresa").select("*").eq("id", 1).execute().data
                    emp_i = res_e[0] if res_e else {}
                except: n_ped = 1; emp_i = {}
                
                pdf = gerar_recibo_pdf(emp_i, cli_sel, st.session_state.carrinho, cond, venc, n_ped, ajust, obs_txt, vias_sel)
                st.download_button("📄 Baixar Pedido", pdf, f"Pedido_{n_ped:04d}.pdf")
                st.session_state.carrinho = []

    # --- 👥 CLIENTES (CRUD TOTAL) ---
    elif menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        t1, t2 = st.tabs(["Lista e Exclusão", "Novo Cadastro"])
        with t2:
            with st.form("c_f"):
                n, d, e, t = st.text_input("Nome"), st.text_input("CPF/CNPJ"), st.text_input("Endereço"), st.text_input("Fone")
                if st.form_submit_button("Cadastrar"):
                    supabase.table("Clientes").insert({"nome_completo":n,"cpf_cnpj":d,"endereco":e,"telefone":t}).execute()
                    st.success("Salvo!"); st.rerun()
        with t1:
            res = supabase.table("Clientes").select("*").execute().data
            if res:
                df = pd.DataFrame(res)
                st.dataframe(df, use_container_width=True)
                sel = st.selectbox("Selecione para excluir", df['nome_completo'])
                if st.button("🗑️ Excluir Cliente"):
                    id_c = df[df['nome_completo'] == sel]['id'].values[0]
                    supabase.table("Clientes").delete().eq("id", id_c).execute()
                    st.rerun()
            else: st.info("Nenhum cliente cadastrado.")

    # --- 📦 ESTOQUE (CRUD TOTAL) ---
    elif menu == "📦 Estoque":
        st.header("📦 Gestão de Estoque")
        t1, t2 = st.tabs(["Lista de Produtos", "Cadastrar Novo"])
        with t2:
            with st.form("p_f"):
                desc, prc, und = st.text_input("Descrição"), st.number_input("Preço"), st.selectbox("Unid", ["KG", "UNI", "CX"])
                if st.form_submit_button("Cadastrar"):
                    supabase.table("produtos").insert({"descricao":desc,"preco_venda":prc,"unidade":und,"estoque_atual":0}).execute()
                    st.success("Produto salvo!"); st.rerun()
        with t1:
            res = supabase.table("produtos").select("*").execute().data
            if res:
                df = pd.DataFrame(res)
                st.dataframe(df, use_container_width=True)
                sel_p = st.selectbox("Selecione para excluir", df['descricao'])
                if st.button("🗑️ Excluir Produto"):
                    id_p = df[df['descricao'] == sel_p]['id'].values[0]
                    supabase.table("produtos").delete().eq("id", id_p).execute()
                    st.rerun()
            else: st.info("Nenhum produto em estoque.")

    # --- ⚙️ CONFIGURAÇÕES (LOGO E REINÍCIO) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Configurações do Sistema")
        try:
            res_e = supabase.table("config_empresa").select("*").eq("id", 1).execute().data
            emp_d = res_e[0] if res_e else {}
        except: emp_d = {}

        c1, c2 = st.columns(2)
        with c1:
            with st.form("cfg"):
                nome = st.text_input("Nome Empresa", value=emp_d.get('nome_empresa',''))
                ende = st.text_input("Endereço", value=emp_d.get('endereco',''))
                fone = st.text_input("Fone", value=emp_d.get('telefone',''))
                cnpj = st.text_input("CNPJ", value=emp_d.get('cnpj',''))
                if st.form_submit_button("Salvar Dados"):
                    supabase.table("config_empresa").upsert({"id":1, "nome_empresa":nome, "endereco":ende, "telefone":fone, "cnpj":cnpj}).execute()
                    st.rerun()
        with c2:
            st.subheader("🖼️ Logomarca")
            foto = st.file_uploader("Subir Logomarca (PNG/JPG)", type=['png','jpg'])
            if foto: st.image(foto, width=200)
            
            st.divider()
            st.subheader("🚨 Área de Perigo")
            if st.button("🔄 Zerar Contador de Pedidos"):
                supabase.table("controle_pedidos").update({"ultimo_numero": 0}).eq("id", 1).execute()
                st.warning("Próximo pedido será o 0001.")

    elif menu == "💰 Financeiro":
        st.header("💰 Financeiro")
        st.info("Funcionalidade em desenvolvimento para a versão 3.0 Pro.")
