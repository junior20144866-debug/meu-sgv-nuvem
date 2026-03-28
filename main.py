import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
from datetime import datetime

# --- 1. CONEXÃO DIRETA (SEM FILTROS) ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ Sistemas", layout="wide", page_icon="🎯")

# --- 2. SEGURANÇA (ACESSO MESTRE) ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.markdown("<h2 style='text-align: center;'>🔐 JMQJ Sistemas</h2>", unsafe_allow_html=True)
        senha = st.text_input("Senha de Operação", type="password")
        if st.button("LIGAR SISTEMA", use_container_width=True):
            if senha == "Naksu@6026": 
                st.session_state.auth = True
                st.rerun()
            else: st.error("Acesso negado.")
    st.stop()

# --- 3. CARREGAMENTO DE DADOS (RAIO-X) ---
def buscar_dados():
    try:
        e = supabase.table("config").select("*").eq("id", 1).execute().data
        p = supabase.table("produtos").select("*").order("descricao").execute().data
        c = supabase.table("Clientes").select("*").order("NOM").execute().data
        return (e[0] if e else {}), pd.DataFrame(p), pd.DataFrame(c)
    except Exception as err:
        st.error(f"Erro de leitura no banco: {err}")
        return {}, pd.DataFrame(), pd.DataFrame()

emp, df_p, df_c = buscar_dados()

# --- 4. INTERFACE ---
with st.sidebar:
    if emp.get('logo_base64'): st.image(emp['logo_base64'], use_container_width=True)
    st.title("JMQJ Sistemas")
    st.write(f"Empresa: {emp.get('nome', 'Não configurada')}")
    st.write("---")
    menu = st.radio("MÓDULOS", ["📊 Dashboard", "🧾 Vendas", "📦 Produtos", "👥 Clientes", "⚙️ Ajustes"])

# --- MODULO CLIENTES (FOCO NA INSERÇÃO MANUAL) ---
if menu == "👥 Clientes":
    st.header("👥 Cadastro de Clientes")
    with st.form("form_cli", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome/Razão Social (Obrigatório)")
        doc = c2.text_input("CPF/CNPJ")
        rua = st.text_input("Endereço (Rua)")
        c3, c4, c5 = st.columns([2, 2, 1])
        bairro = c3.text_input("Bairro")
        cidade = c4.text_input("Cidade")
        uf = c5.text_input("UF", max_chars=2)
        c6, c7 = st.columns(2)
        tel = c6.text_input("Telefone/WhatsApp")
        email = c7.text_input("E-mail")
        
        if st.form_submit_button("💾 SALVAR CLIENTE"):
            if not nome:
                st.error("O campo Nome é obrigatório.")
            else:
                try:
                    payload = {
                        "NOM": nome, "CPF": doc, "RUA": rua, "BAI": bairro,
                        "CIDADE": cidade, "UF": uf, "TEL": tel, "EMAIL": email
                    }
                    supabase.table("Clientes").insert(payload).execute()
                    st.success("✅ Cliente gravado com sucesso!")
                    time.sleep(1); st.rerun()
                except Exception as e:
                    st.error(f"❌ O banco de dados rejeitou a gravação: {e}")

# --- MODULO PRODUTOS ---
elif menu == "📦 Produtos":
    st.header("📦 Cadastro de Produtos")
    with st.form("form_prod", clear_on_submit=True):
        desc = st.text_input("Descrição do Item")
        c1, c2, c3 = st.columns(3)
        uni = c1.text_input("Unidade (UN, KG, PC)")
        est = c2.number_input("Estoque", value=0)
        prc = c3.number_input("Preço de Venda (R$)", value=0.0, step=0.1)
        
        if st.form_submit_button("💾 SALVAR PRODUTO"):
            try:
                supabase.table("produtos").insert({
                    "descricao": desc, "unidade": uni, "estoque": est, "p_venda": prc
                }).execute()
                st.success("✅ Produto gravado!")
                time.sleep(1); st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao gravar: {e}")

# --- MODULO VENDAS (IMPRESSÃO A5) ---
elif menu == "🧾 Vendas":
    st.header("🧾 Emissão de Pedido")
    if df_c.empty or df_p.empty:
        st.warning("Cadastre clientes e produtos primeiro.")
    else:
        with st.form("venda"):
            cli = st.selectbox("Selecione o Cliente", df_c['NOM'].tolist())
            prod = st.selectbox("Selecione o Produto", df_p['descricao'].tolist())
            qtd = st.number_input("Qtd", min_value=1)
            desc_v = st.number_input("Desconto (R$)", value=0.0)
            acre_v = st.number_input("Acréscimo (R$)", value=0.0)
            if st.form_submit_button("GERAR PEDIDO"):
                st.session_state.v_ready = True
                st.session_state.v_cli = df_c[df_c['NOM'] == cli].iloc[0]
                st.session_state.v_pro = df_p[df_p['descricao'] == prod].iloc[0]
                st.session_state.v_vals = {'q': qtd, 'd': desc_v, 'a': acre_v}

        if st.session_state.get('v_ready'):
            c, p, v = st.session_state.v_cli, st.session_state.v_pro, st.session_state.v_vals
            sub = p['p_venda'] * v['q']
            total = sub - v['d'] + v['a']
            
            # Layout Neutro JMQJ
            st.markdown(f"""
            <div style="border: 2px solid #000; padding: 20px; font-family: monospace; background: white; color: black;">
                <h2 style='text-align:center;'>JMQJ Sistemas - Pedido</h2>
                <hr>
                <p><b>EMPRESA:</b> {emp.get('nome', 'JMQJ')}</p>
                <p><b>CLIENTE:</b> {c['NOM']} | End: {c.get('RUA', '')}</p>
                <hr>
                <p>{p['descricao']} | {v['q']} {p.get('unidade')} x {p['p_venda']} = R$ {sub:.2f}</p>
                <p style="text-align:right">DESC: R$ {v['d']:.2f} | ACRE: R$ {v['a']:.2f}</p>
                <h3 style="text-align:right">TOTAL: R$ {total:.2f}</h3>
            </div>
            """, unsafe_allow_html=True)

# --- MODULO AJUSTES ---
elif menu == "⚙️ Ajustes":
    st.header("⚙️ Configurações do Sistema")
    with st.form("ajustes"):
        n = st.text_input("Nome da sua Empresa", value=emp.get('nome',''))
        cn = st.text_input("CNPJ", value=emp.get('cnpj',''))
        tel = st.text_input("Telefone", value=emp.get('tel',''))
        logo = st.file_uploader("Sua Logo (PNG)", type=["png"])
        if st.form_submit_button("💾 FIXAR CONFIGURAÇÃO"):
            l64 = emp.get('logo_base64', '')
            if logo: l64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
            supabase.table("config").upsert({
                "id": 1, "nome": n, "cnpj": cn, "tel": tel, "logo_base64": l64
            }).execute()
            st.success("Configuração salva!")
            st.rerun()
    
    st.divider()
    if st.button("🔥 ZERAR TUDO (RESET TOTAL)"):
        supabase.table("produtos").delete().neq("id", -1).execute()
        supabase.table("Clientes").delete().neq("id", -1).execute()
        st.rerun()

elif menu == "📊 Dashboard":
    st.header("Resumo Operacional")
    c1, c2 = st.columns(2)
    c1.metric("Clientes", len(df_c))
    c2.metric("Produtos", len(df_p))
