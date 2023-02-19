from pandas.io.formats.style import Styler

def transactions_styler(df) -> Styler:    
    def buysell_colormap(val):
        color = 'red' if val=='S' else 'green'
        return f"color: {color};"
    
    # Apply formatting and background color
    formatted_df = df.style.applymap(
        buysell_colormap, subset='buysell'
        ).format(
        {
            'price': '{:.2f}',
            'total': '{:.2f}',
            'fxRate': '{:.4f}',
        })
    return formatted_df