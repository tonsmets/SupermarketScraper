import datetime

"""
Default model for storing discount data
"""
defaultModel = {}
defaultModel['supermarket'] = ''
defaultModel['url'] = ''
defaultModel['image'] = ''
defaultModel['productname'] = ''
defaultModel['duration'] = ''
defaultModel['amount'] = ''
defaultModel['action_price'] = ''
defaultModel['old_price'] = ''
defaultModel['description'] = ''

# Supermarket specific
defaultModel['bonus'] = 'N/A'

# Additional data
defaultModel['scrape_timestamp'] = str(datetime.datetime.now())

"""
Supermarket meta model for storing additional data
"""
metaModel = {}
metaModel['supermarket'] = ''
metaModel['superid'] = ''
metaModel['name'] = ''
metaModel['address'] = ''
metaModel['lat'] = ''
metaModel['lon'] = ''
metaModel['phone'] = ''
metaModel['opening'] = []
metaModel['services'] = []