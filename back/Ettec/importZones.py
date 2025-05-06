import ezodf


def ReadOdf(file):
    """
    Read an ODF file and return the first sheet.
    """
    doc = ezodf.opendoc(file)
    sheet = doc.sheets[0]
    rows = list(sheet.rows())
    if rows[8][0].value != 'VILLES' or rows[8][1].value != 'N° DEPT' or rows[8][2].value != 'ZONES' or rows[8][3].value != 'KMS':
        raise Exception('Error: le titre VILLES pas trouvé en A9 ou N° DEPT pas trouvé en B9 ou ZONES pas trouvé en C9 ou KMS pas trouvé en D9')

    tab = []
    for row in rows[9:]:
        if row[0].value is None or row[1].value is None or row[2].value is None or row[3].value is None:
            continue
        tab.append({
            'ville': row[0].value,
            'departement': row[1].value,
            'zone': row[2].value,
            'kms': row[3].value
        })
    return tab