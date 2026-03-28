import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
from datetime import datetime

# --- 1. CONEXÃO E CONFIGURAÇÃO ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v88", layout="wide", page_icon="🎯")

# --- 2. MOTOR DE SEGURANÇA (BLOQUEIO INICIAL) ---
if 'auth' not in st.session_state: st.session_state.auth = False

def login_screen():
    _, col, _ = st.columns([1,1,1])
    with col:
        st.markdown("<h2 style='text-align: center;'>🔐 Acesso JMQJ SGV</h2>", unsafe_allow_html=True)
        senha = st.text_input("Senha Mestra", type="password")
        if st.button("LIGAR SISTEMA", use_container_width=True):
            if senha == "Naksu@6026": 
                st.session_state.auth = True
                st.rerun()
            else: st.error("Senha incorreta.")

if not st.session_state.auth:
    login_screen()
    st.stop()

# --- 3. MOTOR DE DADOS (FORÇADO E PERSISTENTE) ---
def carregar_universo_manual():
    try:
        e = supabase.table("config").select("*").eq("id", 1).execute().data
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        c = supabase.table("Clientes").select("*").order("NOM").execute().data
        return (e[0] if e else {}), pd.DataFrame(p), pd.DataFrame(c)
    except:
        return {}, pd.DataFrame(), pd.DataFrame()

emp, df_p, df_c = carregar_universo_manual()

# --- 4. INTERFACE E NAVEGAÇÃO ---
with st.sidebar:
    if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
    st.title(emp.get('nome', 'JMQJ SGV'))
    st.write(f"CNPJ: {emp.get('cnpj', '')}")
    st.write(f"Contatos: {emp.get('tel', '')} / {emp.get('email', '')}")
    st.write(f"Endereço: {emp.get('end', '')}, {emp.get('cidade', '')}/{emp.get('uf', '')}")
    st.write("---")
    menu = st.radio("MÓDULOS", ["📊 Painel", "🧾 Emissão de Pedido", "📦 Produtos & Estoque", "👥 Base de Clientes", "⚙️ Ajustes da Empresa"])

# --- MÓDULO: PAINEL ---
if menu == "📊 Painel":
    st.header("Painel Operacional")
    c1, c2, c3 = st.columns(3)
    c1.metric("CLIENTES CADASTRADOS", len(df_c))
    c2.metric("ITENS NO ESTOQUE", len(df_p))
    c3.metric("STATUS", "Online - Manual")

