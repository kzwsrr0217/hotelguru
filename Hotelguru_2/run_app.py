from flask import Flask
from config import Config
from app import create_app

if __name__ == "__main__":
    create_app(config_class=Config).run("localhost", 8888)

"""
from flask import Flask
from config import Config
from app import create_app
import os # <<< os import hozzáadása

if __name__=="__main__":
    # Ideiglenesen hozzuk létre az appot csak az útvonalak kiírásához
    temp_app = create_app(config_class=Config)

    # Útvonalak kiírása a konzolra
    print('--- Regisztrált Útvonalak ---')
    output = []
    # Iterálás a Flask url_map szabályain
    for rule in temp_app.url_map.iter_rules():
        # Argumentumok és metódusok gyűjtése olvasható formában
        options = {arg: f"[{arg}]" for arg in rule.arguments}
        methods = ','.join(rule.methods)
        # Sor formázása: endpoint név, engedélyezett metódusok, URL szabály
        line = f"{rule.endpoint:50s} {methods:20s} {rule.rule}"
        output.append(line)

    # Kiírás rendezve az endpoint neve szerint
    for line in sorted(output):
        print(line)
    # Elválasztó sor a jobb olvashatóságért
    print('--- Regisztrált Útvonalak Vége ---' + os.linesep) # os.linesep a platformfüggetlen sortörésért

    # Az alkalmazás tényleges futtatása
    # Ha a fenti print után akarod futtatni, akkor újra létre kell hozni,
    # vagy használhatod a temp_app-ot is, de a create_app() biztosabb.
    create_app(config_class=Config).run('localhost', 8888)
"""
