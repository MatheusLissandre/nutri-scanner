import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- Configuração da Página ---
st.set_page_config(page_title="NutriScanner", page_icon="💪")
st.title("💪 NutriScanner AI")
st.write("Descubra se o seu suplemento vale a pena!")

# --- Configuração da API ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Chave API não configurada nos Secrets!")
    st.stop()

# --- Entrada de Dados ---
imagem_file = st.file_uploader("Tire uma foto da tabela nutricional", type=["jpg", "png", "jpeg"])
col1, col2 = st.columns(2)
with col1:
    preco = st.number_input("Preço (R$)", value=150.00, format="%.2f")
with col2:
    peso_input = st.number_input("Peso Total (g)", value=900, step=100)

# --- Botão de Análise ---
if st.button("🔍 Analisar Rótulo"):
    if imagem_file:
        with st.spinner("Lendo o rótulo..."):
            try:
                # 1. Carregar imagem
                image_pil = Image.open(imagem_file)

                # 2. Prompt para a IA
                prompt = """
                Analise este rótulo nutricional. Extraia os dados em JSON puro:
                {
                    "nome_produto": "string",
                    "tamanho_porcao_g": float,
                    "proteina_por_porcao_g": float,
                    "peso_total_pote_g": float,
                    "ingredientes_suspeitos": ["lista de ingredientes ruins se houver"]
                }
                Se não encontrar o peso total na imagem, retorne 0.
                """

                # 3. Chamar IA
                model = genai.GenerativeModel('gemini-flash-latest')
                response = model.generate_content([prompt, image_pil])
                
                # 4. Limpar e ler JSON
                txt_limpo = response.text.replace("```json", "").replace("```", "").strip()
                dados = json.loads(txt_limpo)

                # 5. Cálculos
                # Define o peso: Prioridade para o que o usuário digitou
                peso_final = peso_input if peso_input > 0 else dados.get('peso_total_pote_g', 900)
                if peso_final == 0: peso_final = 900 # Segurança

                scoop = dados.get('tamanho_porcao_g', 30)
                prot_scoop = dados.get('proteina_por_porcao_g', 0)
                
                custo_por_g_prot = 0
                concentracao = 0
                
                if scoop > 0:
                    concentracao = (prot_scoop / scoop) * 100
                    total_prot_pote = (peso_final / scoop) * prot_scoop
                    if total_prot_pote > 0:
                        custo_por_g_prot = preco / total_prot_pote

                # 6. Definir Veredito
                veredito = "PREÇO JUSTO"
                cor_texto = "orange"
                if custo_por_g_prot > 0:
                    if custo_por_g_prot < 0.15: 
                        veredito = "BARATO! VALE A PENA" 
                        cor_texto = "green"
                    elif custo_por_g_prot > 0.22: 
                        veredito = "CARO. TEM OPÇÕES MELHORES" 
                        cor_texto = "red"

                # --- 7. EXIBIÇÃO NA TELA ---
                st.divider()
                st.subheader(dados.get('nome_produto', 'Produto Analisado'))
                
                # Veredito colorido
                st.markdown(f"### Veredito: :{cor_texto}[{veredito}]")

                # As 3 métricas lado a lado (O que faltava!)
                c1, c2, c3 = st.columns(3)
                c1.metric("Proteína p/ Scoop", f"{prot_scoop}g", help=f"Em um scoop de {scoop}g")
                c2.metric("Concentração", f"{concentracao:.0f}%")
                c3.metric("R$ por g/Prot.", f"R$ {custo_por_g_prot:.2f}")

                # Detalhes extras
                st.caption(f"Peso considerado no cálculo: {peso_final}g")

                # Alertas de ingredientes
                if dados.get('ingredientes_suspeitos'):
                    st.warning(f"⚠️ Atenção: {', '.join(dados['ingredientes_suspeitos'])}")
                else:
                    st.success("✅ Ingredientes parecem OK!")

            except Exception as e:
                st.error(f"Erro ao processar: {e}")
    else:
        st.warning("Por favor, envie a foto do rótulo primeiro.")




