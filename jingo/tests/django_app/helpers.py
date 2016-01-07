from jingo import register


@register.filter
def test_filter(anything):
    return 'Success!'
