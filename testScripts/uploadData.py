import airtable

AIRTABLE_API_KEY = 'keyiBU3kbqq2MMpOC'
AIRTABLE_BASE_ID = 'appLDM3F8B89UY71p'
AIRTABLE_TABLE_NAME = 'table 1'


airtable_client = airtable.Airtable(
    AIRTABLE_BASE_ID, 'Signups', AIRTABLE_API_KEY)

airtable_client.insert({
    'Phone Number': '+19164170513'
})
