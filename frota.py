import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
from datetime import datetime
import pandas as pd
import pytz # <--- Biblioteca de Fuso Horário

# --- Configuração da Página ---
st.set_page_config(page_title="Gestão de Frotas", page_icon="🚌")
st.title("🚌 Controle de Abastecimento")
st.write("Registre as 4 fotos obrigatórias do abastecimento.")

# --- Configuração da API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Configure a chave API nos Secrets!")
    st.stop()

# --- Entrada de Fotos ---
tab1, tab2, tab3, tab4 = st.tabs(["📸 1. Prefixo", "📸 2. Odômetro", "📸 3. Litros", "📸 4. Nº Bomba"])

with tab1:
    foto_prefixo = st.file_uploader("Foto do Prefixo (Lateral/Vidro)", type=["jpg", "png", "jpeg"], key="pref")
with tab2:
    foto_odo = st.file_uploader("Foto do Odômetro (Painel)", type=["jpg", "png", "jpeg"], key="odo")
with tab3:
    foto_litros = st.file_uploader("Foto do Visor (Apenas Litros)", type=["jpg", "png", "jpeg"], key="lit")
with tab4:
    foto_num_bomba = st.file_uploader("Foto do Número da Bomba (Adesivo/ID)", type=["jpg", "png", "jpeg"], key="num_bomb")

# --- Botão de Processamento ---
if st.button("🚀 Processar Registro"):
    if foto_prefixo and foto_odo and foto_litros and foto_num_bomba:
        with st.spinner("A IA está analisando as 4 imagens..."):
            try:
                # 1. Carregar as imagens
                img1 = Image.open(foto_prefixo)
                img2 = Image.open(foto_odo)
                img3 = Image.open(foto_litros)
                img4 = Image.open(foto_num_bomba)

                # 2. Prompt Turbo
                prompt = """
                Você é um assistente de frota de ônibus. Analise estas 4 imagens na ordem exata:
                
                1. IMAGEM 1 (ÔNIBUS): Extraia o PREFIXO COMPLETO. Se houver hífen, inclua.
                2. IMAGEM 2 (PAINEL): Extraia o ODÔMETRO (Km total).
                3. IMAGEM 3 (VISOR): Extraia APENAS A LITRAGEM abastecida.
                4. IMAGEM 4 (IDENTIFICAÇÃO): Extraia o NÚMERO DA BOMBA.

                Retorne APENAS um JSON neste formato:
                {
                    "prefixo": "string",
                    "odometro_km": int,
                    "litros": float,
                    "numero_bomba": "string"
                }
                """

                # 3. Enviar para o Gemini
                model = genai.GenerativeModel('gemini-flash-latest')
                response = model.generate_content([prompt, img1, img2, img3, img4])
                
                # 4. Limpeza
                txt = response.text.replace("```json", "").replace("```", "").strip()
                dados = json.loads(txt)

                # 5. DATA E HORA BRASIL (CORREÇÃO AQUI) 🕒
                fuso_brasil = pytz.timezone('America/Sao_Paulo')
                agora = datetime.now(fuso_brasil)
                
                dados["data"] = agora.strftime("%d/%m/%Y")
                dados["hora"] = agora.strftime("%H:%M:%S")

                # --- EXIBIÇÃO ---
                st.success("✅ Leitura Realizada!")
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Prefixo", dados["prefixo"])
                c2.metric("Odômetro", f"{dados['odometro_km']} km")
                c3.metric("Litros", f"{dados['litros']} L")
                c4.metric("Bomba", dados["numero_bomba"])

                st.divider()
                st.info(f"📅 Registro (Horário de Brasília): {dados['data']} às {dados['hora']}")

                # --- BANCO DE DADOS (Simulação CSV) ---
                df_novo = pd.DataFrame([dados])
                st.write("### Conferência:")
                st.dataframe(df_novo)
                
                csv = df_novo.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Baixar Registro (CSV)",
                    csv,
                    f"abastecimento_{dados['prefixo']}.csv",
                    "text/csv"
                )

            except Exception as e:
                st.error(f"Erro na leitura: {e}")
    else:
        st.warning("⚠️ Faltam fotos! Por favor, envie as 4 imagens.")
