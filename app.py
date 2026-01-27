import streamlit as st
import requests
from PIL import Image

# Título do App
st.set_page_config(page_title="NutriScanner", page_icon="💪")
st.title("💪 NutriScanner AI")
st.write("Descubra se o seu Whey vale a pena!")

# --- 1. Entrada de Dados ---
imagem_file = st.file_uploader("Tire uma foto do rótulo", type=["jpg", "png", "jpeg"])

col1, col2 = st.columns(2)
with col1:
    preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f", value=150.00)
with col2:
    # Nova caixinha de Peso! Já vem com 900g padrão, mas você pode mudar
    peso_input = st.number_input("Peso Total (g)", min_value=0, value=900, step=100)

# --- 2. Botão de Análise ---
if st.button("🔍 Analisar Suplemento"):
    if imagem_file is not None and preco > 0:
        
        st.info("Enviando para a IA...")
        
        try:
            files = {"file": imagem_file.getvalue()}
            # Agora mandamos o peso junto
            data = {"preco": preco, "peso_manual": peso_input}
            
            response = requests.post("http://127.0.0.1:8000/analisar", files=files, data=data)
            
            if response.status_code == 200:
                # ... (Resto do código igual) ...
                resultado = response.json()
                
                # --- 3. Exibição dos Resultados (A Mágica) ---
                st.success("Análise Concluída!")
                
                # Dados Principais
                prod = resultado["analise_nutricional"]
                fin = resultado["financeiro"]
                
                st.header(resultado["produto"])
                
                # Veredito Grande
                cor_texto = "green" if "BARATO" in fin["veredito"] else "red" if "CARO" in fin["veredito"] else "orange"
                st.markdown(f"### Veredito: :{cor_texto}[{fin['veredito']}]")
                
                # Métricas lado a lado
                col1, col2, col3 = st.columns(3)
                col1.metric("Proteína/Scoop", f"{prod['proteina_por_scoop_g']}g")
                col2.metric("Concentração", prod["concentracao"])
                col3.metric("Custo Real/g", f"R$ {fin['custo_real_por_grama']}")
                
                st.divider()
                
                # Detalhes
                st.text(f"Tamanho do Scoop: {prod['scoop_g']}g")
                st.text(f"Peso do Pote (Estimado): {prod['peso_total_considerado']}g")
                
                # Alertas
                if resultado["alerta"]:
                    st.warning(f"⚠️ Atenção aos ingredientes: {', '.join(resultado['alerta'])}")
                else:
                    st.success("✅ Nenhum ingrediente suspeito detectado.")
                    
            else:
                st.error("Erro no servidor. Tente novamente.")
                
        except Exception as e:
            # Isso vai mostrar o erro exato na tela do celular
            st.error(f"ERRO TÉCNICO: {e}")
            if 'response' in locals():
                st.write("Resposta do servidor:", response.text)
            
    else:
        st.warning("Por favor, envie a foto e o preço.")