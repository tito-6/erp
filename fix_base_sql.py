
import codecs
filepath = r"c:\D\crm\tcrm-src\tcrm\addons\base\data\base_data.sql"
try:
    with open(filepath, 'rb') as f:
        content = f.read()
    if content.startswith(codecs.BOM_UTF8):
        print(f"BOM found in {filepath}. Removing...")
        with open(filepath, 'wb') as f:
            f.write(content[3:])
        print("BOM removed.")
    else:
        print(f"No BOM found in {filepath}.")
except Exception as e:
    print(f"Error: {e}")
