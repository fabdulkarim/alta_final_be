from .model import MessageGroups
from blueprints import db

def create_group(g_type, owner_id):
    group = MessageGroups(g_type, owner_id)

    db.session.add(group)
    db.session.commit()

    return group.id