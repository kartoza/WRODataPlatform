from ckan import model
from ckan.logic import get_action
from ckan.config.environment import load_environment
from paste.deploy import appconfig

CONFIG = "/home/appuser/app/docker/ckan-dev-settings.ini"

conf = appconfig(f"config:{CONFIG}")
load_environment(conf.global_conf, conf.local_conf)

context = {
    "model": model,
    "session": model.Session,
    "ignore_auth": True,
}

pkg = get_action("package_show")(
    context,
    {"id": "atlas-of-agrohydrology-2008-zip"}
)

print(f"Found {len(pkg['resources'])} resources")

for r in pkg["resources"]:
    print(f"Deleting resource {r['id']} | {r.get('name')}")
    get_action("resource_delete")(context, {"id": r["id"]})

model.Session.commit()
print("✅ All resources deleted")
