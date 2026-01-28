import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
from datetime import datetime
import pandas as pd

# --- Configuração da Página ---
st.set_page_config(page_title="Gestão de Frotas", page_icon="🚌")
st.title("🚌 Controle de Abastecimento")
st.write("Tire as fotos e deixe a IA preencher a planilha.")

# --- Configuração da API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Configure a chave API nos Secrets!")
    st.stop()

# --- Entrada de Fotos (Layout em Abas para organizar) ---
tab1, tab2, tab3 = st.tabs(["📸 1. Prefixo", "📸 2. Odômetro", "📸 3. Bomba"])

with tab1:
    foto_prefixo = st.file_uploader("Foto do Ônibus (Prefixo)", type=["jpg", "png", "jpeg"], key="pref")
with tab2:
    foto_odo = st.file_uploader("Foto do Painel (Odômetro)", type=["jpg", "png", "jpeg"], key="odo")
with tab3:
    foto_bomba = st.file_uploader("Foto da Bomba (Litros/Bomba)", type=["jpg", "png", "jpeg"], key="bomb")

# --- Botão de Processamento ---
if st.button("🚀 Processar Registro"):
    if foto_prefixo and foto_odo and foto_bomba:
        with st.spinner("Analisando as 3 imagens..."):
            try:
                # 1. Carregar as imagens
                img1 = Image.open(foto_prefixo)
                img2 = Image.open(foto_odo)
                img3 = Image.open(foto_bomba)

                # 2. Prompt Inteligente para as 3 imagens
                prompt = """
                Você é um assistente de frota de ônibus. Analise estas 3 imagens em ordem:
                1. A primeira imagem é o exterior do ônibus. Extraia o NÚMERO DO PREFIXO (ex: 1040, 2030).
                2. A segunda imagem é o painel. Extraia o ODÔMETRO (Km total). Ignore trip ou parciais.
                3. A terceira imagem é a bomba de combustível. Extraia a LITRAGEM abastecida e o NÚMERO DA BOMBA ou BICO.

                Retorne APENAS um JSON neste formato:
                {
                    "prefixo": "string",
                    "odometro_km": int,
                    "litros": float,
                    "numero_bomba": "string"
                }
                """

                # 3. Enviar tudo junto para o Gemini
                model = genai.GenerativeModel('gemini-flash-latest')
                response = model.generate_content([prompt, img1, img2, img3])
                
                # 4. Limpeza
                txt = response.text.replace("```json", "").replace("```", "").strip()
                dados = json.loads(txt)

                # 5. Adicionar Data e Hora Automáticas
                agora = datetime.now()
                dados["data"] = agora.strftime("%d/%m/%Y")
                dados["hora"] = agora.strftime("%H:%M:%S")

                # --- EXIBIÇÃO ---
                st.success("✅ Leitura Realizada!")
                
                # Cartões de Resumo
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Prefixo", dados["prefixo"])
                c2.metric("Odômetro", f"{dados['odometro_km']} km")
                c3.metric("Litros", f"{dados['litros']} L")
                c4.metric("Bomba", dados["numero_bomba"])

                st.divider()
                st.info(f"📅 Registro Automático: {dados['data']} às {dados['hora']}")

                # --- BANCO DE DADOS (Simulação CSV) ---
                # Aqui criamos uma linha de tabela para você baixar
                df_novo = pd.DataFrame([dados])
                st.write("### Conferência dos Dados:")
                st.dataframe(df_novo)
                
                # Botão para salvar localmente (MVP)
                csv = df_novo.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Baixar Registro (CSV)",
                    csv,
                    f"registro_{dados['prefixo']}.csv",
                    "text/csv"
                )

            except Exception as e:
                st.error(f"Erro na leitura: {e}. Tente tirar fotos mais claras.")
    else:
        st.warning("⚠️ Por favor, envie as 3 fotos para processar.")
