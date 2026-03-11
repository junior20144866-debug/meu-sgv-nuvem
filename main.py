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

# --- FUNÇÃO DE IMPRESSÃO REFORMULADA ---
def gerar_recibo_pdf(empresa, cliente, itens, condicao, vencimento, n_pedido, taxa=0.0, desc_taxa="", vias=2):
    pdf = FPDF(format='A4')
    total_produtos = sum(item['total'] for item in itens)
    total_geral = total_produtos + taxa
    
    def desenhar_via(y_offset):
        # Cabeçalho
        pdf.set_xy(10, y_offset + 10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(120, 6, empresa.get('nome_empresa', 'Sua Empresa'), ln=0)
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
        
        pdf.set_font("Arial", "I", 9)
        obs_texto = f"Obs/Taxa: {desc_taxa}" if desc_taxa else "Observações:"
        pdf.cell(130, 6, obs_texto, 0)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 6, f"(+) Taxas: R$ {taxa:.2f}", 0, ln=1, align="R")
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, f"VALOR TOTAL: R$ {total_geral:.2f}", 0, ln=1, align="R")
        
        # Assinaturas
        pdf.ln(12)
        pdf.cell(90, 0, "", border="T")
        pdf.cell(10, 0, "")
        pdf.cell(90, 0, "", border="T", ln=1)
        pdf.set_font("Arial", "", 8)
        pdf.cell(90, 5, "Visto da Empresa", 0, 0, "C")
        pdf.cell(10, 5, "")
        pdf.cell(90, 5, "Visto do Cliente", 0, 1, "C")

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
    if st.text_input("Senha", type="password") == "Naksu@6026" and st.button("Entrar"):
        st.session_state.autenticado = True
        st.rerun()
else:
    menu = st.sidebar.radio("Navegação", ["🛒 PDV", "📥 Reposição", "👥 Clientes", "📦 Estoque", "📊 Relatórios", "⚙️ Configurações"])

    # --- ABA CLIENTES ---
    if menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        t1, t2 = st.tabs(["Lista", "Novo"])
        with t2:
            with st.form("c_f"):
                n = st.text_input("Nome")
                d = st.text_input("CPF/CNPJ")
                if st.form_submit_button("Salvar"):
                    supabase.table("Clientes").insert({"nome_completo": n, "cpf_cnpj": d}).execute()
                    st.rerun()
        with t1:
            data = supabase.table("Clientes").select("*").execute().data
            if data:
                df = pd.DataFrame(data)
                sel = st.selectbox("Editar Cliente", df['nome_completo'])
                st.dataframe(df)
            else: st.info("Nenhum cliente.")

    # --- ABA ESTOQUE ---
    elif menu == "📦 Estoque":
        st.header("📦 Estoque")
        t1, t2 = st.tabs(["Lista/Editar", "Novo Produto"])
        with t2:
            with st.form("p_f"):
                desc = st.text_input("Descrição")
                prc = st.number_input("Preço", min_value=0.0)
                und = st.selectbox("Unidade", ["KG", "UNI", "CX"])
                if st.form_submit_button("Cadastrar"):
                    supabase.table("produtos").insert({"descricao": desc, "preco_venda": prc, "unidade": und, "estoque_atual": 0}).execute()
                    st.rerun()
        with t1:
            data = supabase.table("produtos").select("*").execute().data
            if data: st.dataframe(pd.DataFrame(data))
            else: st.info("Sem produtos.")

    # --- ABA PDV ---
    elif menu == "🛒 PDV":
        st.header("🛒 Novo Pedido")
        # Dados para o PDV
        clientes = [c['nome_completo'] for c in supabase.table("Clientes").select("nome_completo").execute().data]
        prods = {p['descricao']: p for p in supabase.table("produtos").select("*").execute().data}
        
        c1, c2, c3 = st.columns([3, 1, 1])
        cliente_v = c1.selectbox("Selecione o Cliente", [""] + clientes)
        
        st.divider()
        col_p, col_q, col_b = st.columns([3, 1, 1])
        p_sel = col_p.selectbox("Produto", [""] + list(prods.keys()))
        qtd_v = col_q.number_input("Qtd", min_value=0.1, step=0.1)
        if col_b.button("➕ Adicionar"):
            if p_sel:
                p = prods[p_sel]
                st.session_state.carrinho.append({"descricao": p_sel, "quantidade": qtd_v, "unidade": p['unidade'], "preco_venda": p['preco_venda'], "total": qtd_v * p['preco_venda']})
                st.rerun()

        if st.session_state.carrinho:
            st.table(pd.DataFrame(st.session_state.carrinho))
            if st.button("🗑️ Limpar Carrinho"):
                st.session_state.carrinho = []
                st.rerun()
            
            st.divider()
            col_f1, col_f2, col_f3 = st.columns(3)
            cond_v = col_f1.selectbox("Pagamento", ["À Vista", "À Prazo"])
            venc_v = col_f2.date_input("Vencimento") if cond_v == "À Prazo" else date.today()
            tax_v = col_f3.number_input("Taxa/Entrega (R$)", min_value=0.0)
            obs_v = st.text_input("Descrição da Taxa / Observação")
            
            if st.button("✅ FINALIZAR PEDIDO"):
                # Lógica do número do pedido
                try:
                    res_n = supabase.table("controle_pedidos").select("ultimo_numero").eq("id", 1).execute().data[0]
                    novo_n = res_n['ultimo_numero'] + 1
                    supabase.table("controle_pedidos").update({"ultimo_numero": novo_n}).eq("id", 1).execute()
                except: novo_n = 1
                
                emp = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
                pdf = gerar_recibo_pdf(emp, cliente_v, st.session_state.carrinho, cond_v, venc_v, novo_n, tax_v, obs_v)
                st.download_button("📄 Baixar Pedido", pdf, f"Pedido_{novo_n}.pdf", "application/pdf")

    # --- ABA CONFIGURAÇÕES ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Minha Empresa")
        try:
            dados = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
        except:
            dados = {"nome_empresa": "", "endereco": "", "telefone": "", "cnpj": "", "email": ""}
        
        with st.form("f_emp"):
            nome_e = st.text_input("Nome da Empresa", value=dados['nome_empresa'])
            end_e = st.text_input("Endereço", value=dados['endereco'])
            tel_e = st.text_input("Telefone", value=dados['telefone'])
            cnpj_e = st.text_input("CNPJ", value=dados['cnpj'])
            if st.form_submit_button("Salvar Configurações"):
                supabase.table("config_empresa").upsert({"id": 1, "nome_empresa": nome_e, "endereco": end_e, "telefone": tel_e, "cnpj": cnpj_e}).execute()
                st.success("Salvo!")
