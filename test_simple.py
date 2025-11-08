import streamlit as st

st.set_page_config(page_title="Teste Simples")

st.title("✅ Teste Funcionando!")
st.write("Se você vê isso, o Streamlit está OK")

if st.button("Clique aqui"):
    st.success("Botão funcionou!")
