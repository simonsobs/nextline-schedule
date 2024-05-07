from black import Mode, format_str
from hypothesis import strategies as st


@st.composite
def st_python_scripts(draw: st.DrawFn) -> str:
    types = ('print', 'sleep')
    lines = ['import time']
    n_lines = draw(st.integers(min_value=1, max_value=10))
    for _ in range(n_lines):
        type_ = draw(st.sampled_from(types))
        match type_:
            case 'print':
                text = draw(st.text(max_size=120))
                lines.append(f'print({text!r})')
            case 'sleep':
                secs = draw(st.integers(min_value=1, max_value=100)) / 10_000
                lines.append(f'time.sleep({secs:.5f})')

    code = '\n'.join(lines)
    return format_str(code, mode=Mode())
