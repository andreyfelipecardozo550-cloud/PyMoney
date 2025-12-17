import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Configuração da Página ---
st.set_page_config(page_title="Finanças Pessoais", page_icon="💰", layout="wide")

# --- Conexão com Google Sheets ---
def conectar_google_sheets():
    # Conecta usando a senha que guardamos nos Secrets do Streamlit
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # Abre a planilha pelo nome EXATO
    # IMPORTANTE: Sua planilha no Google TEM que se chamar "Controle Financeiro"
    return client.open("Controle Financeiro").sheet1

# --- Função para Carregar Dados ---
def carregar_dados():
    try:
        sheet = conectar_google_sheets()
        dados = sheet.get_all_records()
        df = pd.DataFrame(dados)
        return df
    except Exception as e:
        return pd.DataFrame()

# --- Função para Salvar ---
def salvar_no_google(nova_linha):
    try:
        sheet = conectar_google_sheets()
        sheet.append_row(nova_linha)
        st.toast("✅ Salvo no Google Sheets!", icon="🎉")
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")

# --- Interface Principal ---
st.title("💰 Controle Financeiro")

# Sidebar (Menu Lateral)
menu = st.sidebar.radio("Navegação", ["Dashboard", "Novo Lançamento", "Tabela Completa"])

# Lógica do App
if menu == "Novo Lançamento":
    st.header("📝 Adicionar Gasto ou Receita")
    
    with st.form("meu_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        data_input = col1.date_input("Data", date.today())
        valor = col2.number_input("Valor (R$)", min_value=0.01, step=0.01)
        
        descricao = st.text_input("Descrição (Ex: Padaria)")
        
        col3, col4, col5 = st.columns(3)
        categoria = col3.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Habitação", "Receita", "Investimento", "Outros"])
        tipo = col4.selectbox("Tipo", ["Saída", "Entrada"])
        pagamento = col5.selectbox("Pagamento", ["Crédito", "Débito", "Pix", "Dinheiro", "Boleto"])
        
        enviar = st.form_submit_button("💾 Salvar Lançamento")
        
        if enviar:
            # Prepara os dados para salvar
            data_formatada = data_input.strftime("%d/%m/%Y")
            linha = [data_formatada, descricao, categoria, tipo, valor, pagamento]
            
            # Manda para o Google Sheets
            salvar_no_google(linha)
            
            # Atualiza a página
            st.rerun()

elif menu == "Dashboard":
    st.header("📊 Visão Geral")
    df = carregar_dados()
    
    if df.empty:
        st.info("Nenhum dado encontrado. Faça seu primeiro lançamento!")
    else:
        # Tratamento de dados para garantir contas certas
        # Converte o valor para número (caso o Google mande como texto)
        if 'Valor' in df.columns:
            df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        
        # Filtra Entradas e Saídas
        receitas = df[df['Tipo'] == "Entrada"]['Valor'].sum()
        despesas = df[df['Tipo'] == "Saída"]['Valor'].sum()
        saldo = receitas - despesas
        
        # Mostra os Cartões (KPIs)
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Saldo Atual", f"R$ {saldo:,.2f}")
        kpi2.metric("Receitas", f"R$ {receitas:,.2f}", delta="Entradas")
        kpi3.metric("Despesas", f"R$ {despesas:,.2f}", delta="-Saídas", delta_color="inverse")
        
        st.divider()
        
        # Gráficos
        col_graf1, col_graf2 = st.columns(2)
        
        # Gráfico de Rosca
        df_saidas = df[df['Tipo'] == "Saída"]
        if not df_saidas.empty:
            fig_pie = px.pie(df_saidas, values='Valor', names='Categoria', title='Despesas por Categoria', hole=0.5)
            col_graf1.plotly_chart(fig_pie, use_container_width=True)
            
        # Gráfico de Barras
        fig_bar = px.bar(df, x='Categoria', y='Valor', color='Tipo', title='Visão Geral', barmode='group')
        col_graf2.plotly_chart(fig_bar, use_container_width=True)

elif menu == "Tabela Completa":
    st.header("🗃️ Dados Brutos")
    df = carregar_dados()
    st.dataframe(df, use_container_width=True)