# --- MÓDULO: VENDAS (MOTOR DE IMPRESSÃO A5) ---
elif menu == "🧾 Emissão de Pedido":
    st.header("Novo Pedido de Venda")
    if df_p.empty or df_c.empty:
        st.warning("⚠️ Atenção: Cadastre Clientes e Produtos antes de emitir pedidos.")
    else:
        col1, col2 = st.columns([1, 1.4])
        with col1:
            with st.form("venda"):
                # Seletor de Cliente
                sel_cli = st.selectbox("Selecione o Cliente", df_c['NOM'].tolist())
                # Seletor de Produto
                prod_formatado = [f"{p['descricao']} | R$ {p['p_venda']:.2f}" for p in df_p.to_dict('records')]
                sel_prod = st.selectbox("Selecione o Produto", prod_formatado)
                
                qtd = st.number_input("Quantidade", min_value=1, value=1)
                desconto = st.number_input("Desconto (R$)", min_value=0.0, value=0.0, step=1.0)
                acrescimo = st.number_input("Acréscimo (R$)", min_value=0.0, value=0.0, step=1.0)
                
                if st.form_submit_button("📄 GERAR PRÉVIA DO PEDIDO"):
                    st.session_state.pedido_ok = True
                    st.session_state.cli_select = df_c[df_c['NOM'] == sel_cli].to_dict('records')[0]
                    st.session_state.prod_select = df_p[df_p['descricao'] == sel_prod.split(' | ')[0]].to_dict('records')[0]
                    st.session_state.qtd = qtd
                    st.session_state.desconto = desconto
                    st.session_state.acrescimo = acrescimo

        if st.session_state.get('pedido_ok'):
            with col2:
                # Recupera dados da sessão
                c = st.session_state.cli_select
                p = st.session_state.prod_select
                q = st.session_state.qtd
                desc = st.session_state.desconto
                acre = st.session_state.acrescimo
                total_itens = p['p_venda'] * q
                total_pedido = total_itens - desc + acre
                
                # Motor de Layout para Impressão (Figura solicitada)
                html_pedido = f"""
                <div style="border:1px solid #000; padding:30px; font-family:monospace; margin-bottom:10px; line-height: 1.3;">
                    <table style="width:100%"><tr>
                    <td style="width:30%"><img src="{emp.get('logo_base64', '')}" width="120"></td>
                    <td style="text-align:center"><b>{emp.get('nome', '')}</b><br>CNPJ: {emp.get('cnpj', '')}<br>{emp.get('end', '')}<br>{emp.get('cidade', '')}/{emp.get('uf', '')}<br>WhatsApp: {emp.get('tel', '')}</td>
                    <td style="text-align:right; border:1px solid #000; padding:5px">PEDIDO: {datetime.now().strftime('%M%S')}<br>{datetime.now().strftime('%d/%m/%Y')}</td>
                    </tr></table>
                    <hr>
                    <p><b>CLIENTE:</b> {c['NOM']}</p>
                    <p>Endereço: {c['RUA']}, {c['BAI']}, {c['CIDADE']}/{c['UF']} | Tel: {c['TEL']}</p>
                    <table style="width:100%; border-collapse: collapse; margin-top: 20px;">
                    <tr style="background-color: #f2f2f2;"><th>DESCRIÇÃO</th><th>QTD</th><th>UN</th><th>PREÇO</th><th>TOTAL</th></tr>
                    <tr><td>{p['descricao']}</td><td style="text-align:center">{q}</td><td style="text-align:center">{p.get('unidade','UN')}</td><td style="text-align:right">R$ {p['p_venda']:.2f}</td><td style="text-align:right">R$ {total_itens:.2f}</td></tr>
                    </table>
                    <hr style="margin-top: 30px;">
                    <table style="width:100%"><tr>
                    <td style="width:70%; text-align:right">Total de Itens:</td><td style="text-align:right">R$ {total_itens:.2f}</td>
                    </tr><tr>
                    <td style="text-align:right; color: red;">(-) Desconto:</td><td style="text-align:right; color: red;">R$ {desc:.2f}</td>
                    </tr><tr>
                    <td style="text-align:right; color: green;">(+) Acréscimo:</td><td style="text-align:right; color: green;">R$ {acre:.2f}</td>
                    </tr><tr style="font-size: 1.2rem; font-weight: bold;">
                    <td style="text-align:right">TOTAL DO PEDIDO:</td><td style="text-align:right">R$ {total_pedido:.2f}</td>
                    </tr></table>
                    <br><br><br>
                    <div style="text-align:center">_________________________________<br>Assinatura do Recebedor</div>
                </div>"""
                st.markdown(html_pedido, unsafe_allow_html=True)
                st.write("Dica: Use Ctrl+P para imprimir esta página em modo A5 (Meia A4).")

# --- MÓDULO: PRODUTOS (INCLUSÃO MANUAL) ---
elif menu == "📦 Produtos & Estoque":
    st.header("Gestão de Produtos")
    tab_list, tab_new = st.tabs(["📋 Lista de Produtos", "➕ Novo Cadastro Manual"])
    with tab_list:
        st.dataframe(df_p, use_container_width=True, hide_index=True)
    with tab_new:
        with st.form("p_manual", clear_on_submit=True):
            st.subheader("Cadastrar Produto")
            d = st.text_input("Descrição do Produto")
            c1, c2, c3 = st.columns(3)
            u = c1.text_input("Unidade (ex: UN, PC, KG)", value="UN")
            e = c2.number_input("Estoque Inicial", min_value=0, value=0)
            v = c3.number_input("Valor de Venda (R$)", min_value=0.0, value=0.0, step=1.0)
            if st.form_submit_button("💾 SALVAR NO BANCO"):
                supabase.table("produtos").insert({"descricao": d, "unidade": u, "estoque": e, "p_venda": v}).execute()
                st.success("Produto cravado com sucesso!"); st.rerun()

