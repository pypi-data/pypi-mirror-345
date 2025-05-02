import streamlit as st
from streamlit_extras.let_it_rain import rain

def example():
    rain(
        # emoji="🦉",
        emoji="🦩",
        font_size=48,
        falling_speed=5,
        animation_length=1,
    )

example()
