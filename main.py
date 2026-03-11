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

# --- FUNÇÃO DE IMPRESSÃO (ESTILO PEDIDO_1.PDF) ---
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
        
        pdf.ln(2)
        txt_pgto = "À Vista" if condicao == "À Vista" else f"À Prazo - Venc: {vencimento.strftime('%d/%m/%Y')}"
        pdf.set_font("Arial", "B", 10)
        pdf.cell(130, 6, f"Pagamento: {txt_pgto}", 0)
        pdf.cell(60, 6, f"Total Produtos: R$ {total_produtos:.2f}", 0, ln=1, align="R")
        
        pdf.set_font("Arial", "", 9)
        pdf.cell(130, 6, f"Obs.: {obs}", 0)
        pdf.cell(60, 6, f"R$ {ajuste_financeiro:.2f}", 0, ln=1, align="R")
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 8, f"VALOR TOTAL: R$ {total_geral:.2f}", 0, ln=1, align="R")
        
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

# --- INTERFACE PRINCIPAL ---
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

    # --- ABA CLIENTES (RESTAURADA) ---
    if menu == "👥 Clientes":
        st.header("👥 Gestão de Clientes")
        t1, t2 = st.tabs(["Lista", "Novo Cadastro"])
        with t2:
            with st.form("c_f"):
                n = st.text_input("Nome")
                d = st.text_input("CPF/CNPJ")
                if st.form_submit_button("Salvar"):
                    supabase.table("Clientes").insert({"nome_completo": n, "cpf_cnpj": d}).execute()
                    st.success("Salvo!"); st.rerun()
        with t1:
            res = supabase.table("Clientes").select("*").execute().data
            if res:
                df = pd.DataFrame(res)
                st.dataframe(df, use_container_width=True)
                sel = st.selectbox("Selecione para excluir", df['nome_completo'])
                if st.button("🗑️ Excluir"):
                    id_c = df[df['nome_completo'] == sel]['id'].values[0]
                    supabase.table("Clientes").delete().eq("id", id_c).execute()
                    st.rerun()
            else: st.info("Sem dados.")

    # --- ABA ESTOQUE (RESTAURADA) ---
    elif menu == "📦 Estoque":
        st.header("📦 Estoque de Produtos")
        t1, t2 = st.tabs(["Lista", "Novo Produto"])
        with t2:
            with st.form("p_f"):
                desc = st.text_input("Descrição")
                prc = st.number_input("Preço", min_value=0.0)
                und = st.selectbox("Unid", ["KG", "UNI", "CX", "PC"])
                if st.form_submit_button("Cadastrar"):
                    supabase.table("produtos").insert({"descricao": desc, "preco_venda": prc, "unidade": und, "estoque_atual": 0}).execute()
                    st.success("Cadastrado!"); st.rerun()
        with t1:
            res = supabase.table("produtos").select("*").execute().data
            if res:
                df = pd.DataFrame(res)
                st.dataframe(df, use_container_width=True)
                sel = st.selectbox("Excluir Produto", df['descricao'])
                if st.button("🗑️ Excluir"):
                    id_p = df[df['descricao'] == sel]['id'].values[0]
                    supabase.table("produtos").delete().eq("id", id_p).execute()
                    st.rerun()
            else: st.info("Sem produtos.")

    # --- ABA REPOSIÇÃO (RESTAURADA) ---
    elif menu == "📥 Reposição":
        st.header("📥 Entrada de Mercadoria")
        res = supabase.table("produtos").select("*").execute().data
        if res:
            p_dict = {p['descricao']: p for p in res}
            with st.form("repo"):
                p_sel = st.selectbox("Produto", list(p_dict.keys()))
                qtd_add = st.number_input("Qtd Entrada", min_value=0.1)
                if st.form_submit_button("Confirmar"):
                    nova_qtd = p_dict[p_sel]['estoque_atual'] + qtd_add
                    supabase.table("produtos").update({"estoque_atual": nova_qtd}).eq("descricao", p_sel).execute()
                    st.success("Estoque Atualizado!"); st.rerun()
        else: st.info("Cadastre produtos antes.")

    # --- ABA PDV (COM OPÇÃO DE VIAS RESTAURADA) ---
    elif menu == "🛒 PDV":
        st.header("🛒 Novo Pedido")
        clis = [c['nome_completo'] for c in supabase.table("Clientes").select("nome_completo").execute().data]
        pros = {p['descricao']: p for p in supabase.table("produtos").select("*").execute().data}
        
        cli_v = st.selectbox("Selecione o Cliente", [""] + clis)
        st.divider()
        cp, cq, cb = st.columns([3, 1, 1])
        p_sel = cp.selectbox("Produto", [""] + list(pros.keys()))
        q_sel = cq.number_input("Qtd", min_value=0.1)
        if cb.button("➕"):
            if p_sel:
                p = pros[p_sel]
                st.session_state.carrinho.append({"descricao": p_sel, "quantidade": q_sel, "unidade": p['unidade'], "preco_venda": p['preco_venda'], "total": q_sel * p['preco_venda']})
                st.rerun()

        if st.session_state.carrinho:
            st.table(pd.DataFrame(st.session_state.carrinho))
            if st.button("🗑️ Limpar"): st.session_state.carrinho = []; st.rerun()
            st.divider()
            f1, f2, f3, f4 = st.columns([2, 2, 2, 1]) # Adicionada coluna para vias
            cond_v = f1.selectbox("Pagamento", ["À Vista", "À Prazo"])
            venc_v = f2.date_input("Vencimento") if cond_v == "À Prazo" else date.today()
            ajuste_v = f3.number_input("Taxa/Desconto (R$)", value=0.0)
            vias_v = f4.radio("Vias", [1, 2], index=1) # OPÇÃO RESTAURADA
            obs_v = st.text_input("Obs.:")
            
            if st.button("✅ FINALIZAR"):
                try:
                    res_n = supabase.table("controle_pedidos").select("ultimo_numero").eq("id", 1).execute().data[0]
                    novo_n = res_n['ultimo_numero'] + 1
                    supabase.table("controle_pedidos").update({"ultimo_numero": novo_n}).eq("id", 1).execute()
                except: novo_n = 1
                try: emp = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
                except: emp = {}
                pdf = gerar_recibo_pdf(emp, cli_v, st.session_state.carrinho, cond_v, venc_v, novo_n, ajuste_v, obs_v, vias_v)
                st.download_button("📄 Baixar PDF", pdf, f"Pedido_{novo_n:04d}.pdf", "application/pdf")
                st.session_state.carrinho = []

    # --- ABA CONFIGURAÇÕES (RESTAURADA) ---
    elif menu == "⚙️ Configurações":
        st.header("⚙️ Minha Empresa")
        try: emp_d = supabase.table("config_empresa").select("*").eq("id", 1).execute().data[0]
        except: emp_d = {"nome_empresa":"","endereco":"","telefone":"","cnpj":""}
        with st.form("conf"):
            n = st.text_input("Nome", value=emp_d['nome_empresa'])
            e = st.text_input("Endereço", value=emp_d['endereco'])
            t = st.text_input("Fone", value=emp_d['telefone'])
            c = st.text_input("CNPJ", value=emp_d['cnpj'])
            if st.form_submit_button("Salvar"):
                supabase.table("config_empresa").upsert({"id":1, "nome_empresa":n, "endereco":e, "telefone":t, "cnpj":c}).execute()
                st.success("Salvo!"); st.rerun()
        st.divider()
        if st.button("🛑 REINICIAR CONTADOR DE PEDIDOS PARA 01"):
            supabase.table("controle_pedidos").update({"ultimo_numero": 0}).eq("id", 1).execute()
            st.warning("Próximo pedido será o 0001.")