# --- MÓDULO: CLIENTES (INCLUSÃO MANUAL COMPLETA) ---
elif menu == "👥 Base de Clientes":
    st.header("Gestão de Clientes")
    tab_list, tab_new = st.tabs(["📋 Relação de Clientes", "➕ Novo Cadastro Manual"])
    with tab_list:
        st.dataframe(df_c, use_container_width=True, hide_index=True)
    with tab_new:
        with st.form("c_manual", clear_on_submit=True):
            st.subheader("Cadastrar Novo Cliente")
            c1, c2 = st.columns(2)
            n = c1.text_input("Nome Completo / Razão Social (NOM)")
            doc = c2.text_input("CPF / CNPJ")
            rua = st.text_input("Rua (Logradouro)")
            c1, c2, c3 = st.columns(3)
            b = c1.text_input("Bairro")
            cep = c2.text_input("CEP")
            cid = c3.text_input("Cidade", value="Caucaia")
            uf = c1.selectbox("UF", ["CE", "RN", "PB", "PE"], index=0)
            c2, c3 = st.columns(2)
            tel = c2.text_input("Telefone / WhatsApp")
            em = c3.text_input("E-mail")
            if st.form_submit_button("💾 SALVAR NO BANCO"):
                supabase.table("Clientes").insert({
                    "NOM": n, "CPF": doc, "RUA": rua, "BAI": b, "CEP": cep, 
                    "CIDADE": cid, "UF": uf, "TEL": tel, "EMAIL": em
                }).execute()
                st.success("Cliente fixado com sucesso!"); st.rerun()

# --- MÓDULO: AJUSTES DA EMPRESA (FIXAÇÃO DA DERLYANA) ---
elif menu == "⚙️ Ajustes da Empresa":
    st.header("Identidade da Agroindústria")
    with st.form("empresa"):
        st.subheader("Dados Cadastrais (Derlyana)")
        nome = st.text_input("Nome da Empresa", value=emp.get('nome',''))
        cnpj = st.text_input("CNPJ", value=emp.get('cnpj',''))
        logo = st.file_uploader("Logomarca (PNG)", type=["png"])
        st.subheader("Endereço e Contato")
        rua = st.text_input("Rua", value=emp.get('end',''))
        c1, c2, c3 = st.columns(3)
        b = c1.text_input("Bairro", value=emp.get('bai',''))
        cep = c2.text_input("CEP", value=emp.get('cep',''))
        cid = c3.text_input("Cidade", value=emp.get('cidade',''))
        uf = c1.selectbox("UF", ["CE", "RN", "PB", "PE"], index=0)
        c2, c3 = st.columns(2)
        tel = c2.text_input("Telefone / Whats App", value=emp.get('tel',''))
        em = c3.text_input("E-mail", value=emp.get('email',''))
        
        if st.form_submit_button("💾 FIXAR DADOS DA EMPRESA"):
            # Converte logo para base64 se houver upload
            l64 = emp.get('logo_base64', '')
            if logo:
                l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
            # Upsert cravado no id: 1
            payload = {
                "id": 1, "nome": nome, "cnpj": cnpj, "logo_base64": l64, "end": rua,
                "bai": b, "cep": cep, "cidade": cid, "uf": uf, "tel": tel, "email": em
            }
            supabase.table("config").upsert(payload).execute()
            st.success("Dados da empresa gravados com sucesso!"); st.rerun()
    
    st.divider()
    if st.button("🔥 RESET TOTAL DO SISTEMA (Cuidado!)"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        supabase.table("config").delete().eq("id", 1).execute()
        st.rerun()
