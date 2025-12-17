import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.title("🧪 Teste de Conexão com Google Sheets")

st.write("Tentando conectar...")

try:
    # 1. Tenta pegar a senha
    if "gcp_service_account" not in st.secrets:
        st.error("ERRO: Não encontrei a 'gcp_service_account' nos Secrets!")
        st.stop()
    
    st.write("✅ Achei a senha nos Secrets.")

    # 2. Tenta autenticar
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    st.write("✅ Autenticação com Google feita.")

    # 3. Tenta achar a planilha
    NOME_PLANILHA = "Controle Financeiro"
    sheet = client.open(NOME_PLANILHA).sheet1
    
    st.success(f"✅ SUCESSO! Conectei na planilha '{NOME_PLANILHA}'!")
    st.write("Se você está vendo isso, a conexão funciona. Pode voltar o código original.")

except gspread.exceptions.SpreadsheetNotFound:
    st.error(f"❌ ERRO CRÍTICO: Não encontrei a planilha com o nome '{NOME_PLANILHA}'.")
    st.warning("Dica: Verifique se o nome do arquivo no Google Sheets é EXATAMENTE 'Controle Financeiro' (sem espaços extras) e se você compartilhou com o email do robô.")

except Exception as e:
    st.error(f"❌ ERRO DESCONHECIDO: {e}")
