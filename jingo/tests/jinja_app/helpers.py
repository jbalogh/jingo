from __future__ import absolute_import, unicode_literals

from jingo import register


@register.filter
def test_filter(anything):
    return 'Success!'
