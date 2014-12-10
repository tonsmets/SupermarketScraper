import datetime

"""
Default model for storing discount data
"""
defaultModel = {}
defaultModel['supermarket'] = ''
defaultModel['url'] = ''
defaultModel['image'] = ''
defaultModel['productname'] = ''
defaultModel['duration'] = 'Unknown'
defaultModel['amount'] = 'Unknown'
defaultModel['action_price'] = 'Unknown'
defaultModel['old_price'] = 'Unknown'
defaultModel['description'] = 'Unknown'

# Supermarket specific
defaultModel['bonus'] = 'N/A'

# Additional data
defaultModel['scrape_timestamp'] = str(datetime.datetime.now())