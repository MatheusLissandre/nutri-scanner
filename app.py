import streamlit as st
import google.generativeai as genai # <--- Biblioteca Estável
from PIL import Image
import json

st.set_page_config(page_title="NutriScanner", page_icon="💪")
st.title("💪 NutriScanner AI")

# --- Configuração da API (Estável) ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Chave API faltando nos Secrets!")
    st.stop()

# --- Entrada de Dados ---
imagem_file = st.file_uploader("Foto do Rótulo", type=["jpg", "png", "jpeg"])
col1, col2 = st.columns(2)
with col1:
    preco = st.number_input("Preço (R$)", value=150.00, format="%.2f")
with col2:
    peso_input = st.number_input("Peso Total (g)", value=900, step=100)

if st.button("🔍 Analisar"):
    if imagem_file:
        with st.spinner("Analisando..."):
            try:
                # Carrega imagem
                image_pil = Image.open(imagem_file)

                # Prompt
                prompt = """
                Extraia os dados deste rótulo em JSON:
                {
                    "nome_produto": "string",
                    "tamanho_porcao_g": float,
                    "proteina_por_porcao_g": float,
                    "peso_total_pote_g": float,
                    "ingredientes_suspeitos": ["lista"]
                }
                Se não achar o peso, use 0.
                """

                # Chama o Modelo (Sintaxe da Versão Estável)
                model = genai.GenerativeModel('gemini-flash-latest')
                response = model.generate_content([prompt, image_pil])
                
                # Limpa JSON
                txt = response.text.replace("```json", "").replace("```", "")
                dados = json.loads(txt)

                # Lógica (igual ao anterior)
                peso = peso_input if peso_input > 0 else dados.get('peso_total_pote_g', 900)
                if peso == 0: peso = 900
                scoop = dados.get('tamanho_porcao_g', 30)
                prot = dados.get('proteina_por_porcao_g', 0)
                
                custo = 0
                if scoop > 0:
                    total_prot = (peso / scoop) * prot
                    if total_prot > 0: custo = preco / total_prot

                # Exibe
                st.success("Pronto!")
                st.subheader(dados.get('nome_produto', 'Produto'))
                
                veredito = "PREÇO JUSTO"
                cor = "orange"
                if custo > 0:
                    if custo < 0.15: 
                        veredito = "BARATO!" 
                        cor = "green"
                    elif custo > 0.22: 
                        veredito = "CARO" 
                        cor = "red"

                st.markdown(f"### Veredito: :{cor}[{veredito}]")
                st.metric("R$/g Proteína", f"R$ {custo:.3f}")
                
                if dados.get('ingredientes_suspeitos'):
                    st.warning(f"⚠️ {dados['ingredientes_suspeitos']}")

            except Exception as e:
                st.error(f"Erro: {e}")


