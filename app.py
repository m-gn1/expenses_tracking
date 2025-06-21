import streamlit as st
st.title("Coucou mon chéri !!")
st.markdown(
    """ 

 regarde ce que je peux faire avec Streamlit !
    """
)

if st.button("Send balloons!"):
    st.balloons()