import streamlit as st
from supabase import create_client
import pandas as pd
import time
import base64
from datetime import datetime

# --- 1. CONEXÃO MESTRA ---
URL_SUPABASE = "https://jvsmiauvvdydxshnzrlr.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2c21pYXV2dmR5ZHhzaG56cmxyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI3NTMzNjAsImV4cCI6MjA4ODMyOTM2MH0.Cu_AqQWMO7ptoYgWEU7bpFNEnzPLq7vL8SNDHPIe_-o"
supabase = create_client(URL_SUPABASE, CHAVE_SUPABASE)

st.set_page_config(page_title="JMQJ SGV v38", layout="wide", page_icon="💼")

# --- 2. MOTOR DE SINCRONIA BLINDADA ---
def buscar_dados_vivos():
    try:
        # Busca forçada sem cache para Clientes, Produtos e Config
        conf = supabase.table("config").select("*").eq("id", 1).execute().data
        est = supabase.table("produtos").select("*").order("descricao").execute().data
        cli = supabase.table("Clientes").select("*").order("nome_completo").execute().data
        
        df_e = pd.DataFrame(est) if est else pd.DataFrame(columns=['id', 'descricao', 'ean13', 'preco_venda'])
        df_e['preco_venda'] = pd.to_numeric(df_e['preco_venda'], errors='coerce').fillna(0.0)
        
        df_c = pd.DataFrame(cli) if cli else pd.DataFrame(columns=['id', 'nome_completo', 'cpf_cnpj', 'endereco'])
        
        return (conf[0] if conf else {}), df_e, df_c
    except Exception as e:
        st.error(f"Erro Crítico: {e}")
        return {}, pd.DataFrame(), pd.DataFrame()

