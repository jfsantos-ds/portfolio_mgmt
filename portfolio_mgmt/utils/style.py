from pandas.io.formats.style import Styler

def transactions_styler(style: Styler) -> Styler:
    style = style.format(
        formatter={
        ('price', 'total', 'autoFxFeeInBaseCurrency', 'feeInBaseCurrency', 'totalPlusAllFeesInBaseCurrency'): "{:.2f}",  # precision 2 floats
        ('fxRate'): "{:.2f}",  # precision 4 floats
        }
        )
    return style