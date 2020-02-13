from .model import MessageReceipts, Messages, MessageGroups, UserGroups

from blueprints import db

def send_to_recipient(r_uid,r_gid,m_id):
    msg_receipt = MessageReceipts(r_uid,r_gid,m_id)
    db.session.add(msg_receipt)
    db.session.commit()

def send_message(author_uid, message_content, target_gid):
    message = Messages(author_uid,message_content)

    print(target_gid)
    
    db.session.add(message)
    db.session.commit()

    qry = UserGroups.query.filter_by(group_id=int(target_gid))
    print(qry)
    # uid_row = []
    for que in qry:
        print(que.user_id, target_gid)
        # uid_row.append(que.user_id)
        send_to_recipient(int(que.user_id),int(target_gid),message.id)



# def create_message():
