import requests
import datetime
import json


dstart = datetime.date(year=2018, month=1, day=1)  # inclusive
dend = datetime.date(year=2019, month=1, day=1)    # exclusive
sep = ';'


def fetch_data(auth):
    """For simplicity, get the Authorization string from a browser session"""
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Authorization": auth,
        "Content-type": "application/json",
    })

    transactions_url = "https://platform-rest-prod.ngdata.no/trumf/husstand/transaksjoner"
    details_url = "https://platform-rest-prod.ngdata.no/trumf/husstand/transaksjoner/detaljer/{batchid}"

    r = s.get(transactions_url, params={
        'felter': ','.join(('dato', 'beskrivelse', 'kjedeid', 'partnerid', 'batchid', 'belop',
                            'trumf', 'ekstratrumf', 'trumfvisa', 'literbensin', 'trumftotal')),
        'fra': dstart.isoformat(),
        'til': dend.isoformat(),
        'format': 'crm'})

    transactions = r.json()

    for i, trans in enumerate(transactions):
        r = s.get(details_url.format(batchid=trans['batchid']))
        trans['details'] = r.json()
        print("{} / {} ({} - {})".format(i + 1, len(transactions), trans['dato'], trans['batchid']))

    print("Fetched all records [{}, {}[".format(dstart.isoformat(), dend.isoformat()))

    return transactions


def make_csv_table(transactions):
    """Conveniently format the data for importing into spreadsheet and further analythics"""
    for t in transactions:
        t['dato'] = datetime.datetime.strptime(t['dato'], "%Y-%m-%d").date()

    transactions = sorted(transactions, key=lambda x: (x['dato'], x['batchid']))

    yield sep.join(['id', 'dato', 'butikk', 'totalbelop', 'totaltrumf', 'ean',
                    'vare', 'antall', 'belop'])
    for t in transactions:
        t['belop'] = str(t['belop']).replace('.', ',')
        t['trumftotal'] = str(t['trumftotal']).replace('.', ',')
        if 'varelinjer' not in t['details']:
            t['details']['varelinjer'] = [
                    {'vareTekst': 'Ukjent',
                     'ean': '*',
                     'antall': '1',
                     'belop': t['belop']}]
        for v in t['details']['varelinjer']:
            yield sep.join([
                '"=""' + t['batchid'] + '"""',
                t['dato'].isoformat(),
                t['beskrivelse'],
                t['belop'],
                t['trumftotal'],
                '"=""' + v['ean'] + '"""',
                v['vareTekst'],
                v['antall'].replace('.', ','),
                v['belop'].replace('.', ',')
                ])


# Uncomment this to fetch data
## transactions = fetch_data()
## print("storing into data.json")
## with open('data.json', 'w') as f:
##     json.dump(transactions, f)

# Uncomment this to reformat data for spreadsheet use
## with open('data.json') as f:
##     transactions = json.load(f)
## with open('data.csv', 'w') as f:
##     for line in make_csv_table(transactions):
##         f.write(line + '\n')