# --- 3. DESIGN E CSS (ESTILO IMPRESSÃO SISCOM) ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F9; }
    .paper {
        background: white; padding: 40px; border: 1px solid #ddd;
        font-family: 'Courier New', Courier, monospace; color: black;
    }
    .win-tile {
        background: white; padding: 20px; border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-top: 5px solid #0078D4;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FLUXO DE ACESSO ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align: center;'>JMQJ SGV SISTEMAS 💼</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        senha = st.text_input("Chave Mestra", type="password")
        if st.button("ATIVAR 🚀", use_container_width=True):
            if senha == "Naksu@6026":
                st.session_state.auth = True
                st.rerun()
else:
    # CARREGAMENTO EM TEMPO REAL (FIM DA OMISSÃO)
    emp, df_e, df_c = buscar_dados_vivos()

    with st.sidebar:
        if emp.get('logo_base64'):
            st.image(emp['logo_base64'], use_container_width=True)
        st.title(emp.get('nome', 'SGV'))
        st.caption(emp.get('end', ''))
        st.write("---")
        menu = st.radio("MÓDULOS", ["🏠 Dashboard", "🛒 Pedido de Venda", "📦 Estoque (Produtos)", "👥 Clientes", "📑 Importação", "⚙️ Ajustes"])

    # --- ABA: DASHBOARD ---
    if menu == "🏠 Dashboard":
        st.header(f"Painel Gerencial | {emp.get('nome', 'SGV')}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="win-tile">PRODUTOS<br><b style="font-size:25px">{len(df_e)}</b></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="win-tile">CLIENTES<br><b style="font-size:25px">{len(df_c)}</b></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="win-tile">PEDIDOS<br><b style="font-size:25px">0</b></div>', unsafe_allow_html=True)

    # --- ABA: PEDIDO DE VENDA (INSPIRED BY FPQ) ---
    elif menu == "🛒 Pedido de Venda":
        st.header("🛒 Novo Pedido de Venda")
        
        col_dados, col_print = st.columns([1, 1])
        
        with col_dados:
            with st.form("f_venda"):
                st.subheader("Dados da Transação")
                c_v = st.selectbox("Cliente", df_c['nome_completo'].tolist() if not df_c.empty else ["Consumidor"])
                p_v = st.selectbox("Produto", [f"{p['id']} - {p['descricao']} | R$ {p['preco_venda']}" for p in df_e.to_dict('records')] if not df_e.empty else ["Estoque Vazio"])
                qtd = st.number_input("Quantidade", min_value=1, value=1)
                vias = st.radio("Vias", ["1 Via", "2 Vias"], horizontal=True)
                # O botão de gerar agora simula a visualização do print que você mandou
                gerar = st.form_submit_button("🔥 GERAR PRÉVIA DO PEDIDO")

        if gerar:
            with col_print:
                st.subheader("Visualização da Impressão")
                st.markdown(f"""
                <div class="paper">
                    <table style="width:100%">
                        <tr>
                            <td style="width:20%"><img src="{emp.get('logo_base64', '')}" width="80"></td>
                            <td style="text-align:center">
                                <b>{emp.get('nome', 'EMPRESA')}</b><br>
                                {emp.get('end', 'ENDEREÇO')}<br>
                                CNPJ: {emp.get('cnpj', '00.000.000/0001-00')}
                            </td>
                            <td style="text-align:right; border:1px solid #000; padding:5px">
                                <b>PEDIDO Nº 001</b><br>
                                Data: {datetime.now().strftime('%d/%m/%Y')}<br>
                                <b>VIA: {vias}</b>
                            </td>
                        </tr>
                    </table>
                    <hr>
                    <p><b>CLIENTE:</b> {c_v}</p>
                    <table style="width:100%; border-collapse: collapse;">
                        <tr style="background:#eee">
                            <th style="border:1px solid #ddd">DESCRIÇÃO</th>
                            <th style="border:1px solid #ddd">QTD</th>
                            <th style="border:1px solid #ddd">VALOR</th>
                            <th style="border:1px solid #ddd">TOTAL</th>
                        </tr>
                        <tr>
                            <td style="border:1px solid #ddd">{p_v.split('|')[0]}</td>
                            <td style="border:1px solid #ddd; text-align:center">{qtd}</td>
                            <td style="border:1px solid #ddd; text-align:right">{p_v.split('R$')[1]}</td>
                            <td style="border:1px solid #ddd; text-align:right; font-weight:bold">R$ {float(p_v.split('R$')[1].replace(',','.')) * qtd:.2f}</td>
                        </tr>
                    </table>
                    <br><br><br>
                    <div style="text-align:center">________________________________<br>Assinatura do Recebedor</div>
                </div>
                """, unsafe_allow_html=True)
                st.button("🖨️ Enviar para Impressora")

    # --- ABA: ESTOQUE (PRODUTOS) ---
    elif menu == "📦 Estoque (Produtos)":
        st.header("📦 Gestão de Estoque")
        if not df_e.empty:
            st.dataframe(df_e, use_container_width=True, hide_index=True)
            sel = st.selectbox("Excluir Item", ["Selecione..."] + [f"{p['id']} - {p['descricao']}" for p in df_e.to_dict('records')])
            if sel != "Selecione..." and st.button("🗑️ DELETAR"):
                supabase.table("produtos").delete().eq("id", int(sel.split(" - ")[0])).execute()
                st.rerun()
        else: st.warning("Estoque Vazio. Use a Importação.")

    # --- ABA: IMPORTAÇÃO ---
    elif menu == "📑 Importação":
        st.header("📑 Carga Inteligente")
        alvo = st.selectbox("Destino", ["produtos", "Clientes"])
        arq = st.file_uploader("Excel", type=["xlsx"])
        if arq and st.button("🚀 IMPORTAR"):
            df_in = pd.read_excel(arq)
            for i, r in enumerate(df_in.to_dict('records')):
                try:
                    if alvo == "produtos":
                        p_val = str(r.get('P_VENDA', 0)).replace('R$', '').replace('.','').replace(',','.').strip()
                        pld = {"descricao": str(r.get('DESCRICAO')), "preco_venda": float(p_val), "ean13": str(r.get('CODIGO'))}
                    else:
                        pld = {"nome_completo": str(r.get('NOM')), "cpf_cnpj": str(r.get('CGC')), "endereco": str(r.get('RUA'))}
                    supabase.table(alvo).insert(pld).execute()
                except: pass
            st.success("Carga realizada!"); time.sleep(1); st.rerun()

    # --- ABA: AJUSTES E RESETS ---
    elif menu == "⚙️ Ajustes":
        st.header("⚙️ Configurações e Resets")
        with st.form("f_adj"):
            n = st.text_input("Nome Fantasia", value=emp.get('nome', ''))
            e = st.text_input("Endereço", value=emp.get('end', ''))
            logo = st.file_uploader("Logo (PNG)", type=["png"])
            if st.form_submit_button("💾 SALVAR"):
                l_b64 = emp.get('logo_base64', '')
                if logo: l_b64 = f"data:image/png;base64,{base64.b64encode(logo.read()).decode('utf-8')}"
                supabase.table("config").upsert({"id": 1, "nome": n, "end": e, "logo_base64": l_b64}).execute()
                st.rerun()
        
        st.divider()
        st.subheader("🛑 ZONA DE RESET TOTAL")
        c1, c2, c3 = st.columns(3)
        if c1.button("🗑️ ZERAR ESTOQUE"): supabase.table("produtos").delete().neq("id", -1).execute(); st.rerun()
        if c2.button("👥 ZERAR CLIENTES"): supabase.table("Clientes").delete().neq("id", -1).execute(); st.rerun()
        if c3.button("🔥 ZERAR TUDO"):
            supabase.table("produtos").delete().neq("id", -1).execute()
            supabase.table("Clientes").delete().neq("id", -1).execute()
            supabase.table("config").delete().eq("id", 1).execute()
            st.rerun()
