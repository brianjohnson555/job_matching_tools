# Example proxy setup from IPRoyal
# Import the proxies object into main job_scrape file for use with src functions.
proxy = 'geo.iproyal.com:XXXXX'
proxy_auth = 'BLANK'
proxies = {
'http': f'socks5://{proxy_auth}@{proxy}',
'https': f'socks5://{proxy_auth}@{proxy}'
}