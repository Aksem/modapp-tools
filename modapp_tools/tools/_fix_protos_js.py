import re

import modapp_tools.env as env


def fix_js_protos():
    endpoints_by_services = {}

    for protos in env.PROTOS_PATH.iterdir():
        if protos.is_dir():
            continue

        protos_content = ""
        with open(protos, "r") as protos_file:
            protos_content = protos_file.read()

        m = re.search(r"service (?P<service>\w*) {(?P<endpoints>(.|\n)*)}", protos_content)
        if m is None:
            continue
        service = m.groupdict()["service"]
        endpoints_raw = m.groupdict()["endpoints"]
        endpoints_by_services[service] = []

        for endpoint_raw in endpoints_raw.strip("\n").split("\n"):
            m2 = re.search(r"rpc (?P<endpoint>\w*)", endpoint_raw)
            if m2:
                endpoints_by_services[service].append(m2.groupdict()["endpoint"])

    protos_js_content = ""
    protos_js_file = env.CLIENT_SERVICES_PATH / 'protos.js'
    with open(protos_js_file, "r") as js_file:
        protos_js_content = js_file.read()

    for service in endpoints_by_services:
        service_prefix = "/" + service + "/"
        for endpoint in endpoints_by_services[service]:
            protos_js_content = protos_js_content.replace(
                f'{{ value: "{endpoint}" }}', f'{{ value: "{service_prefix + endpoint}" }}'
            )

    with open(protos_js_file, "w") as js_file:
        js_file.write(protos_js_content)
